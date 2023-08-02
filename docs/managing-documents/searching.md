---
layout: default
title: Searching documents
parent: Managing documents
nav_order: 3
permalink: /documents/searching
---

The [POST /v1/search endpoint](https://docs.marklogic.com/REST/POST/v1/search) in the MarkLogic REST API supports
returning content and metadata for each matching document. Similar to reading multiple documents via the 
[GET /v1/documents endpoint](https://docs.marklogic.com/REST/GET/v1/documents, the data is returned in a multipart
HTTP response. The MarkLogic Python client simplifies use of this operation by returning a list of `Document` instances
via the `client.documents.search` method.

## Setup for examples

The examples below all assume that you have created a new MarkLogic user named "python-user" as described in the 
[setup guide](/setup). To run these examples, please run the following script first, which will 
create a `Client` instance that interacts with the out-of-the-box "Documents" database in MarkLogic:

```
from marklogic import Client
from marklogic.documents import Document, DefaultMetadata

client = Client('http://localhost:8000', digest=('python-user', 'pyth0n'))
client.documents.write([
    DefaultMetadata(permissions={"rest-reader": ["read", "update"]}, collections=["python-example"]),
    Document("/doc1.json", {"text": "example one"}),
    Document("/doc2.json", {"text": "example two"})
])
```

## Searching via a search string

The search endpoint in the REST API provides several ways of submitting a query. The simplest approach is by submitting
a search string that utilizes the
[the MarkLogic search grammar](https://docs.marklogic.com/guide/search-dev/search-api#id_41745):

```
# Find documents with the term "example" in them.
docs = client.documents.search("example")
assert len(docs) == 2

# Find documents with the term "one" in them.
docs = client.documents.search("one")
assert len(docs) == 1
```

The search string in the example corresponds to the `q` argument, which is the first argument in the method and thus
does not need to be named. 

## Searching via a complex query

More complex queries can be submitted via the `query` parameter. The value of this parameter must be one of the
following:

1. A [structured query](https://docs.marklogic.com/guide/search-dev/structured-query#).
2. A [serialized CTS query](https://docs.marklogic.com/guide/rest-dev/search#id_30577).
3. A [combined query](https://docs.marklogic.com/guide/rest-dev/search#id_69918).

For each of the above approaches, the query can be either a dictionary (for use when defining the query via JSON) or 
a string of XML. Based on the type, the client will set the appropriate Content-type header. 

Examples of a structured query:

```
# JSON
docs = client.documents.search(query={"query": {"term-query": {"text": "example"}}})
assert len(docs) == 2

# XML
query = "<query xmlns='http://marklogic.com/appservices/search'>\
        <term-query><text>example</text></term-query></query>"
docs = client.documents.search(query=query)
assert len(docs) == 2
```

Examples of a serialized CTS query:

```
# JSON
query = {"ctsquery": {"wordQuery": {"text": "example"}}}
docs = client.documents.search(query=query)
assert len(docs) == 2

# XML
query = "<word-query xmlns='http://marklogic.com/cts'><text>world</text></word-query>"
docs = client.documents.search(query=query)
assert len(docs) == 2
```

Examples of a combined query:

```
# JSON
options = {"constraint": {"name": "c1", "word": {"element": {"name": "text"}}}}
query = {
    "search": {"options": options},
    "qtext": "c1:example",
}
docs = client.documents.search(query=query)
assert len(docs) == 2

# XML
query = "<search xmlns='http://marklogic.com/appservices/search'><options>\
        <constraint name='c1'><word><element name='text'/></word></constraint>\
        </options><qtext>c1:example</qtext></search>"
docs = client.documents.search(query=query)
assert len(docs) == 2
```

## Controlling search results

The search endpoint supports a variety of parameters for controlling the search request. For convenience, several of the
more commonly used parameters are available as arguments in the `client.documents.search` method:

```
# Specify the starting point and page length.
docs = client.documents.search("example", start=2, page_length=5)
assert len(docs) == 1

# Search via a collection without any search string.
docs = client.documents.search(collections=["python-example"])
assert len(docs) == 2
```

Similar to [reading documents](/documents/reading), you can use the `categories` argument to control what is returned for 
each matching document:

```
# Retrieve all content and metadata for each matching document.
docs = client.documents.search("example", categories=["content", "metadata"])
assert "python-example" in docs[0].collections
assert "python-example" in docs[1].collections

# Retrieve only permissions for each matching document.
docs = client.documents.search("example", categories=["permissions"])
assert docs[0].content is None
assert docs[1].content is None
```

The `client.documents.search` method provides a `**kwargs` argument, so you can pass in any other arguments you would
normally pass to `requests`, such as a `params` argument that specifies additional parameters:


```
docs = client.documents.search("example", params={"database": "Documents"})
assert len(docs) == 2
```

## Error handling

A POST call to the /v1/search endpoint in MarkLogic will return an HTTP response with a status code of 200 for a
successful request. For any other status code, the `client.documents.search` method will the `requests` `Response` object,
providing access to the error details returned by MarkLogic.