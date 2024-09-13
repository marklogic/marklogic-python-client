# Based on example at
# https://python.langchain.com/docs/use_cases/question_answering/quickstart .

import bs4
from dotenv import load_dotenv
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from marklogic import Client
from marklogic.documents import DefaultMetadata, Document
import os

load_dotenv()
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.environ["AZURE_EMBEDDING_DEPLOYMENT_NAME"]
)

loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100
)
splits = text_splitter.split_documents(docs)

client = Client("http://localhost:8003", digest=("langchain-user", "password"))

marklogic_docs = [DefaultMetadata(collections="posts_with_embeddings")]
for split in splits:
    text = split.page_content
    embedding = embeddings.embed_query(text)
    doc = Document(
        None,
        {"text": text, "embedding": embedding},
        extension=".json",
        directory="/post/",
    )
    marklogic_docs.append(doc)

client.documents.write(marklogic_docs)
print(
    f"Number of documents written to collection 'posts': {len(marklogic_docs)-1}"
)

loader = WebBaseLoader(
    web_paths=(
        "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/docs/modules/state_of_the_union.txt",
    )
)
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100
)
splits = text_splitter.split_documents(docs)

marklogic_docs = [DefaultMetadata(collections="sotu_with_embeddings")]
for split in splits:
    text = split.page_content
    embedding = embeddings.embed_query(text)
    doc = Document(
        None,
        {"text": text, "embedding": embedding},
        extension=".json",
        directory="/sotu/",
    )
    marklogic_docs.append(doc)

client.documents.write(marklogic_docs)
print(
    f"Number of documents written to collection 'sotu': {len(marklogic_docs)-1}"
)
