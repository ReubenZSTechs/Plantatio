import json
from neo4j import GraphDatabase
from tqdm import tqdm

URI = "neo4j+s://0178696e.databases.neo4j.io"
USERNAME = "0178696e"
NEO4J_PASSWORD = "YJ3Qg2EupZUgBX7X9DnJRUzF3-OH8GmviRTAsC-dxfc"
NEO4J_DATABASE = "0178696e"

JSONL_PATH = "src/pipeline/rag/tomato_triplets_dataset.jsonl"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, NEO4J_PASSWORD)
)

def sanitize_relation(rel):
    return (
        rel.upper()
        .replace(" ", "_")
        .replace("-", "_")
    )

def insert_triplet(tx, item):

    t = item["triplets"][0]

    subject = t["subject"]
    relation = sanitize_relation(t["relation"])
    object_ = t["object"]

    subj_label = t["subj_ner"]
    obj_label = t["obj_ner"]

    query = f"""
    MERGE (s:{subj_label} {{
        name: $subject
    }})

    MERGE (o:{obj_label} {{
        name: $object
    }})

    MERGE (s)-[r:{relation}]->(o)

    SET r.text = $text
    """

    tx.run(
        query,
        subject=subject,
        object=object_,
        text=item["text"]
    )

with open(JSONL_PATH, "r", encoding="utf-8") as f:
    lines = [json.loads(line) for line in f]

with driver.session() as session:

    for item in tqdm(lines):

        session.execute_write(
            insert_triplet,
            item
        )

driver.close()

print("DONE")