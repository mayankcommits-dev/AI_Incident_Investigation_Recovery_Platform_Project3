from pathlib import Path


def load_runbooks(runbook_directory: Path):
    documents = []

    for file_path in runbook_directory.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        documents.append({
            "text": text,
            "source": file_path.name
        })

    return documents


#Chunking
def create_chunks(documents, chunk_size=500, overlap=100):
    chunks = []

    for document in documents:
        text = document["text"]
        source = document["source"]

        start = 0
        chunk_number = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            if len(chunk_text.strip()) < 100:
                break

            chunks.append({
                "id": f"{source}_{chunk_number}",
                "text": chunk_text,
                "source": source,
                "chunk_number": chunk_number
            })

            chunk_number += 1
            start += chunk_size - overlap

    return chunks