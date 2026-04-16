import os
import chromadb
from django.conf import settings
from sentence_transformers import SentenceTransformer

client = None
embedding_model = None
GLOBAL_COLLECTION_NAME = "all_books"

def get_chroma_client():
    global client
    if client is None:
        persist_dir = str(settings.CHROMA_PERSIST_DIRECTORY)
        os.makedirs(persist_dir, exist_ok=True)
        client = chromadb.PersistentClient(path=persist_dir)
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

def get_global_collection():
    client = get_chroma_client()
    try:
        return client.get_collection(name=GLOBAL_COLLECTION_NAME)
    except:
        return client.create_collection(name=GLOBAL_COLLECTION_NAME)

def add_chunks_to_global_store(book_id, book_title, chunks):
    """Add chunks to the global cross-book collection."""
    collection = get_global_collection()
    ids = [f"book_{book_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"book_id": book_id, "book_title": book_title, "chunk_index": i} for i in range(len(chunks))]
    collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)

def global_similarity_search(query, top_k=5):
    """Search across ALL books."""
    collection = get_global_collection()
    query_embedding = generate_embedding(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results