# Based on example at
# https://python.langchain.com/docs/use_cases/question_answering/quickstart .

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from marklogic import Client
from marklogic_vector_query_retriever import (
    MarkLogicVectorQueryRetriever,
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


load_dotenv()
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.environ["AZURE_EMBEDDING_DEPLOYMENT_NAME"]
)
retriever = MarkLogicVectorQueryRetriever.create(
    Client("http://localhost:8003", digest=("langchain-user", "password")),
    embedding_generator=embeddings,
)
retriever.collections = [sys.argv[2]]
retriever.max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 10
if len(sys.argv) > 4:
    retriever.query_type = sys.argv[4]

question = sys.argv[1]

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

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
print(rag_chain.invoke(question))
