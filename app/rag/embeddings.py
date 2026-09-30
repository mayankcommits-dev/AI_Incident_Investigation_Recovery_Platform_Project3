from sentence_transformers import SentenceTransformer


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_documents(texts):
    return embedding_model.encode(texts).tolist()


def embed_query(query):
    return embedding_model.encode(query).tolist()