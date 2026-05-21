import chromadb
from chromadb.config import Settings

client = chromadb.PersistentClient(path='data/chroma_db')

# collection = client.get_collection(name="AUDIO_LLM-MINI_PROJECT_1-SRA")

# collection.modify(name="AUDIO_LLM-BGE")

print(client.list_collections())