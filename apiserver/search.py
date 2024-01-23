import meilisearch
import os

MEILISEARCH_URL = os.getenv("MEILISEARCH_URL")
MEILISEARCH_KEY = os.getenv("MEILISEARCH_KEY")
MEILISEARCH_INDEX = os.getenv("MEILISEARCH_INDEX")

client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_KEY)

# An index is where the documents are stored.
index = client.index(MEILISEARCH_INDEX)


def execute_search(search_queries: dict) -> dict | None:
    return client.multi_search(search_queries)


def add_documents(documents: list[dict]):
    print(documents)
    return index.add_documents(documents)


def delete_document(comp_id: any):
    return index.delete_document(comp_id)
