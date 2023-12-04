This example project is based on the 
[langchain example retriever](https://python.langchain.com/docs/use_cases/question_answering), 
using the same dataset as shown in that example, but with the dataset loaded into MarkLogic.

To try out this project, use docker-compose to instantiate a new MarkLogic 
instance with port 8003 available (you can use your own MarkLogic instance too, just be sure that port 8003
is available):

    docker-compose up -d --build

Then deploy a small REST API application to MarkLogic, which includes a basic non-admin MarkLogic user 
named `langchain-user`:

    ./gradlew -i mlDeploy

Next, create a new Python virtual environment - [pyenv](https://github.com/pyenv/pyenv) is recommended for this - 
and install the 
[langchain example dependencies](https://python.langchain.com/docs/use_cases/question_answering/#dependencies) ,
along with the [MarkLogic Python client](https://pypi.org/project/marklogic-python-client/): 

    pip install -U langchain openai chromadb langchainhub bs4 tiktoken marklogic_python_client

Then run the following Python program to load text data into two different collections in the 
`langchain-test-content` database:

    python load_data.py

Then run the following to ask a question with the results augmented via the `marklogic_retriever.py` module in this
project; you will be prompted for an OpenAI API key when you run this, which you can type or paste in:

    python ask.py "What is task decomposition?" posts

The retriever uses a [cts.similarQuery](https://docs.marklogic.com/cts.similarQuery) to select from the documents 
loaded via `load_data.py`. It defaults to a page length of 10. You can change this by providing a command line
argument - e.g.:

    python ask.py "What is task decomposition?" posts 15

Example of a good question for the "sotu" collection:

    python ask.py "What are economic sanctions?" sotu 20

To use a word query instead of a similar query, along with a set of drop words, specify "word" as the 4th argument:

    python ask.py "What are economic sanctions?" sotu 20 word
