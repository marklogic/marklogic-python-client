from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import (
    BaseRetriever,
)
from marklogic import Client

"""
Modeled after
https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/retrievers/elastic_search_bm25.py ,
which uses a `create` method instead of __init__.
"""


class MarkLogicContextualQueryRetriever(BaseRetriever):

    client: Client
    max_results: int = 10
    collections: List[str] = []

    @classmethod
    def create(cls, client: Client):
        return cls(client=client)

    def _get_relevant_documents(
        self,
        chat_context: object,
    ) -> List[Document]:
        search_words = []
        for word in chat_context["question"].split():
            search_words.append(word.lower().replace("?", ""))
        term_query = {"term-query": {"text": search_words}}

        print(f"contextual_query: {chat_context['contextual_query']}")
        chat_context["contextual_query"]["query"]["queries"].append(term_query)

        print(f"Searching with query: {chat_context['contextual_query']}")
        results = self.client.documents.search(
            query=chat_context["contextual_query"],
            page_length=self.max_results,
            collections=self.collections,
        )
        print(f"Count of matching MarkLogic documents: {len(results)}")
        return map(lambda doc: Document(page_content=doc.content), results)
