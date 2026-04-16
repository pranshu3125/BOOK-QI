import os
import chromadb
from chromadb.config import Settings
from django.conf import settings
from sentence_transformers import SentenceTransformer
import hashlib

client = None
embedding_model = None

def get_chroma_client():
    global client
    if client is None:
        persist_dir = str(settings.CHROMA_PERSIST_DIRECTORY)
        os.makedirs(persist_dir, exist_ok=True)
        client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
    return client

def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return embedding_model

def generate_embeddings(texts):
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()

def generate_embedding(text):
    model = get_embedding_model()
    embedding = model.encode([text])[0]
    return embedding.tolist()

def get_or_create_collection(book_id):
    client = get_chroma_client()
    collection_name = f"book_{book_id}"
    try:
        collection = client.get_collection(name=collection_name)
    except:
        collection = client.create_collection(name=collection_name)
    return collection

def add_chunks_to_vector_store(book_id, chunks):
    collection = get_or_create_collection(book_id)
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"chunk_{i}"
        collection.upsert(
            ids=[chunk_id],
            documents=[chunk],
            metadatas=[{"book_id": book_id, "chunk_index": i}]
        )

def similarity_search(book_id, query, top_k=5):
    collection = get_or_create_collection(book_id)
    
    query_embedding = generate_embedding(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    return results

def delete_book_from_vector_store(book_id):
    client = get_chroma_client()
    collection_name = f"book_{book_id}"
    try:
        client.delete_collection(name=collection_name)
    except:
        pass
