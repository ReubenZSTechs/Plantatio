import json
from src.pipeline.rag.connect_to_neo4j import Neo4jHandler
from src.models.LLM.v2_LLM import LLMManager
from src.utils.CONFIG import CONFIG
from src.utils.prompt_templates_v2 import (
    get_entities_to_retrieve_prompt,
    get_relationship_extraction_prompt,
)
import re
import time
import traceback
import os
from datetime import datetime
from difflib import SequenceMatcher


class BibleKGCreator:
    def __init__(self):
        self.llm = LLMManager()

    # ─────────────────────────────────────────────────────────────
    # BIBLE LOADING
    # ─────────────────────────────────────────────────────────────

    def get_bible(self, path="data/bible/en_bbe_flat.json"):
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def get_bible_per_chapter(self):
        bible = self.get_bible()
        bible_dict = {}
        for verse in bible:
            key = f"{verse['book']}_{verse['chapter']}"
            if key not in bible_dict:
                bible_dict[key] = ""
            bible_dict[key] += f"{verse['verse']}. {verse['text']}\n"
        return bible_dict

    # ─────────────────────────────────────────────────────────────
    # NODE CREATION
    # ─────────────────────────────────────────────────────────────

    def create_verse_node(self, handler, book, chapter, verse_num, text):
        query = """
        MERGE (v:Verse {book: $book, chapter: $chapter, verse: $verse})
        SET v.text = $text
        """
        handler.execute_query(query, {
            "book": book, "chapter": chapter,
            "verse": verse_num, "text": text
        })

    def sanitize_entity(self, entity):
        """
        Validate and clean entity dict from LLM.
        Also cleans the optional 'properties' field.
        Returns None if entity is malformed.
        """
        if (
            not isinstance(entity, dict)
            or "type" not in entity
            or "name" not in entity
        ):
            return None

        entity_name = entity["name"].strip()
        if not entity_name:
            return None

        entity_type = re.sub(r'[^a-zA-Z0-9_]', '_', entity["type"])

        raw_props  = entity.get("properties", {})
        clean_props = self._sanitize_properties(raw_props)

        return {
            "type":       entity_type,
            "name":       entity_name,
            "properties": clean_props
        }

    def _sanitize_properties(self, props: dict) -> dict:
        """
        Clean a properties dict for safe Neo4j storage.
        Accepts: str, int, float, bool, list of primitives.
        Rejects: nested objects.
        """
        if not isinstance(props, dict):
            return {}

        clean = {}
        for k, v in props.items():
            key = re.sub(r'[^a-zA-Z0-9_]', '_', str(k))
            if isinstance(v, (str, int, float, bool)):
                clean[key] = v
            elif isinstance(v, list):
                clean[key] = [i for i in v if isinstance(i, (str, int, float, bool))]
        return clean

    def create_entity_node(self, handler, entity_type, entity_name, properties: dict = None):
        """
        MERGE entity node and SET immutable properties if provided.
        Uses += so existing properties are never overwritten.
        """
        if properties:
            query = f"""
            MERGE (e:{entity_type} {{name: $name}})
            SET e += $properties
            """
            handler.execute_query(query, {
                "name":       entity_name,
                "properties": properties
            })
        else:
            query = f"""
            MERGE (e:{entity_type} {{name: $name}})
            """
            handler.execute_query(query, {"name": entity_name})

    def create_mentions_relationship(
        self, handler, entity_type, entity_name, book, chapter, verse_num
    ):
        query = f"""
        MATCH (e:{entity_type} {{name: $name}})
        MATCH (v:Verse {{book: $book, chapter: $chapter, verse: $verse}})
        MERGE (v)-[:MENTIONS]->(e)
        """
        handler.execute_query(query, {
            "name": entity_name, "book": book,
            "chapter": chapter, "verse": verse_num
        })

    # ─────────────────────────────────────────────────────────────
    # ENTITY EXTRACTION
    # ─────────────────────────────────────────────────────────────

    def extract_entities_from_verse(self, text: str, context_verses: list = None):
        """
        Extract entities from the current verse.

        Args:
            text           : The verse text to process.
            context_verses : List of previous verse texts (up to 3) for pronoun resolution.
        """
        prompt   = get_entities_to_retrieve_prompt(text, context_verses=context_verses)
        entities = self.llm.call_kg_worker(prompt=prompt)
        return entities if isinstance(entities, list) else []

    # ─────────────────────────────────────────────────────────────
    # RELATIONSHIP CREATION
    # ─────────────────────────────────────────────────────────────

    def _is_type_b(self, target: str, valid_names: set) -> bool:
        """
        Determine if a relationship is Type B (attribute/value string).
        Type B: target is NOT an entity node name.
        Type A: target IS an entity node name.
        """
        return target not in valid_names

    def _create_type_a_relationship(
        self, handler, source, relation_type, target, rel_properties: dict
    ):
        """
        Create a direct entity-to-entity relationship (Type A).
        Optionally sets numeric properties on the relationship.
        """
        if rel_properties:
            query = f"""
            MATCH (a {{name: $source}})
            MATCH (b {{name: $target}})
            MERGE (a)-[r:{relation_type}]->(b)
            SET r += $properties
            """
            handler.execute_query(query, {
                "source":     source,
                "target":     target,
                "properties": rel_properties
            })
        else:
            query = f"""
            MATCH (a {{name: $source}})
            MATCH (b {{name: $target}})
            MERGE (a)-[r:{relation_type}]->(b)
            """
            handler.execute_query(query, {
                "source": source,
                "target": target
            })

    def _create_type_b_relationship(
        self, handler, source, relation_type, target_value: str
    ):
        """
        Create an attribute relationship from entity to a value string node (Type B).
        e.g. earth -[HAS_STATE]-> (:StateValue {value: "formless"})

        AttributeValue nodes are shared across the graph — same value reused.
        
        Comprehensive label mapping for all biblical attribute types.
        """
        # Comprehensive label map for all Type B relationship types that appear in the Bible
        label_map = {
            # ── Basic States & Conditions ──
            "HAS_STATE":           "StateValue",
            "HAS_STATUS":          "StatusValue",
            "HAS_CONDITION":       "ConditionValue",
            "HAS_QUALITY":         "QualityValue",
            
            # ── Roles, Titles & Names ──
            "HAS_ROLE":            "RoleValue",
            "HAS_TITLE":           "TitleValue",
            "HAS_NAME":            "NameValue",
            "HAS_EPITHET":         "EpithetValue",
            "HAS_OFFICE":          "OfficeValue",
            "HAS_POSITION":        "PositionValue",
            
            # ── Location & Space ──
            "HAS_LOCATION":        "LocationValue",
            "HAS_DWELLING":        "DwellingValue",
            "HAS_DOMAIN":          "DomainValue",
            "HAS_KINGDOM":         "KingdomValue",
            "HAS_TERRITORY":       "TerritoryValue",
            
            # ── Family & Relationships ──
            "HAS_CHILDREN":        "FamilyValue",
            "HAS_DESCENDANTS":     "FamilyValue",
            "HAS_KINSHIP":         "FamilyValue",
            "HAS_LINEAGE":         "FamilyValue",
            
            # ── Physical Attributes ──
            "HAS_APPEARANCE":      "AppearanceValue",
            "HAS_FORM":            "FormValue",
            "HAS_BEAUTY":          "BeautyValue",
            "HAS_STRENGTH":        "StrengthValue",
            "HAS_AGE":             "AgeValue",
            "HAS_COLOR":           "ColorValue",
            
            # ── Health & Life ──
            "HAS_HEALTH":          "HealthValue",
            "HAS_SICKNESS":        "SicknessValue",
            "HAS_AFFLICTION":      "AfflictionValue",
            "HAS_DISEASE":         "DiseaseValue",
            "HAS_VIGOR":           "VigorValue",
            "HAS_WEAKNESS":        "WeaknessValue",
            
            # ── Spiritual Attributes ──
            "HAS_FAITH":           "SpiritualValue",
            "HAS_GRACE":           "SpiritualValue",
            "HAS_BLESSING":        "SpiritualValue",
            "HAS_CURSE":           "SpiritualValue",
            "HAS_HOLINESS":        "SpiritualValue",
            "HAS_RIGHTEOUSNESS":   "SpiritualValue",
            "HAS_SIN":             "SpiritualValue",
            "HAS_REDEMPTION":      "SpiritualValue",
            "HAS_SALVATION":       "SpiritualValue",
            "HAS_COVENANT":        "CovenantValue",
            "HAS_PROMISE":         "PromiseValue",
            
            # ── Emotions & Dispositions ──
            "HAS_EMOTION":         "EmotionValue",
            "HAS_JOY":             "EmotionValue",
            "HAS_SORROW":          "EmotionValue",
            "HAS_FEAR":            "EmotionValue",
            "HAS_LOVE":            "EmotionValue",
            "HAS_HATRED":          "EmotionValue",
            "HAS_ANGER":           "EmotionValue",
            "HAS_WRATH":           "EmotionValue",
            "HAS_MERCY":           "EmotionValue",
            "HAS_COMPASSION":      "EmotionValue",
            "HAS_PRIDE":           "EmotionValue",
            "HAS_HUMILITY":        "EmotionValue",
            "HAS_CONFIDENCE":      "EmotionValue",
            "HAS_DOUBT":           "EmotionValue",
            "HAS_HOPE":            "EmotionValue",
            "HAS_DESPAIR":         "EmotionValue",
            "HAS_PEACE":           "EmotionValue",
            "HAS_TURMOIL":         "EmotionValue",
            
            # ── Moral & Ethical ──
            "HAS_VIRTUE":          "VirtueValue",
            "HAS_VICE":            "ViceValue",
            "HAS_JUSTICE":         "JusticeValue",
            "HAS_INJUSTICE":       "JusticeValue",
            "HAS_OBEDIENCE":       "MoralValue",
            "HAS_DISOBEDIENCE":    "MoralValue",
            "HAS_LOYALTY":         "MoralValue",
            "HAS_BETRAYAL":        "MoralValue",
            "HAS_TRUTH":           "TruthValue",
            "HAS_FALSEHOOD":       "TruthValue",
            "HAS_HONESTY":         "TruthValue",
            "HAS_DECEIT":          "TruthValue",
            
            # ── Possession & Wealth ──
            "HAS_WEALTH":          "WealthValue",
            "HAS_RICHES":          "WealthValue",
            "HAS_TREASURE":        "WealthValue",
            "HAS_PROPERTY":        "PropertyValue",
            "HAS_INHERITANCE":     "PropertyValue",
            "HAS_POSSESSION":      "PropertyValue",
            "HAS_ABUNDANCE":       "AbundanceValue",
            "HAS_SCARCITY":        "AbundanceValue",
            "HAS_FAMINE":          "AbundanceValue",
            "HAS_PLENTY":          "AbundanceValue",
            
            # ── Power & Authority ──
            "HAS_POWER":           "PowerValue",
            "HAS_AUTHORITY":       "AuthorityValue",
            "HAS_DOMINION":        "DominionValue",
            "HAS_THRONE":          "ThroneValue",
            "HAS_CROWN":           "CrownValue",
            "HAS_SCEPTER":         "ScepterValue",
            
            # ── Conflict & Victory ──
            "HAS_VICTORY":         "VictoryValue",
            "HAS_DEFEAT":          "DefeatValue",
            "HAS_TRIUMPH":         "VictoryValue",
            "HAS_FAILURE":         "DefeatValue",
            "HAS_CAPTIVITY":       "CaptivityValue",
            "HAS_FREEDOM":         "FreedomValue",
            "HAS_EXILE":           "ExileValue",
            "HAS_RETURN":          "ReturnValue",
            
            # ── Actions & Events ──
            "HAS_ACTION":          "ActionValue",
            "HAS_SUFFERING":       "SufferingValue",
            "HAS_TRIAL":           "TrialValue",
            "HAS_TEMPTATION":      "TemptationValue",
            "HAS_TESTING":         "TestingValue",
            "HAS_TRIBULATION":     "TribulationValue",
            "HAS_PERSECUTION":     "PersecutionValue",
            "HAS_PUNISHMENT":      "PunishmentValue",
            "HAS_REWARD":          "RewardValue",
            "HAS_JUDGMENT":        "JudgmentValue",
            
            # ── Divine Manifestation ──
            "HAS_GLORY":           "GloryValue",
            "HAS_HONOR":           "HonorValue",
            "HAS_SHAME":           "ShameValue",
            "HAS_MAJESTY":         "MajestyValue",
            "HAS_SPLENDOR":        "SplendorValue",
            "HAS_PRESENCE":        "PresenceValue",
            "HAS_ABSENCE":         "AbsenceValue",
            
            # ── Knowledge & Wisdom ──
            "HAS_KNOWLEDGE":       "KnowledgeValue",
            "HAS_WISDOM":          "WisdomValue",
            "HAS_UNDERSTANDING":   "UnderstandingValue",
            "HAS_IGNORANCE":       "IgnoranceValue",
            "HAS_FOLLY":           "FollyValue",
            "HAS_VISION":          "VisionValue",
            "HAS_PROPHECY":        "ProphecyValue",
            "HAS_REVELATION":      "RevelationValue",
            "HAS_MYSTERY":         "MysteryValue",
            
            # ── Worship & Devotion ──
            "HAS_WORSHIP":         "WorshipValue",
            "HAS_PRAISE":          "PraiseValue",
            "HAS_PRAYER":          "PrayerValue",
            "HAS_SONG":            "SongValue",
            "HAS_OFFERING":        "OfferingValue",
            "HAS_SACRIFICE":       "SacrificeValue",
            "HAS_RITUAL":          "RitualValue",
            "HAS_CEREMONY":        "CeremonyValue",
            "HAS_CELEBRATION":     "CelebrationValue",
            "HAS_MOURNING":        "MourningValue",
            "HAS_FASTING":         "FastingValue",
            "HAS_FEAST":           "FeastValue",
            
            # ── Time & Duration ──
            "HAS_AGE_OF":          "AgeValue",
            "HAS_GENERATION":      "GenerationValue",
            "HAS_ERA":             "EraValue",
            "HAS_EPOCH":           "EpochValue",
            "HAS_SEASON":          "SeasonValue",
            
            # ── Transformation & Change ──
            "HAS_TRANSFORMATION":  "TransformationValue",
            "HAS_RENEWAL":         "RenewalValue",
            "HAS_RESTORATION":     "RestorationValue",
            "HAS_REBIRTH":         "RebirthValue",
            "HAS_RESURRECTION":    "ResurrectionValue",
            "HAS_ASCENSION":       "AscensionValue",
            
            # ── Miscellaneous ──
            "HAS_SIGN":            "SignValue",
            "HAS_WONDER":          "WonderValue",
            "HAS_MIRACLE":         "MiracleValue",
            "HAS_PORTENT":         "PortentValue",
            "HAS_OMEN":            "OmenValue",
            "HAS_TOKEN":           "TokenValue",
            "HAS_MARK":            "MarkValue",
            "HAS_SEAL":            "SealValue",
            "HAS_SYMBOL":          "SymbolValue",
        }
        
        node_label = label_map.get(relation_type, "AttributeValue")

        query = f"""
        MATCH (a {{name: $source}})
        MERGE (v:{node_label} {{value: $value}})
        MERGE (a)-[r:{relation_type}]->(v)
        """
        handler.execute_query(query, {
            "source": source,
            "value":  target_value
        })

    def create_relationships_between_entities(
        self,
        handler,
        verse_text: str,
        entities: list,
        context_verses: list = None,
    ):
        """
        Extract and create all relationships between entities in a verse.

        Args:
            handler        : Neo4j handler.
            verse_text     : The current verse text.
            entities       : Sanitized entity list for this verse.
            context_verses : List of previous verse texts (up to 3) for pronoun resolution.

        Handles:
          - Type A: entity → entity (with optional numeric properties)
          - Type B: entity → value string node (HAS_STATE, HAS_ROLE, etc.)
          - Auto-creation of missing entities found in verse
        """
        print("\nRELATIONSHIP EXTRACTION START")

        prompt = get_relationship_extraction_prompt(
            bible_text=verse_text,
            entities=entities,
            context_verses=context_verses,
        )
        relations = self.llm.call_kg_worker(prompt=prompt)

        if not isinstance(relations, list):
            print("[SKIP] Invalid relation output")
            return []

        valid_names   = {e["name"].strip() for e in entities if e.get("name")}
        newly_created = set()
        created       = []

        for rel in relations:
            if not isinstance(rel, dict):
                continue

            source        = rel.get("source")
            target        = rel.get("target")
            relation_type = rel.get("relationship")

            # Basic validation
            if not all(isinstance(x, str) for x in [source, target, relation_type]):
                print(f"[SKIP] None or invalid field: {rel}")
                continue

            source        = source.strip()
            target        = target.strip()
            relation_type = relation_type.strip().upper()

            if not source or not target or not relation_type:
                print(f"[SKIP] Empty field after strip: {rel}")
                continue

            if source == target:
                print(f"[SKIP] Self-relationship: {source}")
                continue

            # Sanitize
            relation_type  = re.sub(r'[^a-zA-Z0-9_]', '_', relation_type)
            rel_properties = self._sanitize_properties(rel.get("properties", {}))

            # Determine Type A vs Type B
            is_b = self._is_type_b(target, valid_names)

            if is_b:
                # ────────────────────────────────────────────────────
                # TYPE B — entity → value string
                # ────────────────────────────────────────────────────
                
                # Check source exists (may be from context or verse)
                if source not in valid_names and source not in newly_created:
                    # Build combined search text (context + current verse)
                    search_text = verse_text
                    if context_verses:
                        search_text = " ".join(context_verses) + " " + verse_text
                    
                    if self._entity_exists_in_verse(source, search_text):
                        if self._create_missing_entity(handler, source, verse_text):
                            valid_names.add(source)
                            newly_created.add(source)
                        else:
                            print(f"[SKIP] Could not create source: '{source}'")
                            continue
                    else:
                        print(f"[SKIP] Source '{source}' not in verse or context")
                        continue

                # Type B allows any value string as target (including "none", "childless")
                # No need to validate target against entity list
                try:
                    self._create_type_b_relationship(handler, source, relation_type, target)
                    created.append(rel)
                    print(f"[OK-B] {source} -[{relation_type}]-> \"{target}\"")
                except Exception as e:
                    print(f"[ERROR] Type B failed: {source} -[{relation_type}]-> \"{target}\": {e}")

            else:
                # ────────────────────────────────────────────────────
                # TYPE A — entity → entity
                # ────────────────────────────────────────────────────
                
                # Build combined search text for auto-creation
                search_text = verse_text
                if context_verses:
                    search_text = " ".join(context_verses) + " " + verse_text
                
                # Auto-create source if missing
                if source not in valid_names and source not in newly_created:
                    if self._entity_exists_in_verse(source, search_text):
                        if self._create_missing_entity(handler, source, verse_text):
                            valid_names.add(source)
                            newly_created.add(source)
                        else:
                            print(f"[SKIP] Could not create source: '{source}'")
                            continue
                    else:
                        print(f"[SKIP] Source '{source}' not in verse or context")
                        continue

                # Auto-create target if missing
                if target not in valid_names and target not in newly_created:
                    if self._entity_exists_in_verse(target, search_text):
                        if self._create_missing_entity(handler, target, verse_text):
                            valid_names.add(target)
                            newly_created.add(target)
                        else:
                            print(f"[SKIP] Could not create target: '{target}'")
                            continue
                    else:
                        print(f"[SKIP] Target '{target}' not in verse or context")
                        continue

                try:
                    self._create_type_a_relationship(
                        handler, source, relation_type, target, rel_properties
                    )
                    created.append(rel)
                    props_str = f" {rel_properties}" if rel_properties else ""
                    print(f"[OK-A] {source} -[{relation_type}]-> {target}{props_str}")
                except Exception as e:
                    print(f"[ERROR] Type A failed: {source} -[{relation_type}]-> {target}: {e}")

        print(f"\nTOTAL CREATED: {len(created)}")
        print(f"AUTO-CREATED ENTITIES: {len(newly_created)}")
        return created

    # ─────────────────────────────────────────────────────────────
    # AUTO ENTITY CREATION HELPERS
    # ─────────────────────────────────────────────────────────────

    def _entity_exists_in_verse(self, entity_name: str, verse_text: str) -> bool:
        entity_lower = entity_name.lower().strip()
        verse_lower  = verse_text.lower()

        if entity_lower in verse_lower:
            return True

        variations = [
            f"the {entity_lower}",
            f"{entity_lower}s",
            entity_lower.replace(" of ", " "),
        ]
        for variant in variations:
            if variant in verse_lower:
                return True

        words = re.findall(r'\b\w+\b', verse_lower)
        for word in words:
            if SequenceMatcher(None, entity_lower, word).ratio() > 0.8:
                return True

        return False

    def _infer_entity_type(self, entity_name: str, verse_text: str) -> str:
        """
        Infer entity type from name and context. Comprehensive mapping for all
        biblical entity types from Genesis to Revelation.
        """
        entity_lower = entity_name.lower().strip()
        verse_lower  = verse_text.lower()

        # ── DIVINE & SPIRITUAL ENTITIES ──
        if any(w in entity_lower for w in [
            'god', 'god\'s', 'lord', 'yahweh', 'jehovah', 'almighty', 'most high',
            'father', 'son', 'holy spirit', 'holy ghost', 'jesus', 'christ',
            'messiah', 'savior', 'redeemer', 'judge', 'creator', 'sustainer'
        ]):
            return "DivineEntity"

        if any(w in entity_lower for w in [
            'angel', 'archangel', 'seraph', 'cherub', 'gabriel', 'michael',
            'raphael', 'uriel', 'messenger', 'heavenly being'
        ]):
            return "Angel"

        if any(w in entity_lower for w in [
            'demon', 'devil', 'satan', 'lucifer', 'evil spirit', 'unclean spirit',
            'malevolent', 'serpent', 'adversary', 'belial', 'beelzebub'
        ]):
            return "DemonOrEvil"

        if any(w in entity_lower for w in [
            'spirit', 'ghost', 'shade', 'specter', 'apparition'
        ]):
            return "SpiritualEntity"

        # ── PERSONS (with specific roles) ──
        if any(w in entity_lower for w in [
            'king', 'pharaoh', 'ruler', 'caesar', 'herod', 'nebuchadnezzar',
            'darius', 'xerxes', 'cyrus', 'augustus'
        ]):
            return "King"

        if any(w in entity_lower for w in [
            'queen', 'esther', 'bathsheba', 'jezebel', 'vashti', 'candace'
        ]):
            return "Queen"

        if any(w in entity_lower for w in [
            'priest', 'high priest', 'levite', 'aaron', 'melchizedek',
            'caiaphas', 'annas', 'zacharias'
        ]):
            return "Priest"

        if any(w in entity_lower for w in [
            'prophet', 'seer', 'moses', 'elijah', 'elisha', 'isaiah', 'jeremiah',
            'ezekiel', 'daniel', 'hosea', 'amos', 'obadiah', 'jonah', 'micah',
            'nahum', 'habakkuk', 'zephaniah', 'haggai', 'zechariah', 'malachi',
            'john the baptist', 'samuel', 'nathan', 'gad'
        ]):
            return "Prophet"

        if any(w in entity_lower for w in [
            'apostle', 'disciple', 'peter', 'james', 'john', 'andrew', 'thomas',
            'matthew', 'philip', 'bartholomew', 'mark', 'luke', 'paul', 'barnabas'
        ]):
            return "Apostle"

        if any(w in entity_lower for w in [
            'patriarch', 'abraham', 'isaac', 'jacob', 'israel',
            'david', 'solomon', 'joseph', 'moses'
        ]):
            return "Patriarch"

        if any(w in entity_lower for w in [
            'matriarch', 'sarah', 'rebecca', 'leah', 'rachel',
            'eve', 'mary', 'martha', 'mary magdalene'
        ]):
            return "Matriarch"

        if any(w in entity_lower for w in [
            'man', 'male', 'boy', 'son'
        ]):
            return "Person"

        if any(w in entity_lower for w in [
            'woman', 'female', 'girl', 'daughter', 'wife', 'mother'
        ]):
            return "Person"

        if any(w in entity_lower for w in [
            'person', 'people', 'human', 'mankind', 'mortal', 'someone', 'servant'
        ]):
            return "Person"

        # ── GROUPS & NATIONS ──
        if any(w in entity_lower for w in [
            'israel', 'israelite', 'judah', 'judean', 'hebrew', 'jew',
            'ephraim', 'benjamin', 'simeon', 'tribe', 'nation', 'kingdom'
        ]):
            return "Group"

        if any(w in entity_lower for w in [
            'egypt', 'egyptian', 'assyria', 'assyrian', 'babylon', 'babylonian',
            'persia', 'persian', 'greece', 'greek', 'rome', 'roman',
            'philistine', 'canaanite', 'amorite', 'moabite', 'edomite'
        ]):
            return "Group"

        if any(w in entity_lower for w in [
            'family', 'household', 'house of', 'lineage', 'clan', 'assembly',
            'congregation', 'church', 'synagogue', 'council', 'sanhedrin'
        ]):
            return "Group"

        # ── LOCATIONS & GEOGRAPHY ──
        if any(w in entity_lower for w in [
            'eden', 'garden', 'bethlehem', 'nazareth', 'jerusalem', 'jericho',
            'damascus', 'tyre', 'sidon', 'gaza', 'samaria', 'galilee',
            'athens', 'rome', 'corinth', 'ephesus', 'philadelphia', 'thyatira',
            'babylon', 'memphis', 'thebes', 'nineveh', 'ur'
        ]):
            return "City"

        if any(w in entity_lower for w in [
            'judea', 'galilee', 'samaria', 'perea', 'decapolis', 'transjordan',
            'egypt', 'assyria', 'babylon', 'persia', 'greece', 'rome',
            'canaan', 'phenicia', 'moab', 'edom', 'ammon', 'aram'
        ]):
            return "Region"

        if any(w in entity_lower for w in [
            'mount', 'mountain', 'sinai', 'horeb', 'carmel', 'zion', 'ararat',
            'tabor', 'gilboa', 'hermon', 'olive', 'moriah', 'gerizim', 'ebal',
            'hill', 'peak', 'summit', 'volcano'
        ]):
            return "NamedLocation"

        if any(w in entity_lower for w in [
            'jordan', 'nile', 'euphrates', 'tigris', 'river', 'stream',
            'red sea', 'dead sea', 'galilee', 'sea', 'lake', 'water'
        ]):
            return "NamedLocation"

        if any(w in entity_lower for w in [
            'land', 'place', 'territory', 'wilderness', 'desert', 'field',
            'valley', 'plain', 'forest', 'grove', 'threshing floor'
        ]):
            return "Place"

        # ── BUILDINGS & STRUCTURES ──
        if any(w in entity_lower for w in [
            'temple', 'tabernacle', 'sanctuary', 'holy of holies', 'holy place'
        ]):
            return "Temple"

        if any(w in entity_lower for w in [
            'altar', 'ark', 'golden altar', 'brazen altar', 'incense altar'
        ]):
            return "Building"

        if any(w in entity_lower for w in [
            'house', 'home', 'dwelling', 'tent', 'palace', 'fortress', 'tower',
            'wall', 'gate', 'city', 'building', 'structure'
        ]):
            return "Building"

        if any(w in entity_lower for w in [
            'tomb', 'sepulcher', 'cave', 'grave', 'cemetery'
        ]):
            return "Building"

        # ── NATURAL PHENOMENA ──
        if any(w in entity_lower for w in [
            'earth', 'world', 'ground', 'soil', 'dust', 'clay', 'rock', 'stone'
        ]):
            return "NaturalPhenomenon"

        if any(w in entity_lower for w in [
            'sky', 'heaven', 'heavens', 'firmament', 'vault', 'expanse'
        ]):
            return "NaturalPhenomenon"

        if any(w in entity_lower for w in [
            'water', 'waters', 'sea', 'ocean', 'river', 'stream', 'spring',
            'well', 'rain', 'flood', 'deluge', 'moisture'
        ]):
            return "NaturalPhenomenon"

        if any(w in entity_lower for w in [
            'light', 'darkness', 'day', 'night', 'dawn', 'dusk', 'shadow', 'shade'
        ]):
            return "NaturalPhenomenon"

        if any(w in entity_lower for w in [
            'fire', 'flame', 'burning', 'blaze', 'furnace', 'heat'
        ]):
            return "NaturalPhenomenon"

        if any(w in entity_lower for w in [
            'wind', 'breeze', 'gust', 'storm', 'whirlwind', 'tempest', 'weather'
        ]):
            return "NaturalPhenomenon"

        if any(w in entity_lower for w in [
            'sun', 'moon', 'star', 'stars', 'constellation', 'planet', 'comet'
        ]):
            return "CelestialBody"

        if any(w in entity_lower for w in [
            'cloud', 'clouds', 'vapor', 'mist', 'fog', 'thunder', 'lightning'
        ]):
            return "NaturalPhenomenon"

        if any(w in entity_lower for w in [
            'snow', 'ice', 'hail', 'frost', 'cold'
        ]):
            return "NaturalPhenomenon"

        # ── ANIMALS ──
        if any(w in entity_lower for w in [
            'serpent', 'snake', 'dragon', 'viper', 'asp'
        ]):
            return "Animal"

        if any(w in entity_lower for w in [
            'lion', 'bear', 'wolf', 'leopard', 'ox', 'bull', 'calf',
            'donkey', 'ass', 'horse', 'mule', 'sheep', 'lamb', 'goat',
            'pig', 'hog', 'camel', 'deer', 'gazelle', 'antelope'
        ]):
            return "Animal"

        if any(w in entity_lower for w in [
            'bird', 'eagle', 'vulture', 'hawk', 'raven', 'crow', 'dove',
            'pigeon', 'owl', 'sparrow', 'swallow', 'crane', 'heron', 'stork'
        ]):
            return "Animal"

        if any(w in entity_lower for w in [
            'fish', 'whale', 'sea creature', 'sea monster', 'leviathan'
        ]):
            return "Animal"

        if any(w in entity_lower for w in [
            'locust', 'grasshopper', 'cricket', 'bee', 'hornet', 'fly', 'worm',
            'serpent', 'lizard', 'frog', 'toad', 'insect', 'creature', 'beast'
        ]):
            return "Animal"

        # ── PLANTS & VEGETATION ──
        if any(w in entity_lower for w in [
            'tree', 'trees', 'oak', 'cedar', 'pine', 'fig', 'olive', 'vine',
            'palm', 'sycamore', 'terebinth', 'acacia', 'almond', 'apple'
        ]):
            return "Plant"

        if any(w in entity_lower for w in [
            'grass', 'herb', 'plant', 'vegetation', 'foliage', 'leaf', 'leaves',
            'flower', 'blossom', 'thorn', 'thistle', 'weed', 'straw'
        ]):
            return "Plant"

        if any(w in entity_lower for w in [
            'wheat', 'barley', 'grain', 'corn', 'seed', 'harvest', 'field'
        ]):
            return "Plant"

        # ── FOOD & DRINK ──
        if any(w in entity_lower for w in [
            'bread', 'loaf', 'grain', 'wheat', 'barley', 'flour', 'meal',
            'unleavened bread', 'manna'
        ]):
            return "Food"

        if any(w in entity_lower for w in [
            'fruit', 'apple', 'fig', 'grape', 'pomegranate', 'olive', 'date',
            'berry', 'vegetable', 'herb', 'bitter herbs'
        ]):
            return "Food"

        if any(w in entity_lower for w in [
            'wine', 'water', 'milk', 'honey', 'oil', 'oil', 'vinegar',
            'drink', 'beverage', 'wine'
        ]):
            return "Food"

        if any(w in entity_lower for w in [
            'meat', 'flesh', 'lamb', 'goat', 'bull', 'fish', 'bird'
        ]):
            return "Food"

        # ── ARTIFACTS & OBJECTS ──
        if any(w in entity_lower for w in [
            'ark', 'chest', 'box', 'vessel', 'jar', 'pitcher', 'cup', 'goblet',
            'basin', 'bowl', 'plate', 'dish', 'table', 'candlestick', 'lampstand'
        ]):
            return "Artifact"

        if any(w in entity_lower for w in [
            'sword', 'spear', 'dagger', 'arrow', 'bow', 'sling', 'club',
            'mace', 'axe', 'hammer', 'weapon', 'armor', 'breastplate',
            'shield', 'helmet', 'coat of mail'
        ]):
            return "Artifact"

        if any(w in entity_lower for w in [
            'staff', 'rod', 'scepter', 'crown', 'throne', 'seat', 'chair'
        ]):
            return "Artifact"

        if any(w in entity_lower for w in [
            'lamp', 'light', 'torch', 'candle', 'fire', 'altar', 'incense',
            'censer', 'pan', 'tongs', 'bell', 'pomegranate'
        ]):
            return "Artifact"

        if any(w in entity_lower for w in [
            'scroll', 'tablet', 'stone', 'parchment', 'paper', 'book', 'letter'
        ]):
            return "Artifact"

        if any(w in entity_lower for w in [
            'cloth', 'robe', 'garment', 'tunic', 'mantle', 'veil', 'curtain',
            'linen', 'wool', 'leather', 'silk', 'purple'
        ]):
            return "Artifact"

        # ── MATERIALS & MINERALS ──
        if any(w in entity_lower for w in [
            'gold', 'silver', 'bronze', 'copper', 'iron', 'tin', 'lead',
            'metal', 'ore', 'stone', 'marble', 'jasper', 'pearl'
        ]):
            return "Material"

        if any(w in entity_lower for w in [
            'wood', 'timber', 'cedar', 'acacia', 'shittim'
        ]):
            return "Material"

        if any(w in entity_lower for w in [
            'clay', 'pottery', 'ceramic', 'brick', 'mortar'
        ]):
            return "Material"

        if any(w in entity_lower for w in [
            'glass', 'crystal', 'stone', 'rock', 'granite', 'limestone'
        ]):
            return "Material"

        # ── TIME & CALENDAR ──
        if any(w in entity_lower for w in [
            'day', 'night', 'morning', 'evening', 'noon', 'midnight',
            'dawn', 'dusk', 'time'
        ]):
            return "TimeConcept"

        if any(w in entity_lower for w in [
            'week', 'year', 'month', 'season', 'sabbath', 'generation',
            'era', 'age', 'epoch', 'period'
        ]):
            return "TimeConcept"

        if any(w in entity_lower for w in [
            'passover', 'pentecost', 'tabernacles', 'thanksgiving', 'feast',
            'festival', 'holiday'
        ]):
            return "TimeConcept"

        # ── EVENTS & MIRACLES ──
        if any(w in entity_lower for w in [
            'creation', 'exodus', 'flood', 'deluge', 'plague', 'judgment',
            'war', 'battle', 'victory', 'defeat', 'exile', 'return',
            'resurrection', 'ascension', 'crucifixion', 'persecution'
        ]):
            return "Event"

        if any(w in entity_lower for w in [
            'miracle', 'sign', 'wonder', 'marvel', 'portent', 'omen'
        ]):
            return "Miracle"

        # ── SPIRITUAL & ABSTRACT CONCEPTS ──
        if any(w in entity_lower for w in [
            'covenant', 'contract', 'agreement', 'oath', 'vow', 'promise'
        ]):
            return "AbstractConcept"

        if any(w in entity_lower for w in [
            'law', 'commandment', 'statute', 'ordinance', 'decree', 'rule',
            'torah', 'ten commandments'
        ]):
            return "AbstractConcept"

        if any(w in entity_lower for w in [
            'word', 'truth', 'wisdom', 'knowledge', 'understanding', 'counsel',
            'guidance', 'instruction', 'teaching', 'doctrine'
        ]):
            return "AbstractConcept"

        if any(w in entity_lower for w in [
            'faith', 'grace', 'mercy', 'compassion', 'love', 'charity',
            'righteousness', 'holiness', 'sanctity', 'purity', 'justice',
            'peace', 'joy', 'hope', 'salvation', 'redemption'
        ]):
            return "SpiritualConcept"

        if any(w in entity_lower for w in [
            'sin', 'transgression', 'iniquity', 'rebellion', 'disobedience',
            'wickedness', 'evil', 'darkness', 'death', 'curse', 'wrath'
        ]):
            return "SpiritualConcept"

        if any(w in entity_lower for w in [
            'blessing', 'prosperity', 'abundance', 'fertility', 'increase',
            'favor', 'glory', 'honor', 'exaltation', 'triumph'
        ]):
            return "SpiritualConcept"

        # ── DISEASES & AFFLICTIONS ──
        if any(w in entity_lower for w in [
            'leprosy', 'disease', 'sickness', 'plague', 'pestilence', 'fever',
            'illness', 'affliction', 'infirmity', 'wound', 'sore', 'boil',
            'blindness', 'deafness', 'muteness', 'lameness', 'paralysis'
        ]):
            return "Disease"

        # ── FALLBACK WITH CONTEXT ANALYSIS ──
        # Check for creation/formation verbs
        if re.search(rf'\b{re.escape(entity_lower)}\b.*?(created|made|formed|established|fashioned)', verse_lower):
            return "NaturalPhenomenon"

        # Check if it's a demon or evil entity
        if any(w in entity_lower for w in ['demon', 'unclean', 'evil']):
            return "DemonOrEvil"

        # Default fallback
        return "Unknown"

    def _create_missing_entity(self, handler, entity_name: str, verse_text: str) -> bool:
        entity_name = entity_name.strip()
        entity_type = re.sub(r'[^a-zA-Z0-9_]', '_',
                             self._infer_entity_type(entity_name, verse_text))
        query = f"MERGE (e:{entity_type} {{name: $name}})"
        try:
            handler.execute_query(query, {"name": entity_name})
            print(f"[AUTO-CREATE] {entity_name} ({entity_type})")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to create entity '{entity_name}': {e}")
            return False

    def create_mentions_relationship_for_auto_entities(
        self, handler, entity_name, book, chapter, verse_num
    ):
        query = "MATCH (e {name: $name}) RETURN labels(e) AS types LIMIT 1"
        try:
            records, _, _ = handler.execute_query(query, {"name": entity_name})
            if records and records[0]["types"]:
                entity_type = records[0]["types"][0]
                mention_query = f"""
                MATCH (e:{entity_type} {{name: $name}})
                MATCH (v:Verse {{book: $book, chapter: $chapter, verse: $verse}})
                MERGE (v)-[:MENTIONS]->(e)
                """
                handler.execute_query(mention_query, {
                    "name": entity_name, "book": book,
                    "chapter": chapter, "verse": verse_num
                })
        except Exception as e:
            print(f"[WARNING] Could not create MENTIONS for {entity_name}: {e}")

    # ─────────────────────────────────────────────────────────────
    # MAIN VERSE PROCESSING
    # ─────────────────────────────────────────────────────────────

    def process_verse(self, handler, verse, context_verses: list = None):
        """
        Process a single verse: extract entities and relationships, write to Neo4j.

        Args:
            handler        : Neo4j handler.
            verse          : Verse dict with keys: book, chapter, verse, text.
            context_verses : List of up to 3 previous verse texts (same chapter).
        """
        book      = verse['book']
        chapter   = verse['chapter']
        verse_num = verse['verse']
        text      = verse['text']

        print("\n" + "=" * 60)
        print(f"VERSE: {book} {chapter}:{verse_num}")
        if context_verses:
            context_str = " | ".join(context_verses)
            print(f"CONTEXT ({len(context_verses)} verses): {context_str[:80]}{'...' if len(context_str) > 80 else ''}")
        print("-" * 60)
        print(text)
        print("-" * 60)

        # ── 1. EXTRACT ENTITIES (with context for pronoun resolution) ──
        raw_entities = self.extract_entities_from_verse(
            text=text,
            context_verses=context_verses,
        )

        print(f"TOTAL ENTITIES: {len(raw_entities)}")
        print("ENTITIES:")
        for e in raw_entities:
            print(f"  - {e.get('type')} | {e.get('name')} | {e.get('properties', {})}")
        print("=" * 60)

        # ── 2. CREATE VERSE NODE ──
        self.create_verse_node(
            handler=handler, book=book,
            chapter=chapter, verse_num=verse_num, text=text
        )

        # ── 3. CREATE ENTITY NODES + MENTIONS ──
        clean_entities = []

        for entity in raw_entities:
            cleaned = self.sanitize_entity(entity)
            if cleaned is None:
                continue

            entity_type  = cleaned["type"]
            entity_name  = cleaned["name"]
            entity_props = cleaned["properties"]

            self.create_entity_node(
                handler=handler,
                entity_type=entity_type,
                entity_name=entity_name,
                properties=entity_props if entity_props else None
            )

            self.create_mentions_relationship(
                handler=handler,
                entity_type=entity_type,
                entity_name=entity_name,
                book=book, chapter=chapter, verse_num=verse_num
            )

            clean_entities.append(cleaned)

        # ── 4. EXTRACT & CREATE RELATIONSHIPS ──
        relationships = self.create_relationships_between_entities(
            handler=handler,
            verse_text=text,
            entities=clean_entities,
            context_verses=context_verses,
        )

        print("RELATIONSHIPS:")
        for r in relationships:
            props_str = f" {r.get('properties')}" if r.get('properties') else ""
            print(f"  - {r.get('source')} -[{r.get('relationship')}]-> {r.get('target')}{props_str}")
        print("=" * 60)

        # ── 5. MENTIONS for auto-created entities ──
        known_names = {e["name"] for e in clean_entities}
        for rel in relationships:
            for name in [rel.get('source', ''), rel.get('target', '')]:
                name = name.strip()
                if name and name not in known_names:
                    self.create_mentions_relationship_for_auto_entities(
                        handler=handler, entity_name=name,
                        book=book, chapter=chapter, verse_num=verse_num
                    )

    # ─────────────────────────────────────────────────────────────
    # CONTEXT WINDOW MANAGEMENT
    # ─────────────────────────────────────────────────────────────

    def _get_context_window(self, bible, current_index, window_size=3):
        """
        Get up to window_size previous verses from the SAME CHAPTER.
        Returns list of verse texts.
        """
        if current_index == 0:
            return []
        
        current = bible[current_index]
        context = []
        
        # Look back up to window_size verses
        for i in range(max(0, current_index - window_size), current_index):
            prev = bible[i]
            # Stop if different chapter/book
            if prev['book'] != current['book'] or prev['chapter'] != current['chapter']:
                break
            context.append(prev['text'])
        
        return context

    # ─────────────────────────────────────────────────────────────
    # PIPELINE ENTRY POINT
    # ─────────────────────────────────────────────────────────────

    def create_bible_kg_with_entities(self):
        bible   = self.get_bible()
        handler = Neo4jHandler()
        handler.connect()

        processed_ids = self._load_processed_ids()

        for idx, verse in enumerate(bible):
            verse_id = verse.get("id")

            if verse_id in processed_ids:
                continue

            # Get context window (up to 3 previous verses, same chapter)
            context_verses = self._get_context_window(bible, idx, window_size=3)

            # Process verse with retry
            success = False
            for attempt in range(100):
                try:
                    self.process_verse(
                        handler=handler,
                        verse=verse,
                        context_verses=context_verses,
                    )
                    success = True
                    break
                except Exception as e:
                    print(
                        f"[ERROR] {verse.get('book')} {verse.get('chapter')}:{verse.get('verse')} "
                        f"attempt {attempt + 1}: {e}"
                    )
                    traceback.print_exc()
                    time.sleep(1.5)

            if success:
                self._log_processed_verse(verse)
            else:
                print(f"[FAILED] Skipping verse after 100 attempts: {verse}")

        handler.close()

    # ─────────────────────────────────────────────────────────────
    # PROCESSED VERSE TRACKING
    # ─────────────────────────────────────────────────────────────

    def _load_processed_ids(self) -> set:
        path = CONFIG['PROCESSED_VERSES_FILEPATH']
        if not os.path.exists(path):
            return set()
        processed = set()
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    processed.add(json.loads(line.strip())["id"])
                except Exception:
                    continue
        return processed

    def _log_processed_verse(self, verse: dict):
        path = CONFIG['PROCESSED_VERSES_FILEPATH']
        os.makedirs(os.path.dirname(path), exist_ok=True)
        record = {
            "id":           verse.get("id"),
            "book":         verse.get("book"),
            "chapter":      verse.get("chapter"),
            "verse":        verse.get("verse"),
            "processed_at": datetime.utcnow().isoformat()
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    creator = BibleKGCreator()
    creator.create_bible_kg_with_entities()