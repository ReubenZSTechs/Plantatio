import json
from neo4j import GraphDatabase
from tqdm import tqdm

# =========================
# Neo4j Aura Credentials
# =========================

URI = "neo4j+s://0178696e.databases.neo4j.io"
USERNAME = "0178696e"
NEO4J_PASSWORD = "YJ3Qg2EupZUgBX7X9DnJRUzF3-OH8GmviRTAsC-dxfc"
NEO4J_DATABASE = "0178696e"

JSONL_PATH = "src/pipeline/rag/tomato_triplets_dataset.jsonl"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, NEO4J_PASSWORD)
)

# =========================
# Cypher Query
# =========================

QUERY = """
MERGE (s:Entity {name: $subject})
SET s.ner = $subj_ner

MERGE (o:Entity {name: $object})
SET o.ner = $obj_ner

MERGE (s)-[r:RELATION {type: $relation}]->(o)
SET r.text = $text
"""

# =========================
# Insert Function
# =========================

def insert_triplet(tx, item):
    triplet = item["triplets"][0]

    tx.run(
        QUERY,
        subject=triplet["subject"],
        relation=triplet["relation"],
        object=triplet["object"],
        subj_ner=triplet["subj_ner"],
        obj_ner=triplet["obj_ner"],
        text=item["text"]
    )

# =========================
# Main Import
# =========================

with open(JSONL_PATH, "r", encoding="utf-8") as f:
    lines = [json.loads(line) for line in f]

with driver.session(database=NEO4J_DATABASE) as session:
    for item in tqdm(lines):
        session.execute_write(insert_triplet, item)

driver.close()
print("Import completed!")