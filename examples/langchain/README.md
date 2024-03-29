# Example langchain retriever

This project demonstrates one approach for implementing a 
[langchain retriever](https://python.langchain.com/docs/modules/data_connection/)
that allows for 
[Retrieval Augmented Generation (RAG)](https://python.langchain.com/docs/use_cases/question_answering/)
to be supported via MarkLogic and the MarkLogic Python Client. This example uses the same data as in 
[the langchain RAG quickstart guide](https://python.langchain.com/docs/use_cases/question_answering/quickstart), 
but with the data having first been loaded into MarkLogic.

**This is only intended as an example** of how easily a langchain retriever can be developed
using the MarkLogic Python Client. The queries in this example are simple and naturally 
do not have any knowledge of how your data is modeled in MarkLogic. You are encouraged to use 
this as an example for developing your own retriever, where you can build a query based on a 
question submitted to langchain that fully leverages the indexes and data models in your MarkLogic
application. Additionally, please see the 
[langchain documentation on splitting text](https://python.langchain.com/docs/modules/data_connection/document_transformers/). You may need to restructure your data so that you have a larger number of 
smaller documents in your database so that you do not exceed the limit that langchain imposes on how
much data a retriever can return.

# Setup

To try out this project, use [docker-compose](https://docs.docker.com/compose/) to instantiate a new MarkLogic 
instance with port 8003 available (you can use your own MarkLogic instance too, just be sure that port 8003
is available):

    docker-compose up -d --build

Then deploy a small REST API application to MarkLogic, which includes a basic non-admin MarkLogic user 
named `langchain-user`:

    ./gradlew -i mlDeploy

Next, create a new Python virtual environment - [pyenv](https://github.com/pyenv/pyenv) is recommended for this - 
and install the 
[langchain example dependencies](https://python.langchain.com/docs/use_cases/question_answering/quickstart#dependencies),
along with the MarkLogic Python Client: 

    pip install -U langchain langchain_openai langchain-community langchainhub openai chromadb bs4 marklogic_python_client

Then run the following Python program to load text data from the langchain quickstart guide 
into two different collections in the `langchain-test-content` database:

    python load_data.py

Create a ".env" file to hold your OpenAI API key:

    echo "OPENAI_API_KEY=<your key here>" > .env

# Testing the retriever

You are now ready to test the example retriever. Run the following to ask a question with the 
results augmented via the `marklogic_retriever.py` module in this project; you will be 
prompted for an OpenAI API key when you run this, which you can type or paste in:

    python ask.py "What is task decomposition?" posts

The retriever uses a [cts.similarQuery](https://docs.marklogic.com/cts.similarQuery) to select from the documents 
loaded via `load_data.py`. It defaults to a page length of 10. You can change this by providing a command line
argument - e.g.:

    python ask.py "What is task decomposition?" posts 15

Example of a question for the "sotu" (State of the Union speech) collection:

    python ask.py "What are economic sanctions?" sotu 20

To use a word query instead of a similar query, along with a set of drop words, specify "word" as the 4th argument:

    python ask.py "What are economic sanctions?" sotu 20 word
