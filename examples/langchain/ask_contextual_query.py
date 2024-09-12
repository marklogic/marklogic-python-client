# Based on example at
# https://python.langchain.com/docs/use_cases/question_answering/quickstart .

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_openai import AzureChatOpenAI
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from marklogic import Client
from marklogic_contextual_query_retriever import (
    MarkLogicContextualQueryRetriever,
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


question = sys.argv[1]

retriever = MarkLogicContextualQueryRetriever.create(
    Client("http://localhost:8003", digest=("langchain-user", "password"))
)
retriever.collections = [sys.argv[2]]
retriever.max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 10
if len(sys.argv) > 4:
    retriever.query_type = sys.argv[4]

load_dotenv()

prompt = hub.pull("rlm/rag-prompt")
# Note that the Azure OpenAI API key, the Azure OpenAI Endpoint, and the OpenAI API
# Version, are all read from the environment automatically.
llm = AzureChatOpenAI(
    model_name=os.getenv("AZURE_LLM_DEPLOYMENT_NAME"),
    azure_deployment=os.getenv("AZURE_LLM_DEPLOYMENT_NAME"),
    temperature=0,
    max_tokens=None,
    timeout=None,
)

contextual_query = {
    "query": {
        "queries": [
            {
                "near-query": [
                    {"word-query": ["role"]},
                    {"word-query": ["assistant"]},
                ]
            },
        ]
    },
}
chat_context = {"question": question, "contextual_query": contextual_query}


def get_question():
    return chat_context["question"]


rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough().pick("question"),
    }
    | prompt
    | llm
    | StrOutputParser()
)
print(rag_chain.invoke(input=chat_context))
