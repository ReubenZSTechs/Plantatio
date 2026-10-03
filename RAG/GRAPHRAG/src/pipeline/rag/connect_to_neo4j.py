"""Thin wrapper around the Neo4j driver used by the GraphRAG retriever.

Connection details come from the environment (NEO4J_URI, NEO4J_USER,
NEO4J_PASSWORD, NEO4J_DATABASE) so no credential is stored in source.
"""

from __future__ import annotations

import logging
import os

from neo4j import GraphDatabase

logger = logging.getLogger(__name__)


class Neo4jNotConfigured(RuntimeError):
    """Raised when the graph is used before its credentials are supplied."""


def _graph_env() -> tuple[str, str, str, str]:
    """Return (uri, user, password, database) from the environment."""
    return (
        os.getenv("NEO4J_URI", "").strip(),
        os.getenv("NEO4J_USER", "").strip(),
        os.getenv("NEO4J_PASSWORD", "").strip(),
        os.getenv("NEO4J_DATABASE", "neo4j").strip() or "neo4j",
    )


def graph_is_configured() -> bool:
    """True when enough environment detail exists to attempt a connection."""
    uri, user, password, _ = _graph_env()
    return bool(uri and user and password)


class Neo4jHandler:
    """Owns a Neo4j driver and exposes the queries the pipeline needs.

    Supports the context-manager protocol so callers can guarantee the driver
    is closed:

        with Neo4jHandler() as handler:
            records, summary, keys = handler.get_neo4j_entities()
    """

    def __init__(self, uri: str | None = None, auth: tuple[str, str] | None = None,
                 database: str | None = None):
        env_uri, env_user, env_password, env_database = _graph_env()

        self.uri = uri or env_uri
        self.auth = auth or (env_user, env_password)
        self.database = database or env_database
        self.driver = None

    def __enter__(self) -> "Neo4jHandler":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def connect(self) -> None:
        """Open the driver, verifying that credentials are present first."""
        if not (self.uri and self.auth[0] and self.auth[1]):
            raise Neo4jNotConfigured(
                "Neo4j is not configured. Set NEO4J_URI, NEO4J_USER and "
                "NEO4J_PASSWORD (see .env.example)."
            )

        self.driver = GraphDatabase.driver(self.uri, auth=self.auth)
        logger.info("Connected to Neo4j database %r.", self.database)

    def execute_query(self, query: str, parameters: dict | None = None):
        """Run a Cypher query, returning the driver's (records, summary, keys)."""
        if not self.driver:
            raise Neo4jNotConfigured("Driver not connected. Call connect() first.")

        return self.driver.execute_query(
            query,
            parameters or {},
            database_=self.database,
        )

    def close(self) -> None:
        """Close the driver if one is open."""
        if self.driver:
            self.driver.close()
            self.driver = None

    def get_neo4j_entities(self, limit: int = 25):
        """Return up to `limit` :Entity nodes."""
        return self.execute_query("MATCH (n:Entity) RETURN n LIMIT $limit", {"limit": limit})

    def get_neo4j_relationships(self, limit: int = 25):
        """Return up to `limit` relationships of any type."""
        return self.execute_query("MATCH ()-[r]->() RETURN r LIMIT $limit", {"limit": limit})

    def get_neo4j_all_nodes(self, limit: int = 25):
        """Return up to `limit` nodes of any label."""
        return self.execute_query("MATCH (n) RETURN n LIMIT $limit", {"limit": limit})

    def get_neo4j_all_data(self, limit: int = 25):
        """Return up to `limit` (source)-[rel]->(target) triples."""
        return self.execute_query(
            "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT $limit", {"limit": limit}
        )

    def get_neo4j_data_by_label(self, label: str, limit: int = 25):
        """Return up to `limit` nodes carrying `label`.

        The label is interpolated because Cypher cannot parameterise labels; it
        is validated first so the call cannot be used to inject Cypher.
        """
        if not label.isidentifier():
            raise ValueError(f"Invalid node label: {label!r}")

        return self.execute_query(f"MATCH (n:`{label}`) RETURN n LIMIT $limit", {"limit": limit})

    def get_neo4j_schema(self):
        """Return the graph's node labels and relationship types."""
        return self.execute_query("CALL db.schema.visualization()")

    def describe_schema(self) -> str:
        """Render the graph schema as readable text for prompt injection."""
        records, _, _ = self.get_neo4j_schema()
        schema = records[0].data()

        labels = [node["name"] for node in schema.get("nodes", [])]
        relationships = [
            f"(:{rel[0]['name']})-[:{rel[1]}]->(:{rel[2]['name']})"
            for rel in schema.get("relationships", [])
        ]

        return (
            "Node labels: " + ", ".join(labels) + "\n"
            "Relationships:\n  " + "\n  ".join(relationships)
        )

    def clear_database(self) -> None:
        """Delete every node and relationship. Irreversible."""
        self.execute_query("MATCH (n) DETACH DELETE n")
