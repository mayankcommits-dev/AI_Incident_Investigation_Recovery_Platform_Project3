from app.rag.retriever import retrieve_runbooks


test_cases = [
    {
        "query": "OCR processing timed out while extracting invoice data",
        "expected_source": "ocr_timeout_runbook.txt"
    },
    {
        "query": "Payment API authentication token has expired",
        "expected_source": "authentication_runbook.txt"
    },
    {
        "query": "Connection to the automation queue timed out",
        "expected_source": "queue_connection_runbook.txt"
    }
]


unsupported_queries = [
    "How do I reset my employee password?",
    "What is the weather today?",
    "The database disk is completely full"
]


# Unsupported queries
for query in unsupported_queries:

    results = retrieve_runbooks(
        query=query,
        top_k=2
    )

    assert len(results) == 0, (
        f"Unsupported query retrieved: {results}"
    )

    print("\nUnsupported Query:", query)


# Supported queries
for case in test_cases:

    results = retrieve_runbooks(
        query=case["query"],
        top_k=2
    )

    assert len(results) > 0, (
        f"No runbook retrieved for: {case['query']}"
    )

    assert results[0]["source"] == case["expected_source"], (
        f"Expected {case['expected_source']}, "
        f"got {results[0]['source']}"
    )

    print("\nQuery:", case["query"])
    print("Expected:", case["expected_source"])

    for result in results:
        print(
            result["source"],
            "Distance:",
            round(result["distance"], 3)
        )