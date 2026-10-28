import os
import numpy as np
import faiss

from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from langchain_openai import OpenAIEmbeddings

from app.services.runbook_ingestion import (
    load_runbooks,
    split_runbooks,
)

load_dotenv()


class HybridRunbookSearch:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
        self.documents = []
        self.vector_index = None
        self.bm25_index = None

    def build_index(self):
        """Build FAISS and BM25 indexes from runbooks."""
        runbooks = load_runbooks()
        self.documents = split_runbooks(runbooks)

        if not self.documents:
            raise ValueError("No runbook documents found.")

        texts = [
            document.page_content
            for document in self.documents
        ]

        # Build keyword-search index
        tokenized_texts = [
            text.lower().split()
            for text in texts
        ]
        self.bm25_index = BM25Okapi(tokenized_texts)

        # Build semantic-search index
        vectors = self.embeddings.embed_documents(texts)
        vectors = np.asarray(vectors, dtype="float32")

        faiss.normalize_L2(vectors)

        self.vector_index = faiss.IndexFlatIP(
            vectors.shape[1]
        )
        self.vector_index.add(vectors)

        print(f"Indexed documents: {len(self.documents)}")
        print("FAISS index: ready")
        print("BM25 index: ready")

    def search(self, query: str, k: int = 3) -> list[dict]:
        """Combine semantic and keyword retrieval rankings."""
        if self.vector_index is None or self.bm25_index is None:
            raise RuntimeError("Call build_index() first.")

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        k = max(1, min(k, len(self.documents)))

        # Semantic search
        query_vector = np.asarray(
            [self.embeddings.embed_query(query)],
            dtype="float32",
        )
        faiss.normalize_L2(query_vector)

        _, semantic_ids = self.vector_index.search(
            query_vector, k
        )

        # Keyword search
        keyword_scores = self.bm25_index.get_scores(
            query.lower().split()
        )
        keyword_ids = np.argsort(keyword_scores)[::-1][:k]

        # Reciprocal Rank Fusion combines the two rankings.
        scores = {}
        rank_constant = 60

        for ranking in (semantic_ids[0], keyword_ids):
            for rank, doc_id in enumerate(ranking, start=1):
                doc_id = int(doc_id)
                if doc_id >= 0:
                    scores[doc_id] = scores.get(doc_id, 0) + (
                        1 / (rank_constant + rank)
                    )

        ranked_ids = sorted(
            scores,
            key=scores.get,
            reverse=True,
        )

        return [
            {
                "content": self.documents[doc_id].page_content,
                "source": self.documents[doc_id].metadata["source"],
                "score": round(scores[doc_id], 6),
            }
            for doc_id in ranked_ids[:k]
        ]


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is missing from .env")

    search_engine = HybridRunbookSearch()
    search_engine.build_index()

    query = "Application memory usage is high and the service is crashing"
    results = search_engine.search(query, k=3)

    print(f"\nQuery: {query}")
    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print(f"Source: {result['source']}")
        print(f"Score: {result['score']}")
        print(result["content"])