import json

def get_prompt_refiner_prompt(initial_query):
    prompt = f"""
        You are an expert linguistic editor.

        TASK:
        Refine the given user query to be grammatically correct, clear, and precise.

        INSTRUCTIONS:
        1. Fix spelling and grammar errors
        2. Preserve original semantic meaning exactly
        3. Do NOT add any new information
        4. Do NOT remove any important intent
        5. Keep it concise, yet detailed

        OUTPUT FORMAT (STRICT JSON):
        {{
            "refined_query": "..."
        }}

        CRITICAL:
        - Output MUST be valid JSON
        - Do NOT include any text outside JSON
        - Do NOT include explanations
        - Do NOT include markdown
        - Do NOT include trailing commas
        - Do NOT include comments

        USER QUERY INPUT:
        {initial_query}
    """
    return prompt


def get_prompt_analyzer_prompt(refined_query):
    prompt = f"""
        You are a context extraction specialist.

        TASK:
        Transform the user query into a structured user context.

        INSTRUCTIONS:
        1. Identify the main objective of the query
        2. Extract key details explicitly mentioned or strongly implied
        3. Identify constraints or requirements if present
        4. Do NOT introduce any form of external information
        5. If something is not clearly stated, do NOT infer it
        6. Classify the intent type of the query

        INTENT TYPES (choose one):
        - explanation
        - comparison
        - direct answering

        OUTPUT FORMAT (STRICT):
        {{
            "objective": "...",
            "key_details": ["...", "..."],
            "constraints": ["...", "..."],
            "intent_type": "..."
        }}

        CRITICAL:
        - Output MUST be valid JSON
        - Do NOT include <think> or explanations
        - Do NOT include markdown
        - Do NOT include trailing commas
        - Do NOT include comments
        - Do NOT include explanations
        - If unsure, return the correct schema with empty values

        DEFINITIONS:
        - objective: main goal of the query
        - key_details: important elements mentioned
        - constraints: limitations or requirements
        - intent_type: category of the query

        CONSTRAINTS:
        1. No speculation
        2. No repetition
        3. Be concise
        4. Use only the query

        QUERY INPUT:
        {refined_query}
    """
    return prompt


def get_cot_steps_prompt(refined_query, user_context):
    intent = user_context.get("intent_type", "") if isinstance(user_context, dict) else ""

    if intent not in ["explanation", "comparison", "direct answering"]:
        intent = "explanation"

    user_context = json.dumps(user_context, indent=2, ensure_ascii=False)

    prompt = f"""
        You are a structured reasoning planner.

        TASK:
        Generate a minimal set of reasoning ACTIONS required to solve the query.

        INTENT TYPE:
        {intent}

        INSTRUCTIONS:
        1. Generate at most 5 steps
        2. Each step must be necessary, actionable, and contributing to answer the question
        3. Do NOT answer the query

        CRITICAL RULE:
        - You are NOT allowed to answer the query under any circumstances
        - You are ONLY allowed to produce planning steps
        - Any explanation, answer, or conclusion will be considered invalid

        INTENT-SPECIFIC GUIDELINES:

        - If intent_type = "explanation":
            > Focus on logical flow and clarity
            > Steps should build understanding progressively
            > Start from definition --> mechanism --> implications

        - If intent_type = "comparison":
            > Structure steps in parallel (A vs B)
            > Identify comparison dimensions (features, pros/ cons, performance)
            > Ensure fairness and symmetry

        - If intent_type = "direct_answering":
            > Minimize steps (2-4 preferred)
            > Focus only on essential reasoning
            > Avoid unnecessary decomposition

        YOU MUST FOLLOW THIS EXACT PATTERN:
        - Output must start with [
        - Output must end with ]
        - No text before or after

        OUTPUT FORMAT (STRICT):
        [
            "step 1",
            "step 2",
            "step 3"
        ]

        CORRECT EXAMPLE:
        [
            "Define the concept of X",
            "Explain how X works",
            "Analyze implications of X"
        ]

        INCORRECT EXAMPLE (DO NOT DO THIS):
        [1. Define X, 2. Explain X]

        INVALID OUTPUT EXAMPLES:
        - Any paragraph explanation
        - Any numbered list (1., 2., etc.)
        - Any sentence outside JSON
        - Any conclusion or summary

        CONSTRAINTS:
        1. No repetition
        2. No vague steps
        3. No unnecessary steps
        4. No final answer
        5. Merge steps if they describe closely related actions

        CRITICAL:
        - Output MUST be valid JSON
        - Output MUST be a JSON array of strings
        - Do NOT number the steps
        - Do NOT include anything except the JSON array
        - Each item MUST be a string. Do NOT use numbering like "1.".
        - Do NOT include trailing commas
        - Do NOT include comments
        - Do NOT include explanations
        - If unsure, return the correct schema with empty values

        TASK INPUT:
        - Query: {refined_query}
        - Context: {user_context}
    """
    return prompt


def get_generate_sub_questions_prompt(refined_query, cot_steps):
    cot_steps = json.dumps(cot_steps, indent=2, ensure_ascii=False)

    prompt = f"""
        You are a query decomposition expert.

        TASK:
        Generate sub_questions to retrieve complete information.

        Instructions:
        1. Each sub_question must target missing information
        2. Cover all reasoning steps
        3. Avoid redundancy
        4. Optimize for retrieval systems (RAG)
        5. Ensure all reasoning steps are covered at least once

        OUTPUT FORMAT (STRICT JSON ARRAY):
        [
            "sub_question 1",
            "sub_question 2",
            "sub_question 3"
        ]

        CONSTRAINTS:
        1. No overlap
        2. No vague questions
        3. No answering

        CRITICAL:
        - Output MUST be valid JSON
        - Output MUST be a JSON array of strings
        - Do NOT number the steps
        - Do NOT include anything except the JSON array
        - Do NOT include trailing commas
        - Do NOT include comments
        - Do NOT include explanations
        - If unsure, return the correct schema with empty values

        TASK INPUT:
        - Query: {refined_query}
        - Reasoning Steps: {cot_steps}
    """
    return prompt


def get_analyze_entity_prompt(sub_questions, refined_query):
    sub_questions = json.dumps(sub_questions, indent=2, ensure_ascii=False)

    prompt = f"""
        You are an entity extraction and ranking specialist

        TASK:
        Extract and prioritize entities for guided retrieval

        INSTRUCTIONS:
        1. Identify key entities required to answer the query
        2. Assign an importance score (0 to 1) to each entity
        3. Keep only the most relevant entities (max 8)
        4. Prefer specific over generic entities
        5. Prefer entities that improve retrieval specificity
        6. Avoid generic terms unless necessary
        7. Every object MUST contain ALL required keys
        8. Do NOT omit any fields

        ENTITY TYPES:
        - Concepts
        - Objects
        - Technical terms
        - Named entities

        OUTPUT FORMAT (STRICT):
        [
            {{"entity": "...", "score": 0.0-1.0}}
        ]

        CRITICAL:
        - Output MUST be valid JSON
        - Do NOT include <think> or explanations
        - Do NOT include markdown
        - Response must start with [ and end with ]
        - Do NOT include trailing commas
        - Do NOT include comments
        - Do NOT include explanations outside JSON
        - If unsure, return the correct schema with empty values

        CONSTRAINTS:
        1. No duplication
        2. No vague entities
        3. No irrelevant entities

        TASK INPUT:
        - Sub-questions: {sub_questions}
        - Query: {refined_query}
    """
    return prompt


def get_fusion_units_prompt(cot_steps, sub_questions, entity_metadata, refined_prompt):
    cot_steps = json.dumps(cot_steps, indent=2, ensure_ascii=False)
    sub_questions = json.dumps(sub_questions, indent=2, ensure_ascii=False)
    entity_metadata = json.dumps(entity_metadata, indent=2, ensure_ascii=False)

    prompt = f"""
        You are a reasoning alignment specialist

        TASK:
        Combine reasoning steps, sub_questions, and entities into aligned reasoning units.

        EACH UNIT MUST CONTAIN:
        1. One reasoning step
        2. One matching sub_question
        3. A small set of relevant entities

        INSTRUCTIONS:
        1. Match each reasoning step with the most relevant sub_question
        2. Assign only the entities that directly support that step
        3. Remove any and all redundant or overlapping items
        4. If elements do not align well, discard weak ones or unaligned elements
        5. Ensure each unit represents a unique information need
        6. Assign a unique unit_id to each unit

        OUTPUT FORMAT (STRICT):
        [
            {{
                "unit_id": "unit_0",
                "step": "...",
                "sub_question": "...",
                "entities": ["...", "..."]
            }}
        ]

        CRITICAL:
        - Output MUST be valid JSON
        - Do NOT include <think> or explanations
        - Do NOT include markdown
        - Response must start with [ and end with ]
        - Do NOT include trailing commas
        - Do NOT include comments
        - Do NOT include explanations
        - If unsure, return the correct schema with empty values

        CONSTRAINTS:
        1. Maximum 5 units
        2. No duplication across units
        3. No vague entities
        4. No unused steps or sub_questions
        5. Do NOT create new information beyond inputs

        TASK INPUT:
        - Reasoning steps: {cot_steps}
        - Sub_questions: {sub_questions}
        - Entities: {entity_metadata}
        - Query: {refined_prompt}
    """
    return prompt


def get_fusion_confidence_prompt(reasoning_units, refined_query):
    reasoning_units = json.dumps(reasoning_units, indent=2, ensure_ascii=False)

    prompt = f"""
        You are a reasoning quality evaluator

        TASK:
        Evaluate the quality of each reasoning unit. For each unit, assign a confidence score (0.0-1.0).

        SCORING CRITERIA:
        1. Alignment: Does the step match the sub_question?
        2. Entity relevance: Are entities directly useful for the step?
        3. Clarity: Is the unit specific and unambiguous?
        4. Completeness: Does the unit represent a meaningful information need?
        5. Use the provided unit_id exactly as given
        6. All numeric values MUST be numbers, not strings

        SCORING GUIDELINES:
        - 0.9-1.0 --> Excellent alignment and clarity
        - 0.7-0.89 --> Good but slightly imperfect
        - 0.5-0.69 --> Weak or partially unclear
        - <0.5 --> Poor (should be discarded)

        OUTPUT FORMAT (STRICT):
        [
            {{
                "unit_id": "unit_0",
                "confidence": 0.0
            }}
        ]

        CRITICAL:
        - Output MUST be valid JSON
        - Do NOT include <think> or explanations
        - Do NOT include markdown
        - Response must start with [ and end with ]
        - Do NOT include trailing commas
        - Do NOT include comments
        - Do NOT include explanations
        - If unsure, return the correct schema with empty values
        - If you include ANY text outside the JSON array, your response will be discarded.
        - Do NOT include <think> or reasoning.
        - Return ONLY JSON. No prefix. No suffix. No explanation.

        CONSTRAINTS:
        1. Use full score range
        2. No repetition
        3. No explanation
        4. Do NOT modify original units
        5. All numeric values MUST be numbers, not strings

        TASK INPUT:
        - Reasoning units: {reasoning_units}
        - Query: {refined_query}
    """
    return prompt


def get_data_point_formatter_prompt(step_contexts):
    step_contexts = json.dumps(step_contexts, indent=2, ensure_ascii=False)

    prompt = f"""
        You are a STRICT factual extraction engine.

        TASK:
        Extract ONLY explicitly supported facts from the provided documents.

        DEFINITION OF A VALID FACT:
        - MUST be an EXACT character-for-character substring from the document
        - MUST be directly copy-pasted
        - NO paraphrasing, NO rewriting, NO summarization

        SOURCE_ID RULE:
        - Each document has a unit_id
        - Use that unit_id EXACTLY as the source_id
        - Do NOT invent or modify source_id

        STRICT GROUNDING:
        - If a fact is not explicitly present → DO NOT include it
        - If no valid facts exist → return an empty list []

        FORBIDDEN:
        - Do NOT use prior knowledge
        - Do NOT infer
        - Do NOT generalize
        - Do NOT summarize
        - Do NOT fabricate anything

        OUTPUT FORMAT (STRICT JSON):
        [
        {{
            "fact": "...",
            "source_id": "unit_id_here"
        }}
        ]

        CRITICAL:
        - Output MUST be valid JSON
        - MUST start with [ and end with ]
        - No explanations
        - No markdown
        - No comments
        - No trailing commas

        FAIL-SAFE:
        If you cannot find any EXACT substrings:
        Return []

        INPUT:
        {step_contexts}
    """
    return prompt


def get_debate_1_prompt(point_of_facts, refined_query, cot_steps, debate_context, times_debate):
    cot_steps = json.dumps(cot_steps, indent=2, ensure_ascii=False)

    # Direct answer builder
    prompt = f"""
        You are an argument builder.

        TASK:
        Construct the most direct and accurate answer using the provided facts.

        REASONING STEPS (STRICT GUIDANCE):
        {cot_steps}

        INSTRUCTIONS:
        1. Follow the reasoning steps explicitly when forming your answer
        2. Use only the provided facts
        3. Prioritize high-confidence and well-supported facts
        4. Ensure logical flow following the reasoning steps
        5. Supporting_facts MUST reference valid source_id only
        6. Focus only on disagreements and unresolved issues.
        7. Do NOT restate already agreed information.

        ITERATION RULE:
        - If times_debate == 0:
            > Ignore disagreement constraint
            > Perform full role normally

        - If times_debate > 0:
            > Improve your answer based on previous debate context
            > Address weaknesses, contradictions, and gaps
            > Do NOT repeat previous mistakes

        OUTPUT FORMAT (STRICT):
        {{
            "answer": "...",
            "supporting_facts": ["doc_X", "doc_Y"]
        }}

        CRITICAL:
        - Output MUST be valid JSON
        - Do NOT include <think> or explanations
        - Do NOT include markdown
        - Do NOT include trailing commas
        - Do NOT include comments
        - Do NOT include explanations
        - If unsure, return the correct schema with empty values

        CONSTRAINTS:
        1. No hallucination
        2. No speculation
        3. Be concise
        4. Follow reasoning steps strictly

        TASK INPUT:
        - Facts: {point_of_facts}
        - Query: {refined_query}
        - Previous Debate Context: {debate_context}
        - Current round: {times_debate}
    """
    return prompt


def get_debate_2_prompt(point_of_fact, refined_query, cot_steps, debate_context, times_debate):
    cot_steps = json.dumps(cot_steps, indent=2, ensure_ascii=False)

    # Critical Validator
    prompt = f"""
        You are a critical evaluator.

        TASK:
        Identify weaknesses, gaps, and uncertainties in the reasoning and facts.

        REASONING STEPS (REFERENCE):
        {cot_steps}

        INSTRUCTIONS:
        1. Evaluate reasoning against the steps
        2. Identify missing information per step
        3. Detect weak or unsupported facts
        4. Highlight ambiguity and logical gaps
        5. Focus only on disagreements and unresolved issues.
        6. Do NOT restate already agreed information.

        ITERATION RULE:
        - If times_debate == 0:
            > Ignore disagreement constraint
            > Perform full role normally

        - If times_debate > 0:
            > Focus on unresolved issues from previous rounds
            > Avoid repeating already identified issues
            > Push deeper into remaining weaknesses

        OUTPUT FORMAT (STRICT):
        {{
            "weaknesses": ["...", "..."],
            "uncertainties": ["...", "..."]
        }}

        CRITICAL:
        - Output MUST be valid JSON
        - Do NOT include <think> or explanations
        - Do NOT include markdown
        - Do NOT include trailing commas
        - Do NOT include comments
        - Do NOT include explanations
        - If unsure, return the correct schema with empty values

        CONSTRAINTS:
        1. No hallucination
        2. No repetition
        3. Stay grounded in facts

        TASK INPUT:
        - Facts: {point_of_fact}
        - Query: {refined_query}
        - Previous Debate Context: {debate_context}
        - Current round: {times_debate}
    """
    return prompt


def get_debate_3_prompt(point_of_fact, refined_query, cot_steps, debate_context, times_debate):
    cot_steps = json.dumps(cot_steps, indent=2, ensure_ascii=False)

    # Structured synthesizer
    prompt = f"""
        You are a structured reasoning expert.

        TASK:
        Organize the facts into a structured and coherent perspective.

        REASONING STEPS (STRUCTURE GUIDE):
        {cot_steps}

        INSTRUCTIONS:
        1. Organize facts following reasoning steps
        2. Group facts into logical themes
        3. Highlight relationships between facts
        4. Build a structured understanding (NOT a final answer)
        5. Focus only on disagreements and unresolved issues.
        6. Do NOT restate already agreed information.

        ITERATION RULE:
        - If times_debate == 0:
            > Ignore disagreement constraint
            > Perform full role normally

        - If times_debate > 0:
            > Improve structure clarity
            > Resolve inconsistencies identified in previous rounds
            > Refine grouping and organization

        OUTPUT FORMAT (STRICT):
        {{
            "themes": ["...", "..."],
            "structured_summary": "..."
        }}

        CRITICAL:
        - Output MUST be valid JSON
        - Do NOT include <think> or explanations
        - Do NOT include markdown
        - Do NOT include trailing commas
        - Do NOT include comments
        - Do NOT include explanations
        - If unsure, return the correct schema with empty values

        CONSTRAINTS:
        1. No hallucination
        2. No repetition
        3. Do NOT directly answer the query

        TASK INPUT:
        - Facts: {point_of_fact}
        - Query: {refined_query}
        - Previous Debate Context: {debate_context}
        - Current round: {times_debate}
    """
    return prompt


def get_correlation_checker_prompt(argument_debate, refined_query):
    debator_1 = json.dumps(argument_debate["debator_1"], ensure_ascii=False)
    debator_2 = json.dumps(argument_debate["debator_2"], ensure_ascii=False)
    debator_3 = json.dumps(argument_debate["debator_3"], ensure_ascii=False)

    prompt = f"""
        You are a reasoning consistency evaluator.

        TASK:
        Analyze the outputs from multiple reasoning agents and evaluate how well they align or correlate.

        INSTRUCTIONS:
        1. Identify agreements between outputs
        2. Identify contradictions or conflicts
        3. Identify missing coverage (important aspects not addressed)
        4. Assign a correlation score (0.0 to 1.0)

        SCORING RULES:
        - 0.9-1.0 --> Strong agreement, no contradictions, good coverage
        - 0.7-0.89 --> Minor differences, mostly consistent
        - 0.5-0.69 --> Noticeable inconsistencies or gaps
        - <0.5 --> Major contradictions or poor alignment

        OUTPUT FORMAT (STRICT):
        {{
            "correlation_score": 0.0,
            "agreements": ["...", "..."],
            "contradictions": ["...", "..."],
            "gaps": ["...", "..."]
        }}

        CRITICAL:
        - Output MUST be valid JSON
        - Do NOT include <think> or explanations
        - Do NOT include markdown
        - Do NOT include trailing commas
        - Do NOT include comments
        - Do NOT include explanations
        - If unsure, return the correct schema with empty values

        CONSTRAINTS:
        1. No hallucination
        2. No repetition
        3. Be concise
        4. Use only provided outputs

        TASK INPUT:
        - Query: {refined_query}
        - Debator Outputs:
            > Debator 1: {debator_1}
            > Debator 2: {debator_2}
            > Debator 3: {debator_3}
    """
    return prompt


def get_answer_generation_prompt(refined_query, user_context, sub_questions, debate_context, correlation_result):
    user_context = json.dumps(user_context, indent=2, ensure_ascii=False)
    sub_questions = json.dumps(sub_questions, indent=2, ensure_ascii=False)

    prompt = f"""
        You are a senior reasoning expert.

        TASK:
        Generate a final answer using all available information.

        INSTRUCTIONS:
        1. Use debate arguments as primary source
        2. Incorporate sub_question insights
        3. Align with user context
        4. Resolve contradictions when possible
        5. Prioritize areas of agreement
        6. Resolve contradictions using strongest evidence
        7. Address identified gaps explicitly
        8. Answer must be in detailed explaining evidence and facts from given context

        OUTPUT FORMAT (STRICT JSON):
        {{
            "final_answer": "..."
        }}

        CRITICAL:
        - Output MUST be valid JSON
        - Do NOT include any text outside JSON
        - Do NOT include explanations
        - Do NOT include markdown
        - Do NOT include trailing commas
        - Do NOT include comments

        TASK INPUT:
        - User Context: {user_context}
        - Debate Context: {debate_context}
        - Sub_questions: {sub_questions}
        - Debate Arguments: {correlation_result}
        - Query: {refined_query}
    """
    return prompt


def get_evaluation_prompt(refined_query, answer, point_of_facts, debate_context, correlation_result):
    prompt = f"""
        You are a strict evaluation expert.

        TASK:
        Evaluate the quality of the final answer based on multiple criteria.

        METRICS TO EVALUATE:
        1. Faithfullness:
            - Does the answer strictly reflect the provided facts?
            - No hallucination or unsupported claims
        
        2. Relevance:
            - Does the answer directly address the query?

        3. Completeness:
            - Does the answer cover all important aspects of the query?

        4. Coherence:
            - Is the answer logically structured and easy to follow?

        5. Correlation:
            - Does the answer align with the majority of debator outputs?
            - Is it consistent with the correlation analysis
        
        6. Consistency:
            - Is the answer internally consistent?
            - No contradictions within the answer

        SCORING:
        Assign a score from 0.0 to 1.0 for each metric:

        - 0.9-1.0 --> Excellent
        - 0.7-0.89 --> Good
        - 0.5-0.69 --> Weak
        - <0.5 --> Poor

        OUTPUT FORMAT (STRICT):
        {{
            "faithfulness": 0.0,
            "relevance": 0.0,
            "completeness": 0.0,
            "coherence": 0.0,
            "correlation": 0.0,
            "consistency": 0.0
        }}

        CRITICAL:
        - Output MUST be valid JSON
        - Do NOT include <think> or explanations
        - Do NOT include markdown
        - Do NOT include trailing commas
        - Do NOT include comments
        - Do NOT include explanations
        - If unsure, return the correct schema with empty values

        RULES:
        1. Be strict and critical in scoring
        2. Use full score range (avoid clustering at high values)
        3. Do NOT explain scores
        4. Base evaluation only on provided inputs

        TASK INPUT:
        - Query: {refined_query}
        - Final Answer: {answer}
        - Facts: {point_of_facts}
        - Debate Context: {debate_context}
        - Correlation Analysis: {correlation_result}
    """
    return prompt



# ─────────────────────────────────────────────────────────────────────────────
# PROMPT 1 — Entity Extraction
# ─────────────────────────────────────────────────────────────────────────────
 
def get_entities_to_retrieve_prompt(bible_text: str, context_verses: list = None) -> str:
    """
    Build the entity-extraction prompt.
 
    Args:
        bible_text      : The verse being processed.
        context_verses  : List of preceding verse texts (up to 3) from the same chapter,
                          used ONLY for pronoun/subject resolution. None/empty if no context.
    """
 
    if context_verses and len(context_verses) > 0:
        context_text = " ".join(context_verses)
        context_block = f"""## PRECEDING CONTEXT
The current verse is a grammatical continuation of the text below
(one or more preceding verses that form part of the same unfinished sentence).
Use this ONLY to resolve pronouns or implicit subjects that have no referent
in the current verse. Do NOT extract nodes from this text.
 
\"\"\"{context_text}\"\"\"
 
"""
        pronoun_step = """## STEP 2 — PRONOUN RESOLUTION
Resolve ALL pronouns before extracting.
1. Look for the referent inside the CURRENT verse first.
2. Only if absent, consult the PRECEDING CONTEXT above.
 
Examples:
  cur:  "it was waste"            → "it" = earth  (referent in current verse)
  cur:  "and he rested"           → "he" absent in current verse
  ctx:  "…God ended his work…"    → "he" = God    (resolved from preceding context)
 
After resolving, extract the referent as an entity — NOT the pronoun itself.
DO NOT create nodes for pronouns."""
    else:
        context_block = ""
        pronoun_step = """## STEP 2 — PRONOUN RESOLUTION
Resolve ALL pronouns before extracting:
  "it was waste"         → "it" = earth
  "the face of the deep" → "face" refers to "deep", extract "deep"
  "Spirit of God"        → refers to God
 
DO NOT create nodes for pronouns."""
 
    prompt = f"""You are a Biblical Knowledge Graph node extraction engine.
 
{context_block}## TASK
Extract all meaningful semantic nodes from the CURRENT Bible verse.
For each entity, also extract IMMUTABLE properties directly stated in the verse.
 
## CORE PRINCIPLES
1. Extract ONLY from the CURRENT verse — preceding context is for pronoun
   resolution only, never a source of new nodes.
2. Extract EXPLICITLY STATED and STRONGLY IMPLIED entities.
3. Do NOT extract verbs, actions, or relationships.
4. Prioritize PROPER NOUNS over generic descriptions.
5. Use MOST SPECIFIC TYPE available.
6. Attach IMMUTABLE properties only when directly inferable from the current verse.
 
## STEP 1 — IDENTIFY NOUN PHRASES
List every noun, proper noun, and noun phrase in the CURRENT verse:
- People, places, things explicitly named
- Collective nouns (people, group, assembly)
- Pronouns → resolve to their referent (see Step 2), then extract the referent
- Compound descriptions ("Spirit of God", "face of the waters")
 
{pronoun_step}
 
## STEP 3 — CANONICALIZE NAMES
Use the PROPER NOUN or PRIMARY NAME:
  "Spirit of God"    → "God"
  "face of waters"   → "waters"
  "people of Israel" → "Israel"
  "Mount Sinai"      → "Mount Sinai"    (fixed name, keep as-is)
  "Garden of Eden"   → "Garden of Eden" (fixed name, keep as-is)
  "seventh day"      → "seventh day"    (fixed concept, keep as-is)
 
## STEP 4 — IMPLICIT ENTITIES
Extract implied entities ONLY if:
(a) Clearly referred to in the CURRENT verse,
(b) Essential to understanding the verse, and
(c) Not speculative.
 
  "Spirit of God moving" → extract "God"
  "face of the waters"   → extract "waters"
  "Let there be light"   → extract "light"
 
If a pronoun in the current verse was resolved via the previous verse context,
extract that resolved entity — but ONLY because it is referenced here.
 
## STEP 5 — TYPE ASSIGNMENT
Select the MOST SPECIFIC type. Priority: named role > generic (Prophet > Person),
specific location > generic (City > Place).
 
DIVINE & SPIRITUAL
  DivineEntity     — God, Yahweh, the Almighty, the Lord, Jesus, Christ, Messiah
  Angel            — Gabriel, Michael, Raphael, Uriel, heavenly beings
  DemonOrEvil      — Satan, demons, evil spirits, Lucifer, adversaries
  SpiritualEntity  — spirits, ghosts, shades, apparitions
  SpiritualConcept — faith, grace, mercy, redemption, blessing, curse, salvation
 
PERSONS (by role/status)
  King             — rulers, pharaohs, caesars (David, Solomon, Herod, Pharaoh)
  Queen            — queens, queen mothers (Esther, Bathsheba, Jezebel)
  Priest           — priests, high priests, levites (Aaron, Caiaphas)
  Prophet          — prophets, seers (Moses, Elijah, Isaiah, Jeremiah, John Baptist)
  Apostle          — apostles, disciples (Peter, Paul, James, John)
  Patriarch        — patriarchs (Abraham, Isaac, Jacob, Moses, David, Solomon)
  Matriarch        — matriarchs, significant women (Sarah, Rachel, Eve, Mary)
  Person           — named individuals without specific role
 
GROUPS & NATIONS
  Group            — peoples, nations, tribes, families, assemblies, congregations,
                     councils, synagogues, churches
 
LOCATIONS
  City             — Jerusalem, Bethlehem, Damascus, Rome, Ephesus, Nineveh
  Region           — Judea, Galilee, Egypt, Babylon, Canaan, Assyria
  NamedLocation    — Mount Sinai, Jordan River, Red Sea, Garden of Eden
  Place            — generic/unnamed locations (wilderness, field, valley)
 
BUILDINGS & STRUCTURES
  Temple           — Temple of Solomon, Tabernacle, Sanctuary
  Building         — houses, palaces, fortresses, altars, tombs, caves
 
NATURAL PHENOMENA & CELESTIAL
  NaturalPhenomenon — earth, sky, water, light, darkness, fire, wind, deep, abyss
  CelestialBody    — sun, moon, stars, constellations, planets
 
LIVING CREATURES
  Animal           — lions, bears, wolves, sheep, serpents, cattle, domestic creatures
  Plant            — trees, grass, herbs, vegetation, grain, wheat, barley
 
MATERIAL & PHYSICAL
  Artifact         — vessels, weapons, scrolls, religious objects, tools, furniture
  Material         — gold, silver, bronze, wood, stone, clay, iron
  Food             — bread, fruit, wine, grain, manna, meat, honey
 
TEMPORAL & EVENTS
  TimeConcept      — day, night, week, year, sabbath, generation, season, festival
  Event            — exodus, flood, resurrection, persecution, crucifixion, war
  Miracle          — miracles, signs, wonders, marvels, portents
  Disease          — leprosy, plague, sickness, blindness, affliction
 
ABSTRACT & SPIRITUAL CONCEPTS
  Covenant         — covenant, agreement, oath, promise
  Law              — law, commandment, statute, ordinance, Torah
  AbstractConcept  — word, truth, wisdom, knowledge, understanding, doctrine
  Prophecy         — prophecy, vision, revelation, future events
 
## STEP 6 — IMMUTABLE PROPERTIES
Attach ONLY stable facts directly stated in the CURRENT verse.
 
String properties:
  gender      : "male" | "female"
  origin      : birthplace or homeland ("Bethlehem", "Egypt")
  entity_type : sub-classification ("planet", "abyss", "river", "city")
  material    : physical composition ("gold", "stone", "wood")
  known_as    : alternative canonical name in the verse
 
Numeric properties (JSON numbers, NOT strings):
  age            : integer — "Abraham was 100 years old" → 100
  age_at_death   : integer — "died at 175"               → 175
  quantity       : integer — "twelve sons"               → 12
  length_cubits  : float   — "300 cubits long"           → 300
  width_cubits   : float   — "50 cubits wide"            → 50
  height_cubits  : float   — "30 cubits high"            → 30
  weight_shekels : float   — "20 shekels"                → 20
  weight_talents : float   — weight in talents
  capacity_baths : float   — liquid capacity in baths
  capacity_ephahs: float   — dry capacity in ephahs
  count          : integer — "seven times"               → 7
 
Rules:
  ✅ Numbers must be JSON numbers: age: 100, NOT age: "100"
  ✅ Attach numeric to the correct entity ("300 cubits" → ark, not Noah)
  ✅ Use unit in the key (length_cubits, not length: "300 cubits")
  ❌ Do NOT convert units, do NOT infer numbers not in the verse
 
Do NOT include mutable properties (state, role, title, status, location, emotion).
If no immutable properties → omit "properties" field entirely.
 
## STEP 7 — VALIDATE
✅ Include: explicitly named in current verse, proper nouns, major natural elements,
            biblical concepts, pronouns resolved to their referent
❌ Exclude: verbs, vague descriptors ("waste" alone), duplicates, speculation,
            entities that appear only in the previous verse and are NOT referenced here
 
## EXAMPLES
 
Genesis 1:1 — "At the first God made the heaven and the earth."
[
  {{"type": "DivineEntity",      "name": "God"}},
  {{"type": "NaturalPhenomenon", "name": "heaven", "properties": {{"entity_type": "sky"}}}},
  {{"type": "NaturalPhenomenon", "name": "earth",  "properties": {{"entity_type": "planet"}}}}
]
 
Genesis 1:14 — "And God said, Let there be lights in the firmament of the heavens to divide the day from the night; and let them be for signs, and for seasons, and for days, and years."
[
  {{"type": "DivineEntity",      "name": "God"}},
  {{"type": "CelestialBody",     "name": "lights"}},
  {{"type": "NaturalPhenomenon", "name": "firmament"}},
  {{"type": "NaturalPhenomenon", "name": "day"}},
  {{"type": "NaturalPhenomenon", "name": "night"}}
]
 
1 Kings 1:11 — "And David was king over Israel, and he did that which was right in the eyes of the Lord."
[
  {{"type": "King",         "name": "David",   "properties": {{"gender": "male"}}}},
  {{"type": "DivineEntity", "name": "God"}},
  {{"type": "Group",        "name": "Israel"}}
]
 
Genesis 37:5 — "And Joseph dreamed a dream, and he told it his brethren: and they hated him yet the more."
[
  {{"type": "Person", "name": "Joseph",   "properties": {{"gender": "male"}}}},
  {{"type": "Event",  "name": "dream"}}
]
 
Leviticus 13:2 — "When a man shall have in the skin of his flesh a rising, a scab, or a bright spot, and it be in the skin of his flesh like the plague of leprosy; then he shall be brought unto the priest."
[
  {{"type": "Person",  "name": "man"}},
  {{"type": "Disease", "name": "leprosy"}},
  {{"type": "Priest",  "name": "priest"}}
]
 
1 Samuel 3:7 — "Now Samuel did not yet know the Lord, neither was the word of the Lord yet revealed unto him."
[
  {{"type": "Prophet",      "name": "Samuel", "properties": {{"gender": "male"}}}},
  {{"type": "DivineEntity", "name": "God"}},
  {{"type": "AbstractConcept", "name": "word"}}
]
 
Psalm 19:1 — "The heavens declare the glory of God; and the firmament sheweth his handywork."
[
  {{"type": "NaturalPhenomenon", "name": "heavens"}},
  {{"type": "DivineEntity",      "name": "God"}},
  {{"type": "SpiritualConcept",  "name": "glory"}}
]
 
Matthew 4:4 — "But he answered and said, It is written, Man shall not live by bread alone, but by every word that proceedeth out of the mouth of God."
[
  {{"type": "Person",             "name": "Man"}},
  {{"type": "Food",               "name": "bread"}},
  {{"type": "AbstractConcept",    "name": "word"}},
  {{"type": "DivineEntity",       "name": "God"}}
]
 
John 11:25 — "Jesus said unto her, I am the resurrection, and the life: he that believeth in me, though he were dead, yet shall he live."
[
  {{"type": "DivineEntity",      "name": "Jesus"}},
  {{"type": "Miracle",           "name": "resurrection"}},
  {{"type": "SpiritualConcept",  "name": "life"}},
  {{"type": "SpiritualConcept",  "name": "faith"}}
]
 
BAD ENTITIES:
  ❌ {{"type": "Action",       "name": "producing"}}        — verb
  ❌ {{"type": "Entity",       "name": "the light"}}        — has article
  ❌ {{"type": "DivineEntity", "name": "Spirit of God"}}    — canonicalize to "God"
  ❌ {{"type": "Place",        "name": "face"}}             — descriptor only
  ❌ {{"properties": {{"age": "175"}}}}                      — must be number, not string
  ❌ entity from previous verse not referenced in current   — out of scope
 
## OUTPUT FORMAT
[
  {{"type": "TYPE", "name": "EntityName"}},
  {{"type": "TYPE", "name": "EntityName", "properties": {{"entity_type": "planet", "age": 100}}}}
]
 
Rules:
- Valid JSON array only
- Each object MUST have "type" and "name"
- "properties" is optional — immutable facts only
- Numeric values are JSON numbers, string values are plain strings
- Names exclude articles ("the", "a")
- No explanations, markdown, or extra text
- If no entities → return []
 
## BIBLE VERSE
{bible_text}
 
Now extract all entities with their immutable properties:"""
    return prompt
 
 
# ─────────────────────────────────────────────────────────────────────────────
# PROMPT 2 — Relationship Extraction
# ─────────────────────────────────────────────────────────────────────────────
 
def get_relationship_extraction_prompt(
    bible_text: str,
    entities: list,
    context_verses: list = None,
) -> str:
    """
    Build the relationship-extraction prompt.
 
    Args:
        bible_text      : The verse being processed.
        entities        : Entity list already extracted for this verse.
        context_verses  : List of preceding verse texts (up to 3) from the same chapter,
                          used ONLY for pronoun/subject resolution. None/empty if no context.
    """
    entities_json    = json.dumps(entities, indent=2, ensure_ascii=False)
    entity_names     = [e["name"] for e in entities]
    entity_names_str = ", ".join(f'"{n}"' for n in entity_names)
 
    if context_verses and len(context_verses) > 0:
        context_text = " ".join(context_verses)
        context_block = f"""## PRECEDING CONTEXT
The current verse is a grammatical continuation of the text below
(one or more preceding verses that form part of the same unfinished sentence).
Use this ONLY to resolve pronouns or implicit subjects that have no referent
in the current verse. Extract relationships ONLY from the current verse.
 
\"\"\"{context_text}\"\"\"
 
"""
        pronoun_step = """## STEP 1 — PRONOUN & SUBJECT RESOLUTION (do this first)
Resolve ALL pronouns and implicit subjects before extracting.
1. Look for the referent inside the CURRENT verse first.
2. Only if absent, consult the PRECEDING CONTEXT above.
 
Examples:
  cur:  "it was waste"              → "it" = earth  (in current verse)
  cur:  "and he rested on that day" → "he" absent in current verse
  ctx:  "…God ended his work…"      → "he" = God    (from preceding context)
 
After resolution, the resolved name must exist in the entity list.
If it does not, skip the relationship — do not invent sources or targets."""
    else:
        context_block = ""
        pronoun_step = """## STEP 1 — PRONOUN & SUBJECT RESOLUTION (do this first)
Resolve ALL pronouns and implicit subjects before extracting:
  "it was waste"             → "it" = earth
  "he rested"                → "he" = God (nearest explicit subject in verse)
  "Spirit of God was moving" → subject = God
 
After resolution, the resolved name must exist in the entity list.
If it does not, skip the relationship."""
 
    prompt = f"""You are a Biblical Knowledge Graph relationship extraction engine.
 
{context_block}## PRIMARY GOAL
Extract ALL meaningful relationships from the CURRENT verse in a single output array.
All sources and targets must come from the entity list below.
 
Two types of relationships:
  TYPE A — entity → entity  :  God -[CREATED]-> earth
  TYPE B — entity → value   :  earth -[HAS_STATE]-> "formless"
 
Numeric qualifiers attach as properties ON relationships, never as targets.
 
{pronoun_step}
 
## STEP 2 — ENTITY MATCHING
Every source and target in TYPE A MUST come from: [{entity_names_str}]
 
Match by intent, not exact string:
  "the Spirit of God" → "God"
  "the people"        → "Israel"
  "the light"         → "light"
 
## STEP 3 — TYPE A: DIRECT ENTITY RELATIONSHIPS
Extract relationships between two entities from the list above.
 
Type naming rules:
- UPPERCASE_SNAKE_CASE, derived from verse verbs
- Prefer active voice (God -[CREATED]-> earth, not earth -[WAS_CREATED_BY]-> God)
- Avoid: RELATED_TO, CONNECTED_TO, ASSOCIATED_WITH
 
Core relationship categories:
  Creation/Formation : CREATED, FORMED, MADE, ESTABLISHED, SHAPED, FASHIONED, BEGOT
  Speech/Command     : SPOKE_TO, SAID_TO, COMMANDED, DECLARED, WARNED, PROMISED, CALLED
  Divine Perception  : SAW, LOOKED_UPON, OBSERVED, BEHELD, WITNESSED
  Divine Action      : BLESSED, ANOINTED, CHOSE, REVEALED_TO, JUDGED, SUSTAINED
  Movement           : WENT_TO, CAME_TO, RETURNED_TO, ASCENDED_TO, MOVED_OVER, FLED_TO
  Location/Existence : DWELT_IN, LIVED_IN, LOCATED_IN, SETTLED_IN, EXISTED_IN
  Physical Action    : BUILT, DESTROYED, HEALED, KILLED, RESCUED, DELIVERED, SEPARATED, DIVIDED
  Spiritual          : WORSHIPPED, PRAYED_TO, FOLLOWED, OBEYED, FEARED, TRUSTED, SERVED
  Authority          : RULED, LED, APPOINTED, CROWNED, GOVERNED, REIGNED_OVER
  Family/Social      : MARRIED, BECAME_FATHER_OF, BECAME_MOTHER_OF, TAUGHT, DISCIPLED, BORE
  Conflict           : DEFEATED, CONQUERED, WARRED_WITH, DELIVERED_FROM
  
Additional relationship types may appear in biblical text and should be named
appropriately based on the verb's semantic meaning (e.g., BETRAYED, PERSECUTED,
RESURRECTED, ASCENDED, REDEEMED, SANCTIFIED, etc.).
 
Numeric properties on relationships (values MUST be JSON numbers):
  duration_days   : integer — "for 40 days"
  duration_years  : integer — "for 40 years"
  duration_months : integer — "for 6 months"
  duration_hours  : integer — "for 3 hours"
  count           : integer — "seven times"
  quantity        : integer — "twelve loaves"
  distance_cubits : float   — "2000 cubits"
  distance_stadia : float   — "15 stadia"
  weight_shekels  : float   — "thirty shekels"
  weight_talents  : float   — "100 talents"
  amount          : float   — generic if no unit fits
 
  ✅ Unit in key name: duration_years: 40, NOT duration: "40 years"
  ❌ Do NOT use numbers as targets; do NOT infer numbers not in the verse
 
## STEP 4 — TYPE B: ATTRIBUTE RELATIONSHIPS
For mutable contextual facts where the target is a short value string.
 
Basic types (most common):
  HAS_STATE    → "[entity] was/is [condition]"
                 earth was waste   → earth -[HAS_STATE]-> "waste"
                 light was good    → light -[HAS_STATE]-> "good"
 
  HAS_ROLE     → "[entity] acted as [role]"
                 God made earth    → God   -[HAS_ROLE]->  "creator"
                 Moses led Israel  → Moses -[HAS_ROLE]->  "leader"
 
  HAS_TITLE    → "[entity] is called/named [title]"
                 light called Day  → light -[HAS_TITLE]-> "Day"
 
  HAS_STATUS   → temporal status: appointed, crowned, exiled, healed, etc.
                 Saul was anointed → Saul  -[HAS_STATUS]-> "anointed"
 
  HAS_LOCATION → entity at a place NOT already in the entity list
 
  HAS_EMOTION  → "[entity] felt [emotion]"
                 Abraham feared    → Abraham -[HAS_EMOTION]-> "fear"
 
Extended types for biblical contexts:
  Spiritual/Divine   : HAS_FAITH, HAS_GRACE, HAS_BLESSING, HAS_CURSE, HAS_RIGHTEOUSNESS,
                       HAS_HOLINESS, HAS_SIN, HAS_SALVATION, HAS_COVENANT, HAS_PROMISE
  Emotional          : HAS_JOY, HAS_SORROW, HAS_FEAR, HAS_LOVE, HAS_MERCY, HAS_ANGER,
                       HAS_HOPE, HAS_PEACE, HAS_SHAME, HAS_PRIDE, HAS_HUMILITY
  Moral/Ethical      : HAS_VIRTUE, HAS_VICE, HAS_JUSTICE, HAS_OBEDIENCE, HAS_LOYALTY,
                       HAS_TRUTH, HAS_HONESTY, HAS_DECEIT
  Physical Attributes: HAS_STRENGTH, HAS_BEAUTY, HAS_AGE, HAS_APPEARANCE, HAS_FORM,
                       HAS_HEALTH, HAS_SICKNESS, HAS_VIGOR, HAS_WEAKNESS
  Power & Authority  : HAS_POWER, HAS_AUTHORITY, HAS_DOMINION, HAS_THRONE, HAS_CROWN
  Possession         : HAS_WEALTH, HAS_RICHES, HAS_PROPERTY, HAS_TREASURE, HAS_INHERITANCE
  Events & Actions   : HAS_VICTORY, HAS_DEFEAT, HAS_CAPTIVITY, HAS_FREEDOM, HAS_EXILE,
                       HAS_SUFFERING, HAS_JUDGMENT, HAS_REWARD, HAS_PUNISHMENT
  Knowledge          : HAS_KNOWLEDGE, HAS_WISDOM, HAS_UNDERSTANDING, HAS_IGNORANCE,
                       HAS_VISION, HAS_PROPHECY, HAS_REVELATION
  Worship & Practice : HAS_WORSHIP, HAS_PRAYER, HAS_PRAISE, HAS_SONG, HAS_OFFERING,
                       HAS_SACRIFICE, HAS_RITUAL, HAS_FASTING, HAS_CELEBRATION
  Transformation     : HAS_RESURRECTION, HAS_ASCENSION, HAS_RENEWAL, HAS_RESTORATION
 
Target value rules: 1–3 words, lowercase, no articles.
If the target is already an entity in the list → use TYPE A instead.
Do NOT use TYPE B for numeric values.
 
## STEP 5 — MULTI-CLAUSE PROCESSING
For clauses separated by ";", "and", "but", ":":
- Process each clause independently
- Implicit subject carries over from the previous clause in the CURRENT verse
- Only fall back to the previous verse context if the subject is absent
  from the entire current verse
 
## CONFIDENCE THRESHOLD
≥ 90% → include | 70–89% → include with simpler type | < 70% → omit
 
## EXAMPLES
 
Genesis 1:1 — "At the first God made the heaven and the earth."
Entities: ["God", "heaven", "earth"]
[
  {{"source": "God", "relationship": "MADE",     "target": "heaven"}},
  {{"source": "God", "relationship": "MADE",     "target": "earth"}},
  {{"source": "God", "relationship": "HAS_ROLE", "target": "creator"}}
]
 
Genesis 1:2 — "And the earth was waste and without form; and it was dark on the face of the deep: and the Spirit of God was moving on the face of the waters."
Entities: ["earth", "deep", "waters", "God"]
[
  {{"source": "earth", "relationship": "HAS_STATE",   "target": "waste"}},
  {{"source": "earth", "relationship": "HAS_STATE",   "target": "formless"}},
  {{"source": "earth", "relationship": "HAS_STATE",   "target": "dark"}},
  {{"source": "earth", "relationship": "WAS_DARK_ON", "target": "deep"}},
  {{"source": "God",   "relationship": "MOVED_OVER",  "target": "waters"}},
  {{"source": "God",   "relationship": "HAS_ROLE",    "target": "sustainer"}}
]
 
Genesis 2:3 with PREVIOUS VERSE CONTEXT "And on the seventh day God ended his work which he had made;"
Current verse: "and he rested on the seventh day from all his work."
Entities: ["God", "seventh day"]   ← "he" resolved to God via previous verse
[
  {{"source": "God", "relationship": "RESTED_ON",  "target": "seventh day"}},
  {{"source": "God", "relationship": "HAS_STATUS", "target": "rested"}}
]
 
Numbers 14:33 — "Your children shall be wanderers in the wilderness forty years."
Entities: ["children", "wilderness"]
[
  {{"source": "children", "relationship": "WANDERED_IN", "target": "wilderness", "properties": {{"duration_years": 40}}}}
]
 
Genesis 1:4 — "God, looking on the light, saw that it was good: and God made a division between the light and the dark."
Entities: ["God", "light", "dark"]
[
  {{"source": "God",   "relationship": "LOOKED_UPON",    "target": "light"}},
  {{"source": "God",   "relationship": "SAW",            "target": "light"}},
  {{"source": "light", "relationship": "HAS_STATE",      "target": "good"}},
  {{"source": "God",   "relationship": "SEPARATED",      "target": "light"}},
  {{"source": "light", "relationship": "SEPARATED_FROM", "target": "dark"}}
]
 
1 Samuel 16:13 — "Then Samuel took the horn of oil, and anointed him in the midst of his brethren: and the Spirit of the Lord came upon David from that day forward."
Entities: ["Samuel", "Prophet", "David", "king", "Spirit"]
[
  {{"source": "Samuel", "relationship": "ANOINTED",     "target": "David"}},
  {{"source": "David",  "relationship": "HAS_STATUS",   "target": "anointed"}},
  {{"source": "Spirit", "relationship": "CAME_UPON",    "target": "David"}},
  {{"source": "David",  "relationship": "HAS_ROLE",     "target": "king"}}
]
 
Exodus 12:37 — "And the children of Israel journeyed from Ramesses to Succoth, about six hundred thousand on foot that were men, beside children."
Entities: ["Israel", "Ramesses", "Succoth", "men", "children"]
[
  {{"source": "Israel", "relationship": "JOURNEYED_FROM", "target": "Ramesses"}},
  {{"source": "Israel", "relationship": "JOURNEYED_TO",   "target": "Succoth"}},
  {{"source": "Israel", "relationship": "CONSISTED_OF",   "target": "men", "properties": {{"quantity": 600000}}}}
]
 
Matthew 27:11 — "And Jesus stood before the governor: and the governor asked him, saying, Art thou the King of the Jews?"
Entities: ["Jesus", "governor", "Jews"]
[
  {{"source": "Jesus", "relationship": "HAS_TITLE",     "target": "King of the Jews"}},
  {{"source": "Jesus", "relationship": "QUESTIONED_BY", "target": "governor"}},
  {{"source": "Jesus", "relationship": "HAS_ROLE",      "target": "king"}}
]
 
John 11:43-44 — "And when he thus had spoken, he cried with a loud voice, Lazarus, come forth. And he that was dead came forth, bound hand and foot with graveclothes."
Entities: ["Jesus", "Lazarus", "dead", "graveclothes"]
[
  {{"source": "Jesus",   "relationship": "COMMANDED",      "target": "Lazarus"}},
  {{"source": "Lazarus", "relationship": "HAS_STATUS",     "target": "raised"}},
  {{"source": "Lazarus", "relationship": "CAME_FORTH",     "target": "tomb"}},
  {{"source": "Lazarus", "relationship": "HAS_STATE",      "target": "alive"}}
]
 
## OUTPUT FORMAT
[
  {{"source": "EntityName", "relationship": "TYPE",      "target": "EntityName"}},
  {{"source": "EntityName", "relationship": "HAS_STATE", "target": "value"}},
  {{"source": "EntityName", "relationship": "TYPE",      "target": "EntityName", "properties": {{"duration_years": 40}}}}
]
 
Rules:
- Valid JSON array only
- Each object MUST have: source, relationship, target
- "properties" is optional — numeric qualifiers only, values are JSON numbers
- TYPE A: both source and target are entity names from the list
- TYPE B: source is entity name, target is a short lowercase value string
- No self-relationships, no explanations, no markdown
- If no relationships → return []
 
## FINAL CHECKLIST
☐ All pronouns resolved (current verse first; previous verse context only as fallback)
☐ Each clause in the current verse processed
☐ TYPE A: source and target are entity names from the list
☐ TYPE B: target is a short value string, not an entity name
☐ Numeric values are JSON numbers, not strings
☐ No self-relationships
☐ Output is valid JSON
 
## BIBLE VERSE
{bible_text}
 
## ENTITIES
{entities_json}
 
Now extract all relationships. Resolve pronouns FIRST, then process clause by clause."""
    return prompt

# src/utils/prompt_templates_v2.py

def get_text_to_cypher_system_prompt() -> str:
    """
    Strict JSON-only Text-to-Cypher system prompt optimized for knowledge graph retrieval.
    Includes fuzzy CONTAINS matching to handle mixed-case and partial node names.
    """
    return """
You are an expert Neo4j Cypher query generator specialized in knowledge graph traversal.
Your task is to translate a natural-language question into a SINGLE,
syntactically valid Cypher query using ONLY the provided graph schema,
optimized to return rich graph structures (nodes + relationships).

==================================================
CRITICAL OUTPUT RULES
==================================================
You MUST return ONLY valid JSON.
The response MUST:
- Use DOUBLE QUOTES only
- Be valid JSON parsable by Python json.loads()
- Contain NO markdown
- Contain NO explanations
- Contain NO comments
- Contain NO extra text
- Contain NO code fences
- Contain NO backticks

==================================================
REQUIRED JSON FORMAT
==================================================
Return EXACTLY this structure:
{
  "cypher": "<your cypher query here>",
  "return_type": "graph",
  "params": {"key": "value"}
}

If no parameters are needed, omit the "params" key:
{
  "cypher": "<your cypher query here>",
  "return_type": "graph"
}

If the schema does not support the question:
{
  "cypher": "UNSUPPORTED_QUERY",
  "return_type": "none"
}

==================================================
STRICT SCHEMA RULES
==================================================
- Use ONLY node labels defined in the schema
- Use ONLY relationship types defined in the schema
- Use ONLY properties defined in the schema
- NEVER invent labels, properties, or relationships
- If a question cannot be answered using the schema, return UNSUPPORTED_QUERY

==================================================
FUZZY MATCHING RULES  ← CRITICAL
==================================================
Node names in the graph use MIXED CASE and PARTIAL phrases.
Examples of real node names:
  "Tomato", "tomato plant", "Tomato leaves", "tomato yellow leaf curl virus"

NEVER use exact match for user-provided entity names:
  BAD:  MATCH (n:Plant {name: $name})
  BAD:  WHERE n.name = $name

ALWAYS use case-insensitive CONTAINS:
  GOOD: WHERE toLower(n.name) CONTAINS toLower($name)

For multi-keyword queries, extract each keyword and match with OR:
  WHERE toLower(n.name) CONTAINS toLower($kw1)
     OR toLower(n.name) CONTAINS toLower($kw2)

When entity type is unclear, search across ALL relevant labels:
  MATCH (n)
  WHERE (n:Plant OR n:Disease OR n:Symptom OR n:Pest OR n:Risk)
    AND (toLower(n.name) CONTAINS toLower($kw1)
      OR toLower(n.name) CONTAINS toLower($kw2))

Use OPTIONAL MATCH to fetch neighbors without losing anchor nodes:
  MATCH (n)
  WHERE (n:Plant OR n:Disease OR n:Symptom)
    AND toLower(n.name) CONTAINS toLower($name)
  OPTIONAL MATCH (n)-[r]-(neighbor)
  RETURN n, collect(r) AS rels, collect(neighbor) AS neighbors
  LIMIT 50

==================================================
KEYWORD EXTRACTION RULES
==================================================
Extract only DOMAIN-RELEVANT keywords from the user question.
Ignore filler words: my, the, a, look, seem, is, are, so, very, it

Examples:
  "my tomato look sick, the leaf look so yellow"
    → keywords: tomato, leaf, yellow
    → params:   {"kw1": "tomato", "kw2": "yellow", "kw3": "leaf"}

  "yellow leaf on tomato plant"
    → keywords: yellow, leaf, tomato
    → params:   {"kw1": "yellow", "kw2": "leaf", "kw3": "tomato"}

  "what disease causes wilting"
    → keywords: disease, wilting
    → params:   {"kw1": "wilting"}

Use the most specific keyword as the primary filter ($kw1),
and broaden with OR for secondary keywords.

==================================================
KNOWLEDGE GRAPH RETURN RULES
==================================================
The goal is to return a subgraph, not a flat table.
Always return BOTH nodes AND relationships.

PREFERRED return patterns:

1. Anchor node + neighborhood (RECOMMENDED for symptom/disease queries):
   MATCH (n)
   WHERE (n:Plant OR n:Disease OR n:Symptom)
     AND toLower(n.name) CONTAINS toLower($name)
   OPTIONAL MATCH (n)-[r]-(neighbor)
   RETURN n, collect(r) AS rels, collect(neighbor) AS neighbors
   LIMIT 50

2. Multi-hop path traversal:
   MATCH path = (n)-[*1..2]-(m)
   WHERE toLower(n.name) CONTAINS toLower($name)
   RETURN nodes(path) AS nodes, relationships(path) AS rels
   LIMIT 50

3. Multi-keyword OR search across labels:
   MATCH (n)
   WHERE (n:Plant OR n:Disease OR n:Symptom OR n:Pest)
     AND (toLower(n.name) CONTAINS toLower($kw1)
       OR toLower(n.name) CONTAINS toLower($kw2))
   OPTIONAL MATCH (n)-[r]-(neighbor)
   RETURN n, collect(r) AS rels, collect(neighbor) AS neighbors
   LIMIT 50

RULES for graph return:
- ALWAYS declare relationship/neighbor variables with OPTIONAL MATCH BEFORE using them in RETURN
- NEVER use collect(r) or collect(m) without first writing: OPTIONAL MATCH (n)-[r]-(m)
- Always return node objects, never only n.property
- Use OPTIONAL MATCH (n)-[r]-(m) so anchor nodes return even with no relationships
- Use collect(r) and collect(m) for compact graph output ONLY after OPTIONAL MATCH binds r and m
- Use LIMIT 50 by default
- Prefer direction-agnostic patterns -[r]- when direction is unknown

MANDATORY pattern — always write OPTIONAL MATCH before RETURN:
  MATCH (n)
  WHERE (n:Plant OR n:Disease OR n:Symptom)
    AND toLower(n.name) CONTAINS toLower($name)
  OPTIONAL MATCH (n)-[r]-(m)
  RETURN n, collect(r) AS rels, collect(m) AS neighbors
  LIMIT 50

==================================================
READ-ONLY CYPHER RULES
==================================================
Allowed clauses ONLY:
  MATCH, OPTIONAL MATCH, WHERE, WITH,
  RETURN, ORDER BY, LIMIT, UNWIND,
  nodes(), relationships(), labels(), type(),
  collect(), count(), size(), keys(), toLower(), toString()

NEVER use:
  CREATE, DELETE, MERGE, SET,
  REMOVE, DROP, CALL (write procedures)

==================================================
PARAMETER USAGE
==================================================
Use $param for ALL dynamic values extracted from the question.
ALWAYS pair with toLower() CONTAINS — never with = (equals).

Standard pattern:
  MATCH (n)
  WHERE (n:Plant OR n:Disease OR n:Symptom OR n:Pest OR n:Risk)
    AND toLower(n.name) CONTAINS toLower($name)
  OPTIONAL MATCH (n)-[r]-(neighbor)
  RETURN n, collect(r) AS rels, collect(neighbor) AS neighbors
  LIMIT 50

With params in JSON:
{
  "cypher": "MATCH (n) WHERE (n:Plant OR n:Disease OR n:Symptom) AND toLower(n.name) CONTAINS toLower($name) OPTIONAL MATCH (n)-[r]-(neighbor) RETURN n, collect(r) AS rels, collect(neighbor) AS neighbors LIMIT 50",
  "return_type": "graph",
  "params": {"name": "yellow leaf"}
}

==================================================
DECISION LOGIC
==================================================
Follow this order when building the query:

1. Is the question answerable with the schema?
   NO  → return UNSUPPORTED_QUERY

2. Extract domain keywords from the question (ignore filler words).
   No domain keywords found → return UNSUPPORTED_QUERY

3. Does the question ask for a specific scalar (count, single value)?
   YES → return that scalar + the anchor node for graph context
   NO  → return full node + relationship objects

4. How many keywords?
   ONE keyword  → single CONTAINS filter on relevant labels
   MULTI keyword → OR across keywords on relevant labels

5. Does traversal go beyond 1 hop?
   YES → use OPTIONAL MATCH (n)-[r]-(neighbor) or path = (*1..2)
   NO  → use simple OPTIONAL MATCH (n)-[r]-(m)

==================================================
INVALID vs VALID EXAMPLES
==================================================
INVALID (never do this):
  {"cypher": "MATCH (n:Plant {name: $name}) RETURN n, collect(r) AS rels ..."}
  Reason: exact match AND r is not defined — missing OPTIONAL MATCH (n)-[r]-(m)

  {"cypher": "MATCH (n) WHERE n.name = $name RETURN n, collect(r) AS rels, collect(m) AS neighbors"}
  Reason: r and m are NOT defined — you MUST write OPTIONAL MATCH (n)-[r]-(m) before RETURN

  {'cypher': 'MATCH (n) RETURN n'}
  Reason: single quotes — not valid JSON

VALID (always write OPTIONAL MATCH before RETURN):
  {
    "cypher": "MATCH (n) WHERE (n:Plant OR n:Disease OR n:Symptom) AND toLower(n.name) CONTAINS toLower($name) OPTIONAL MATCH (n)-[r]-(m) RETURN n, collect(r) AS rels, collect(m) AS neighbors LIMIT 50",
    "return_type": "graph",
    "params": {"name": "tomato"}
  }

  {
    "cypher": "MATCH (n) WHERE (n:Plant OR n:Disease OR n:Symptom OR n:Pest) AND (toLower(n.name) CONTAINS toLower($kw1) OR toLower(n.name) CONTAINS toLower($kw2)) OPTIONAL MATCH (n)-[r]-(m) RETURN n, collect(r) AS rels, collect(m) AS neighbors LIMIT 50",
    "return_type": "graph",
    "params": {"kw1": "yellow", "kw2": "leaf"}
  }

==================================================
FINAL REMINDER
==================================================
Your response MUST always be valid JSON with double quotes.
ALWAYS use toLower(n.name) CONTAINS toLower($param) — NEVER exact match.
Return nodes AND relationships — not just properties.
When unsure of the label, search across Plant, Disease, Symptom, Pest, Risk.
"""