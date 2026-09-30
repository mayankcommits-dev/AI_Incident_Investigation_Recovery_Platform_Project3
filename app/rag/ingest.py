from pathlib import Path

from app.rag.document_processor import load_runbooks, create_chunks
from app.rag.embeddings import embed_documents
from app.rag.vector_store import store_documents


project_root = Path(__file__).resolve().parent.parent.parent
runbook_directory = project_root / "data" / "runbooks"


def ingest_runbooks():
    documents = load_runbooks(runbook_directory)

    chunks = create_chunks(
        documents,
        chunk_size=500,
        overlap=100
    )

    texts = [chunk["text"] for chunk in chunks]
    ids = [chunk["id"] for chunk in chunks]

    metadata = [
        {
            "source": chunk["source"],
            "chunk_number": chunk["chunk_number"]
        }
        for chunk in chunks
    ]

    embeddings = embed_documents(texts)

    store_documents(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadata=metadata
    )

    print(f"Ingested {len(chunks)} runbook chunks into ChromaDB.")


if __name__ == "__main__":
    ingest_runbooks()