"""Tunables for the GraphRAG retrieval pipeline.

Credentials and model selection live in the environment (see .env.example);
only retrieval behaviour is configured here.
"""

CONFIG = {
    # Confidence floor for accepting an entity match during retrieval.
    'ENTITY_THRESHOLD': 0.7,

    # Confidence floor for treating the top graph result as authoritative.
    'TOP_RESULT_CONFIDENCE': 0.75,

    # Rows returned by a graph query when the generated Cypher omits a LIMIT.
    'DEFAULT_GRAPH_LIMIT': 50,
}
