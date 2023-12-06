# Based on example at
# https://python.langchain.com/docs/use_cases/question_answering.

import sys
from dotenv import load_dotenv
from langchain import hub
from langchain.chat_models import ChatOpenAI
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from marklogic import Client
from marklogic_retriever import MarkLogicRetriever


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


question = sys.argv[1]

retriever = MarkLogicRetriever.create(
    Client("http://localhost:8003", digest=("langchain-user", "password"))
)
retriever.collections = [sys.argv[2]]
retriever.max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 10
if len(sys.argv) > 4:
    retriever.query_type = sys.argv[4]

load_dotenv()

prompt = hub.pull("rlm/rag-prompt")
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)
print(rag_chain.invoke(question))
