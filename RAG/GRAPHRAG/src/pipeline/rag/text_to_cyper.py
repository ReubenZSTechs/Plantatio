"""
text_to_cypher.py
=================
Text-to-Cypher pipeline: accepts natural-language input, converts it
into a Cypher query via LLM, executes against Neo4j, and returns JSON.

Supports the enhanced prompt format that returns:
  {
    "cypher": "...",
    "return_type": "graph" | "scalar" | "none",
    "params": { ... }          ← optional
  }
"""

import ast
import json
import logging
import re
import time
import traceback
from datetime import datetime
from typing import Any, Optional

from src.pipeline.rag.connect_to_neo4j import Neo4jHandler
from src.models.LLM.v2_LLM import LLMManager
from src.utils.prompt_templates_v2 import get_text_to_cypher_system_prompt


# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

UNSUPPORTED_QUERY = "UNSUPPORTED_QUERY"

VALID_RETURN_TYPES = {"graph", "scalar", "none"}

# Default LIMIT injected when the LLM omits one (graph queries only)
DEFAULT_GRAPH_LIMIT = 50


# ─────────────────────────────────────────────────────────────────────────────
# TEXT-TO-CYPHER PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

class TextToCypherPipeline:
    """
    End-to-end pipeline:
      Natural Language -> Cypher (via LLM) -> Neo4j -> JSON results

    The LLM is expected to return JSON with the shape:
      {
        "cypher":       "<Cypher query>",
        "return_type":  "graph" | "scalar" | "none",
        "params":       { ... }          # optional
      }
    """

    def __init__(self):
        self.llm = LLMManager()

        self.handler = Neo4jHandler()
        self.handler.connect()

        self._schema_cache: Optional[str] = None

    # ─────────────────────────────────────────────────────────────
    # SCHEMA
    # ─────────────────────────────────────────────────────────────

    def get_schema(self, force_refresh: bool = False) -> str:
        """
        Fetch and cache graph schema for prompt injection.
        """

        if self._schema_cache and not force_refresh:
            return self._schema_cache

        try:
            records, _, _ = self.handler.get_neo4j_schema()

            schema = records[0].data()

            node_labels = [
                n["name"]
                for n in schema.get("nodes", [])
            ]

            relationships = [
                f"(:{r[0]['name']})-[:{r[1]}]->(:{r[2]['name']})"
                for r in schema.get("relationships", [])
            ]

            self._schema_cache = (
                "Node labels: "
                + ", ".join(node_labels)
                + "\n"
                + "Relationships:\n  "
                + "\n  ".join(relationships)
            )

            logger.info("Schema fetched and cached.")

        except Exception as e:
            logger.warning(
                "Schema fetch failed: %s. Using fallback.",
                e
            )

            self._schema_cache = "(schema unavailable)"

        return self._schema_cache

    def refresh_schema(self):
        """Clear cached schema."""
        self._schema_cache = None
        logger.info("Schema cache cleared.")

    # ─────────────────────────────────────────────────────────────
    # CYPHER GENERATION
    # ─────────────────────────────────────────────────────────────

    # ─────────────────────────────────────────────────────────────
    # LLM OUTPUT PARSER
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_llm_output(cleaned: str, raw: Any) -> dict:
        """
        Robustly parse LLM output into a Python dict.

        Tries three strategies in order:
          1. json.loads            — strict, handles proper JSON
          2. ast.literal_eval      — handles Python dict with single quotes
          3. single→double quotes  — last-resort regex normalisation
        """
        # ── Strategy 1: strict JSON ──────────────────────────────
        try:
            data = json.loads(cleaned)
            logger.debug("Parsed via json.loads.")
            return data

        except json.JSONDecodeError:
            pass

        # ── Strategy 2: Python literal (single-quote dict) ───────
        try:
            data = ast.literal_eval(cleaned)

            if isinstance(data, dict):
                logger.warning(
                    "LLM returned Python dict repr (single quotes); "
                    "parsed via ast.literal_eval."
                )
                return data

        except (ValueError, SyntaxError):
            pass

        # ── Strategy 3: normalise single → double quotes ─────────
        try:
            # Replace single-quoted keys/values carefully
            normalised = re.sub(r"'([^']*)'", r'"\1"', cleaned)
            data = json.loads(normalised)
            logger.warning(
                "LLM output normalised from single quotes; "
                "parsed via json.loads after regex fix."
            )
            return data

        except (json.JSONDecodeError, Exception):
            pass

        # ── All strategies exhausted ──────────────────────────────
        logger.error(
            "All parse strategies failed.\nRaw: %s\nCleaned: %s",
            raw,
            cleaned,
        )

        raise ValueError(
            f"LLM returned unparseable output.\n\nRaw Output:\n{raw}"
        )

    def generate_cypher(
        self,
        question: str,
        schema: str,
    ) -> dict:
        """
        Convert natural language into a Cypher query using the LLM.

        Returns a dict with keys:
          - cypher      : str  — Cypher string or 'UNSUPPORTED_QUERY'
          - return_type : str  — 'graph' | 'scalar' | 'none'
          - params      : dict — query parameters (may be empty)
        """

        system_prompt = get_text_to_cypher_system_prompt()

        logger.debug("Schema:\n%s", schema)
        logger.debug("Question: %s", question)

        prompt = (
            f"{system_prompt}\n\n"
            f"=== Graph Schema ===\n{schema}\n\n"
            f"=== Question ===\n{question}\n\n"
        )

        # ─────────────────────────────────────────────
        # STEP 1 — Generate raw response
        # ─────────────────────────────────────────────

        raw = self.llm.generate(prompt=prompt)

        logger.info("Raw LLM Output: %s", raw)

        # ─────────────────────────────────────────────
        # STEP 2 — Remove markdown fences
        # ─────────────────────────────────────────────

        cleaned = re.sub(
            r"```(?:json|cypher)?\s*",
            "",
            str(raw),
            flags=re.IGNORECASE,
        )

        cleaned = cleaned.replace("```", "").strip()

        logger.info("Cleaned LLM Output: %s", cleaned)

        # ─────────────────────────────────────────────
        # STEP 3 — Parse JSON safely (multi-strategy)
        # ─────────────────────────────────────────────
        #
        # Some local LLMs (e.g. Ollama) return a Python dict
        # repr with single quotes instead of valid JSON.
        # Strategy order:
        #   1. json.loads          — fast, strict
        #   2. ast.literal_eval    — handles single-quote dicts
        #   3. single→double quote — last-resort regex fix
        # ─────────────────────────────────────────────

        data = self._parse_llm_output(cleaned, raw)

        # ─────────────────────────────────────────────
        # STEP 4 — Validate structure
        # ─────────────────────────────────────────────

        if not isinstance(data, dict):
            raise ValueError(
                f"LLM output must be a JSON object.\nParsed: {data}"
            )

        if "cypher" not in data:
            raise ValueError(
                f"Missing 'cypher' key in LLM output.\nParsed: {data}"
            )

        # ─────────────────────────────────────────────
        # STEP 5 — Extract and normalise fields
        # ─────────────────────────────────────────────

        cypher = str(data["cypher"]).strip()

        if not cypher:
            raise ValueError(
                f"Empty Cypher query returned by LLM.\nParsed: {data}"
            )

        # return_type: default to "graph" if absent or invalid
        return_type = str(
            data.get("return_type", "graph")
        ).lower().strip()

        if return_type not in VALID_RETURN_TYPES:
            logger.warning(
                "Unknown return_type '%s'; defaulting to 'graph'.",
                return_type,
            )
            return_type = "graph"

        # params: default to empty dict if absent or wrong type
        params = data.get("params", {})

        if not isinstance(params, dict):
            logger.warning(
                "LLM 'params' is not a dict (%s); ignoring.",
                type(params),
            )
            params = {}

        logger.info(
            "Generated Cypher: %s | return_type: %s | params: %s",
            cypher,
            return_type,
            params,
        )

        return {
            "cypher": cypher,
            "return_type": return_type,
            "params": params,
        }

    # ─────────────────────────────────────────────────────────────
    # LIMIT GUARD  (graph queries only)
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _ensure_limit(cypher: str, return_type: str) -> str:
        """
        Append a default LIMIT to graph queries that omit one,
        preventing accidental full-graph scans.
        """

        if return_type != "graph":
            return cypher

        if re.search(r"\bLIMIT\b", cypher, re.IGNORECASE):
            return cypher

        logger.warning(
            "Graph query missing LIMIT — appending LIMIT %d.",
            DEFAULT_GRAPH_LIMIT,
        )

        return f"{cypher} LIMIT {DEFAULT_GRAPH_LIMIT}"

    # ─────────────────────────────────────────────────────────────
    # CYPHER VALIDATOR & AUTO-FIX
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _fix_cypher(cypher: str) -> str:
        """
        Detect and auto-fix common LLM Cypher generation mistakes
        before sending to Neo4j.

        Fix: collect(r) / collect(m) used in RETURN without a prior
        MATCH or OPTIONAL MATCH that binds r and m.
        Inject 'OPTIONAL MATCH (n)-[r]-(m)' before RETURN.
        """

        upper = cypher.upper().replace(" ", "")

        uses_collect_r = "COLLECT(R)" in upper
        uses_collect_m = "COLLECT(M)" in upper

        # r is bound if any MATCH clause contains -[r]- or -[r:
        has_r_bound = bool(
            re.search(r"-[r[\]:\s]", cypher, re.IGNORECASE)
        )
        # m is bound if OPTIONAL MATCH or a MATCH pattern ends with -(m)
        has_m_bound = bool(
            re.search(r"optional\s+match", cypher, re.IGNORECASE)
        ) or bool(
            re.search(r"-\(\s*m\s*\)", cypher, re.IGNORECASE)
        )

        needs_fix = (
            (uses_collect_r and not has_r_bound)
            or (uses_collect_m and not has_m_bound)
        )

        if needs_fix:
            logger.warning(
                "Auto-fix: collect(r)/collect(m) used without OPTIONAL MATCH. "
                "Injecting 'OPTIONAL MATCH (n)-[r]-(m)' before RETURN."
            )
            cypher = re.sub(
                r"(?i)\bRETURN\b",
                "OPTIONAL MATCH (n)-[r]-(m) RETURN",
                cypher,
                count=1,
            )
            logger.info("Fixed Cypher: %s", cypher)

        return cypher

    # ─────────────────────────────────────────────────────────────
    # KEYWORD INJECTION FALLBACK
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_keywords(question: str) -> list[str]:
        """
        Extract meaningful keywords from a natural-language question.
        Strips common stop words so only domain terms remain.
        """

        stop_words = {
            "my", "the", "a", "an", "is", "are", "was", "were",
            "it", "its", "i", "me", "look", "looks", "so", "very",
            "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "this", "that", "what", "how", "why",
            "sick", "bad", "good", "like", "seem", "seems",
        }

        words = re.findall(r"[a-zA-Z]+", question.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]

    @staticmethod
    def _build_fallback_cypher(keywords: list[str]) -> str:
        """
        Build a broad CONTAINS-based Cypher query from keywords.
        Used when LLM returns 0 results with exact-match params.
        """

        if not keywords:
            return ""

        conditions = " OR ".join(
            f"toLower(n.name) CONTAINS '{kw}'"
            for kw in keywords[:5]          # cap at 5 keywords
        )

        return (
            f"MATCH (n) "
            f"WHERE ({conditions}) "
            f"OPTIONAL MATCH (n)-[r]-(m) "
            f"RETURN n, collect(r) AS rels, collect(m) AS neighbors "
            f"LIMIT 50"
        )

    # ─────────────────────────────────────────────────────────────
    # QUERY EXECUTION
    # ─────────────────────────────────────────────────────────────

    def execute_cypher(
        self,
        cypher: str,
        params: Optional[dict] = None,
        retries: int = 2,
    ) -> list:
        """
        Execute a Cypher query against Neo4j.

        Matches Neo4jHandler.execute_query(query, parameters=None)
        which internally calls driver.execute_query(query, params, database_=...).
        """

        params = params or {}
        last_exc = None

        for attempt in range(1, retries + 2):

            try:
                records, _, _ = self.handler.execute_query(
                    cypher,
                    parameters=params,
                )

                return self._serialize_records(records)

            except Exception as e:

                last_exc = e

                logger.warning(
                    "Execution attempt %d/%d failed: %s",
                    attempt,
                    retries + 1,
                    e,
                )

                if attempt <= retries:
                    time.sleep(1.0)

        raise RuntimeError(
            f"Query failed after {retries + 1} attempt(s). "
            f"Last error: {last_exc}"
        ) from last_exc

    # ─────────────────────────────────────────────────────────────
    # SERIALIZATION
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _serialize_records(records) -> list:
        """
        Convert Neo4j records into JSON-safe dicts.
        Handles node objects, relationship objects, path collections,
        and primitive values produced by graph-return queries.
        """

        result = []

        for record in records:

            try:
                row = {}

                for key in record.keys():
                    row[key] = TextToCypherPipeline._convert_value(
                        record[key]
                    )

                result.append(row)

            except Exception as e:
                logger.warning(
                    "Could not serialize record: %s",
                    e,
                )

        return result

    @staticmethod
    def _convert_value(value: Any) -> Any:
        """
        Recursively convert Neo4j objects into JSON-safe types.

        Handles:
          - Neo4j Node / Relationship  → dict with labels/type + props
          - list / tuple               → list (recurse)
          - dict                       → dict (recurse)
          - primitives                 → as-is
        """

        # Neo4j Node object (has .labels and .items())
        if hasattr(value, "labels") and hasattr(value, "items"):
            return {
                "_labels": list(value.labels),
                **dict(value.items()),
            }

        # Neo4j Relationship object (has .type and .items())
        if hasattr(value, "type") and hasattr(value, "items"):
            return {
                "_type": value.type,
                **dict(value.items()),
            }

        # Generic mapping (covers older neo4j-driver Node fallback)
        if hasattr(value, "items"):
            return dict(value.items())

        if isinstance(value, (list, tuple)):
            return [
                TextToCypherPipeline._convert_value(v)
                for v in value
            ]

        if isinstance(value, dict):
            return {
                k: TextToCypherPipeline._convert_value(v)
                for k, v in value.items()
            }

        return value

    # ─────────────────────────────────────────────────────────────
    # DEBUG HELPERS
    # ─────────────────────────────────────────────────────────────

    def debug_neo4j(self) -> None:
        """
        Print diagnostic info about what's actually in Neo4j.
        Run this to troubleshoot empty query results.
        """

        checks = [
            (
                "Node labels in DB",
                "CALL db.labels() YIELD label RETURN label",
            ),
            (
                "Relationship types in DB",
                "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType",
            ),
            (
                "Sample nodes with name property (top 20)",
                "MATCH (n) WHERE n.name IS NOT NULL "
                "RETURN labels(n) AS labels, n.name AS name LIMIT 20",
            ),
            (
                "Total node count",
                "MATCH (n) RETURN count(n) AS total",
            ),
            (
                "Total relationship count",
                "MATCH ()-[r]->() RETURN count(r) AS total",
            ),
            (
                "All property keys used",
                "CALL db.propertyKeys() YIELD propertyKey RETURN propertyKey",
            ),
        ]

        print("\n" + "=" * 60)
        print("NEO4J DIAGNOSTIC REPORT")
        print("=" * 60)

        for title, cypher in checks:
            print(f"\n── {title} ──")
            print(f"   {cypher}")
            try:
                records, _, _ = self.handler.execute_query(cypher)
                rows = self._serialize_records(records)
                if rows:
                    for row in rows:
                        print(f"   {row}")
                else:
                    print("   (no results)")
            except Exception as e:
                print(f"   ERROR: {e}")

        print("\n" + "=" * 60)

    def debug_search(self, keyword: str) -> None:
        """
        Free-text search across all node properties for a keyword.
        Useful to confirm data exists before running structured queries.
        """

        cypher = (
            "MATCH (n) "
            "WHERE any(key IN keys(n) WHERE "
            "toLower(toString(n[key])) CONTAINS toLower($kw)) "
            "RETURN labels(n) AS labels, n AS props LIMIT 20"
        )

        print(f"\n── Searching all nodes for: '{keyword}' ──")

        try:
            records, _, _ = self.handler.execute_query(
                cypher,
                parameters={"kw": keyword},
            )
            rows = self._serialize_records(records)
            if rows:
                for row in rows:
                    print(f"   {row}")
            else:
                print(f"   No nodes found containing '{keyword}'.")
                print("   ➜ Check if the data was loaded / label names match schema.")
        except Exception as e:
            print(f"   ERROR: {e}")

    # ─────────────────────────────────────────────────────────────
    # MAIN PIPELINE
    # ─────────────────────────────────────────────────────────────

    def query(self, natural_language_input: str) -> dict:
        """
        Full pipeline:
          Natural language -> Cypher -> Neo4j -> JSON

        Output shape:
          {
            "timestamp":   str,
            "question":    str,
            "cypher":      str,
            "return_type": str,
            "params":      dict,
            "records":     list,
            "metadata":    { result_count, elapsed_ms },
            "error":       str | None,
          }
        """

        logger.info("Query received: '%s'", natural_language_input)

        start = time.perf_counter()

        output = {
            "timestamp":   datetime.utcnow().isoformat(),
            "question":    natural_language_input,
            "cypher":      "",
            "return_type": "",
            "params":      {},
            "records":     [],
            "metadata":    {},
            "error":       None,
        }

        try:
            # ─────────────────────────────────────────
            # STEP 1 — Fetch schema
            # ─────────────────────────────────────────

            schema = self.get_schema()

            # ─────────────────────────────────────────
            # STEP 2 — Generate Cypher (now returns dict)
            # ─────────────────────────────────────────

            llm_result = self.generate_cypher(
                natural_language_input,
                schema,
            )

            cypher      = llm_result["cypher"]
            return_type = llm_result["return_type"]
            params      = llm_result["params"]

            output["cypher"]      = cypher
            output["return_type"] = return_type
            output["params"]      = params

            # ─────────────────────────────────────────
            # STEP 3 — Handle unsupported query
            # ─────────────────────────────────────────

            if not cypher or cypher == UNSUPPORTED_QUERY:

                output["return_type"] = "none"
                output["error"] = (
                    "Question could not be mapped "
                    "to the graph schema."
                )

                logger.warning("LLM returned UNSUPPORTED_QUERY.")

                return output

            # ─────────────────────────────────────────
            # STEP 4 — Safety: fix + inject LIMIT
            # ─────────────────────────────────────────

            cypher = self._fix_cypher(cypher)
            cypher = self._ensure_limit(cypher, return_type)
            output["cypher"] = cypher

            # ─────────────────────────────────────────
            # STEP 5 — Execute query
            # ─────────────────────────────────────────

            records = self.execute_cypher(cypher, params=params)

            # ─────────────────────────────────────────
            # STEP 6 — Fallback: keyword CONTAINS search
            #          if LLM exact-match returned nothing
            # ─────────────────────────────────────────

            if not records and return_type == "graph":

                keywords = self._extract_keywords(natural_language_input)
                fallback_cypher = self._build_fallback_cypher(keywords)

                if fallback_cypher:
                    logger.warning(
                        "Primary query returned 0 results. "
                        "Retrying with keyword CONTAINS fallback. "
                        "Keywords: %s",
                        keywords,
                    )

                    records = self.execute_cypher(
                        fallback_cypher,
                        params={},
                    )

                    if records:
                        output["cypher"] = fallback_cypher
                        output["params"] = {}
                        output["metadata"]["fallback_used"] = True
                        output["metadata"]["fallback_keywords"] = keywords
                        logger.info(
                            "Fallback returned %d record(s).",
                            len(records),
                        )
                    else:
                        logger.warning("Fallback also returned 0 results.")

            elapsed_ms = round(
                (time.perf_counter() - start) * 1000,
                2,
            )

            output["records"]  = records
            output["metadata"].update({
                "result_count": len(records),
                "elapsed_ms":   elapsed_ms,
            })

            logger.info(
                "Returned %d record(s) in %.1f ms.",
                len(records),
                elapsed_ms,
            )

        except Exception as e:

            output["error"] = str(e)

            logger.error(
                "Pipeline error: %s\n%s",
                e,
                traceback.format_exc(),
            )

        return output

    def query_json(
        self,
        natural_language_input: str,
        indent: int = 2,
    ) -> str:
        """
        Same as query() but returns a formatted JSON string.
        """

        return json.dumps(
            self.query(natural_language_input),
            indent=indent,
            ensure_ascii=False,
        )

    def batch_query(self, questions: list) -> list:
        """
        Run multiple queries sequentially.
        """

        return [self.query(q) for q in questions]

    # ─────────────────────────────────────────────────────────────
    # LIFECYCLE
    # ─────────────────────────────────────────────────────────────

    def close(self):
        self.handler.close()
        logger.info("Neo4j connection closed.")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


# ─────────────────────────────────────────────────────────────────────────────
# INTERACTIVE CLI
# ─────────────────────────────────────────────────────────────────────────────

def run_interactive_session(pipeline: TextToCypherPipeline):
    """
    Interactive REPL for manual testing.

    Special commands:
      :debug          — print full Neo4j diagnostic report
      :search <kw>    — search all node properties for keyword
      :schema         — print cached schema
      :refresh        — clear and re-fetch schema
      exit / quit     — exit
    """

    print("\n=== Text-to-Cypher (Knowledge Graph) ===")
    print("Commands: :debug | :search <keyword> | :schema | :refresh | exit\n")

    while True:

        try:
            user_input = input("Question > ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        # ── Special debug commands ────────────────────────────────
        if user_input == ":debug":
            pipeline.debug_neo4j()
            continue

        if user_input.startswith(":search "):
            keyword = user_input[len(":search "):].strip()
            if keyword:
                pipeline.debug_search(keyword)
            else:
                print("Usage: :search <keyword>")
            continue

        if user_input == ":schema":
            print("\n── Cached Schema ──")
            print(pipeline.get_schema())
            continue

        if user_input == ":refresh":
            pipeline.refresh_schema()
            print("Schema cache cleared. Will re-fetch on next query.")
            continue

        result = pipeline.query(user_input)

        print("\n" + "=" * 60)
        print(f"Cypher      : {result['cypher']}")
        print(f"Return type : {result['return_type']}")

        if result["params"]:
            print(f"Params      : {result['params']}")

        print(f"Records     : {result['metadata'].get('result_count', 0)}")
        print(f"Elapsed     : {result['metadata'].get('elapsed_ms', '-')} ms")

        if result["error"]:
            print(f"Error       : {result['error']}")

        else:
            print(
                "Results:\n"
                + json.dumps(
                    result["records"],
                    indent=2,
                    ensure_ascii=False,
                )
            )

        print("=" * 60 + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    with TextToCypherPipeline() as pipeline:
        run_interactive_session(pipeline)