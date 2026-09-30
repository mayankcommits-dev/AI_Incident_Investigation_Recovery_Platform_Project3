from app.rag.embeddings import embed_query
from app.rag.vector_store import search_documents

RETRIEVAL_DISTANCE_THRESHOLD = 1.0

def retrieve_runbooks(query: str, top_k: int = 2):
    query_embedding = embed_query(query)

    results = search_documents(
        query_embedding=query_embedding,
        top_k=top_k
    )

    retrieved_chunks = []

    for i in range(len(results["documents"][0])):
        distance = results["distances"][0][i]

        if distance <= RETRIEVAL_DISTANCE_THRESHOLD:
            retrieved_chunks.append({
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "chunk_number": results["metadatas"][0][i]["chunk_number"],
                "distance": distance
            })

    return retrieved_chunks


