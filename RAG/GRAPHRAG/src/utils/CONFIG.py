CONFIG = {
    'DATA_FILEPATH_TRANSCRIPT': 'data/transcript',
    'DATA_FILEPATH_AUDIO': 'data/audio',
    'DATA_FILETYPE_TRANSCRIPT': '.json',
    'DATA_FILETYPE_AUDIO': '.mp3',
    'LLM_MODEL_NAME': "qwen3.5:35b", # Ollama model
    'LLM_EVALUATOR_NAME': 'phi3:3.8b',
    'LLM_REWRITER_NAME': 'llama3.2:3b',
    
    'EMBEDDING_MODEL_NAME_BGE': "BAAI/bge-m3", # BGE
    'EMBEDDING_MODEL_NAME_SENTENCEBERT': 'all-MiniLM-L6-v2', # SentenceBERT
    'COLLECTION_NAME_BGE': "AUDIO_LLM-BGE",
    'COLLECTION_NAME_SENTENCEBERT': "AUDIO_LLM-SENTENCEBERT",
    'CSV_RESULTS_FILEPATH': 'data/training_results/results.csv',
    'PROCESSED_VERSES_FILEPATH': 'logs/processed_verses.json',

    'OLLAMA_MODELS': {
        'WORKER_1': "mistral-small3.2:24b",
        'WORKER_2': "deepseek-r1:32b",
        'WORKER_3': "gemma4:31b",
        'WORKER_4': "qwen3.5:9b-q8_0",
        'WORKER_5': "qwen3.5:35b",
        'WORKER_6': "qwen3.6:35b",
        'DEBATOR_1': "deepseek-r1:32b",
        'DEBATOR_2': "gemma4:31b",
        'DEBATOR_3': "qwen3.6:35b",
        "EVALUATOR": "qwen3.6:27b",
        'LLM_ENTITY_EXTRACTION': 'mistral-small:22b',
        'Text_to_Cypher': 'mistral-small:22b'
    },
    
    'LOGFILE': 'logs/LLM_logs.jsonl',
    'NODE_LOGS': 'logs/node_logs.jsonl',
    'CORRELATION_THRESHOLD': 0.9,
    'ENTITY_THRESHOLD': 0.7,
    'TOP_RESULT_CONFIDENCE': 0.75,
    
}