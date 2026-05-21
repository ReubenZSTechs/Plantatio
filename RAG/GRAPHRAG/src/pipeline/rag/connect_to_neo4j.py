from neo4j import GraphDatabase
from requests import session

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j+s://0178696e.databases.neo4j.io"
AUTH = ("0178696e", "YJ3Qg2EupZUgBX7X9DnJRUzF3-OH8GmviRTAsC-dxfc")
DATABASE = "0178696e"

# URI = "neo4j://127.0.0.1:7687"
# AUTH = ("neo4j", "CRCP4ss!")
# DATABASE = "neo4j"

# with GraphDatabase.driver(URI, auth=AUTH) as driver:
#     driver.verify_connectivity()

#     records, summary, keys = driver.execute_query("""
#         MATCH (n:Entity) RETURN n LIMIT 25;
#         """,
#         database_="bible",
#     )

#     # Loop through results and do something with them
#     # for record in records:
#     #     print(record.data())  # obtain record as dict

#     # print("============")
#     # for i in records:
#     #     print(i)
#     # print("============")
#     # for i in records:
#     #     print(i.data())
#     # print("============")
#     # print(summary)
#     # print("============")
#     # print(keys)

#     # Summary information
#     # print("The query `{query}` returned {records_count} records in {time} ms.".format(
#     #     query=summary.query, records_count=len(records),
#     #     time=summary.result_available_after
#     # ))



class Neo4jHandler:
    def __init__(self, uri=URI, auth=AUTH):
        self.uri = uri
        self.auth = auth
        self.database = DATABASE
        self.driver = None

    def connect(self):
        self.driver = GraphDatabase.driver(self.uri, auth=self.auth)

    def execute_query(self, query, parameters=None):
        if not self.driver:
            raise Exception("Driver not connected. Call connect() first.")

        records, summary, keys = self.driver.execute_query(
            query,
            parameters or {},
            database_=self.database
        )

        return records, summary, keys

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None

    def close_neo4j_driver(self, driver):
        driver.close()


    def get_neo4j_entities(self, limit=25):
        query = f"""
            MATCH (n:Entity) RETURN n LIMIT {limit};
            """
        return self.execute_query(query)

    def get_neo4j_relationships(self, limit=25):
        query = f"""
            MATCH ()-[r]->() RETURN r LIMIT {limit};
            """
        return self.execute_query(query)

    def get_neo4j_all_nodes(self, limit=25):
        query = f"""
            MATCH (n) RETURN n LIMIT {limit};
            """
        return self.execute_query(query)

    def get_neo4j_all_data(self, limit=25):
        query = f"""
            MATCH (n)-[r]->(m) RETURN n, r, m LIMIT {limit};
            """
        return self.execute_query(query)

    def get_neo4j_data_by_label(self, label, limit=25):
        query = f"""
            MATCH (n:{label}) RETURN n LIMIT {limit};
            """
        return self.execute_query(query)

    def get_neo4j_schema(self):
        query = """
            CALL db.schema.visualization();
            """
        return self.execute_query(query)

    def print_schema(self):
        records, summary, keys = handler.get_neo4j_schema()
        print(records)
        schema = records[0].data()

        print("\n========== NODE LABELS ==========\n")

        for node in schema["nodes"]:
            print(f"- {node['name']}")

        print("\n====== RELATIONSHIP TYPES ======\n")

        for rel in schema["relationships"]:

            source = rel[0]["name"]
            relation = rel[1]
            target = rel[2]["name"]

            print(f"(:{source})-[:{relation}]->(:{target})")

    def clear_database(self):
        query = """
            MATCH (n) DETACH DELETE n;
            """
        return self.execute_query(query)

    

if __name__ == "__main__":
    handler = Neo4jHandler()
    handler.connect()
    # handler.clear_database()
    handler.print_schema()