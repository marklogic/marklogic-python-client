from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from marklogic import Client

"""
Modeled after
https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/retrievers/elastic_search_bm25.py ,
which uses a `create` method instead of __init__.
"""


class MarkLogicSimilarQueryRetriever(BaseRetriever):

    client: Client
    max_results: int = 10
    collections: List[str] = []
    query_type: str = "similar"
    drop_words = [
        "did",
        "the",
        "about",
        "a",
        "an",
        "is",
        "are",
        "what",
        "say",
        "do",
        "was",
        "that",
    ]

    @classmethod
    def create(cls, client: Client):
        return cls(client=client)

    def _get_relevant_documents(self, query: str) -> List[Document]:
        words = []
        for word in query.split():
            if word.lower() not in self.drop_words:
                words.append(word.lower().replace("?", ""))

        word_query = "<word-query xmlns='http://marklogic.com/cts'>"
        for word in words:
            word_query = f"{word_query}<text>{word}</text>"
        word_query = f"{word_query}</word-query>"

        similar_query = f"""<similar-query xmlns='http://marklogic.com/cts'>
        <node><text xmlns=''>{query}</text></node></similar-query>"""

        cts_query = word_query if self.query_type == "word" else similar_query

        print(f"Searching with query: {cts_query}")
        results = self.client.documents.search(
            query=cts_query,
            page_length=self.max_results,
            collections=self.collections,
        )
        print(f"Count of matching MarkLogic documents: {len(results)}")
        return map(lambda doc: Document(page_content=doc.content), results)
