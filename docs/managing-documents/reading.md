---
layout: default
title: Reading Documents
parent: Managing Documents
nav_order: 3
---

The [GET /v1/documents](https://docs.marklogic.com/REST/GET/v1/documents) endpoint in the MarkLogic REST API supports
reading multiple documents with metadata via a multipart/mixed HTTP response. The MarkLogic Python client simplifies
handling the response by converting it into a list of `Document` instances via the `client.documents.read` method. 

## Setup for examples

The examples below all assume that you have created a new MarkLogic user named "python-user" as described in the 
[Getting Started](getting-started.md) guide. To run these examples, please run the following script first, which will 
create a `Client` instance that interacts with the out-of-the-box "Documents" database in MarkLogic:
```
from marklogic import Client
from marklogic.documents import Document, DefaultMetadata

client = Client('http://localhost:8000', digest=('python-user', 'pyth0n'))
client.documents.write([
    DefaultMetadata(permissions={"rest-reader": ["read", "update"]}, collections=["python-example"]),
    Document("/doc1.json", {"text": "example one"}),
    Document("/doc2.xml", "<text>example two</text>"),
    Document("/doc3.bin", b"binary example", permissions={"rest-reader": ["read", "update"]})
])
```

## Reading documents

A list of `Document` instances can be obtained for a list of URIs, where each `Document` has its `uri` and `content`
attributes populated but no metadata by default:

```
docs = client.documents.read(["/doc1.json", "/doc2.xml", "/doc3.bin"])
assert len(docs) == 3
```

The [requests toolbelt](https://toolbelt.readthedocs.io/en/latest/) library is used to process the multipart
HTTP response returned by MarkLogic. By default, the `content` attribute of each `Document` will be a binary value. 
The client will convert this into something more useful based on the content types in the table below:

| Content type | `content` attribute type |
| --- | --- |
| application/json | dictionary |
| application/xml | string |
| text/xml | string | 
| text/plain | string |

Thus, the `Document` with a URI of "/doc1.json" will have a dictionary as the value of its 
`content` attribute. The `Document` with a URI of "/doc2.xml" will have a string as the value of its `content`
attribute. And the `Docuemnt` with a URI of "/doc3.bin" will have a binary value for its `content` attribute.

A `Document` instance can be examined simply by printing or logging it; this will display all of the instance's 
changeable attributes, including the URI, content, and metadata:

```
doc = docs[0]
print(doc)

# Can always built-in Python vars method.
print(vars(doc))
```

## Reading documents with metadata

Metadata for each document can be retrieved via the `categories` argument. The acceptable values for this argument
match those of the `category` parameter in the [GET /v1/documents](https://docs.marklogic.com/REST/GET/v1/documents)
documentation: `content`, `metadata`, `metadata-values`, `collections`, `permissions`, `properties`, and `quality`.

The following shows different examples of configuring the `categories` argument:

```
uris = ["/doc1.json", "/doc2.xml", "/doc3.bin"]

# Retrieve content and all metadata for each document.
docs = client.documents.read(uris, categories=["content", "metadata"])
print(docs)

# Retrieve content, collections, and permissions for each document.
docs = client.documents.read(uris, categories=["content", "collections", "permissions"])
print(docs)

# Retrieve only collections for each document; the content attribute will be None.
docs = client.documents.read(uris, categories=["collections"])
print(docs)
```

# Error handling

A GET call to the /v1/documents endpoint in MarkLogic will return an HTTP response with a status code of 200 for a
successful request. For any other status code, the `client.documents.read` method will the `requests` `Response` object,
providing access to the error details returned by MarkLogic.
