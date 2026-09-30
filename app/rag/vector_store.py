from pathlib import Path
import chromadb


project_root = Path(__file__).resolve().parent.parent.parent
chroma_path = project_root / "chroma_db"

client = chromadb.PersistentClient(path=str(chroma_path))

collection = client.get_or_create_collection(
    name="incident_runbooks"
)


def store_documents(ids, embeddings, documents, metadata):
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadata
    )


def search_documents(query_embedding, top_k=2):
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )