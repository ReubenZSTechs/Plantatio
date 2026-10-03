"""Load the tomato triplet dataset into Neo4j as a labelled knowledge graph.

Each JSONL record carries a sentence and the triplets extracted from it. The
subject and object NER types become node labels and the relation becomes the
edge type, so the graph keeps the structure the text-to-Cypher retriever
queries against.

Usage:
    python -m RAG.GRAPHRAG.src.pipeline.rag.neo4j_push [--jsonl PATH] [--wipe]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from RAG.GRAPHRAG.src.pipeline.rag.connect_to_neo4j import Neo4jHandler

logger = logging.getLogger(__name__)

DEFAULT_JSONL = Path(__file__).with_name("tomato_triplets_dataset.jsonl")

_IDENTIFIER_SAFE = re.compile(r"[^A-Za-z0-9_]")


def sanitize_identifier(value: str, fallback: str) -> str:
    """Turn free text into a Cypher-safe label or relationship type.

    Cypher cannot parameterise labels or relationship types, so they are
    interpolated. Restricting them to word characters keeps that safe.
    """
    cleaned = _IDENTIFIER_SAFE.sub("_", value.strip().upper()).strip("_")
    if not cleaned or cleaned[0].isdigit():
        cleaned = f"{fallback}_{cleaned}" if cleaned else fallback
    return cleaned


def load_triplets(jsonl_path: Path) -> list[dict]:
    """Read every triplet from the dataset, flattened across records."""
    triplets: list[dict] = []

    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Skipping malformed JSON on line %d.", line_number)
                continue

            # The original loader took only triplets[0] and silently dropped
            # the rest; every triplet in a record is kept here.
            for triplet in record.get("triplets", []):
                triplets.append({**triplet, "text": record.get("text", "")})

    return triplets


def insert_triplet(tx, triplet: dict) -> None:
    """MERGE one subject-relation-object triple into the graph."""
    subject_label = sanitize_identifier(triplet.get("subj_ner", ""), "ENTITY")
    object_label = sanitize_identifier(triplet.get("obj_ner", ""), "ENTITY")
    relation = sanitize_identifier(triplet.get("relation", ""), "RELATED_TO")

    tx.run(
        f"""
        MERGE (s:`{subject_label}` {{name: $subject}})
        MERGE (o:`{object_label}` {{name: $object}})
        MERGE (s)-[r:`{relation}`]->(o)
        SET r.text = $text
        """,
        subject=triplet["subject"],
        object=triplet["object"],
        text=triplet["text"],
    )


def ingest(jsonl_path: Path = DEFAULT_JSONL, wipe: bool = False) -> int:
    """Load the dataset into Neo4j, returning the number of triplets written."""
    triplets = load_triplets(jsonl_path)
    logger.info("Loaded %d triplets from %s.", len(triplets), jsonl_path)

    with Neo4jHandler() as handler:
        if wipe:
            logger.warning("Clearing the existing graph before ingest.")
            handler.clear_database()

        with handler.driver.session(database=handler.database) as session:
            for triplet in triplets:
                session.execute_write(insert_triplet, triplet)

    return len(triplets)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")

    parser = argparse.ArgumentParser(description="Ingest tomato triplets into Neo4j")
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL, help="Dataset path")
    parser.add_argument("--wipe", action="store_true", help="Clear the graph first")
    args = parser.parse_args()

    count = ingest(args.jsonl, wipe=args.wipe)
    logger.info("Ingested %d triplets.", count)


if __name__ == "__main__":
    main()
