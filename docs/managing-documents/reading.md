---
layout: default
title: Reading documents
parent: Managing documents
nav_order: 2
permalink: /documents/reading
---

The [GET /v1/documents](https://docs.marklogic.com/REST/GET/v1/documents) endpoint in the MarkLogic REST API supports
reading multiple documents with metadata via a multipart/mixed HTTP response. The MarkLogic Python client simplifies
handling the response by converting it into a list of `Document` instances via the `client.documents.read` method. 

## Table of contents
{: .no_toc .text-delta }

- TOC
{:toc}

## Setup for examples

The examples below all assume that you have created a new MarkLogic user named "python-user" as described in the 
[setup guide](../example-setup.md). To run these examples, please run the following script first, which will 
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
# Read multiple documents via a list of URIs.
docs = client.documents.read(["/doc1.json", "/doc2.xml", "/doc3.bin"])
assert len(docs) == 3

# Read a single document, verifying that it does not have any metadata.
doc = client.documents.read("/doc1.json")[0]
assert "/doc1.json" == doc.uri
assert "example one" == doc.content["text"]
assert doc.collections is None
assert doc.permissions is None
assert doc.quality is None
assert doc.metadata_values is None
assert doc.properties is None
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

## Providing additional arguments

The `client.documents.read` method provides a `**kwargs` argument, so you can pass in any other arguments you would
normally pass to `requests`. For example:

```
uris = ["/doc1.json", "/doc2.xml", "/doc3.bin"]
docs = client.documents.read(uris, params={"database": "Documents"})
print(docs)
```

Please see [the application developer's guide](https://docs.marklogic.com/guide/rest-dev/documents#id_80116)
for more information on reading documents.

## Returning the original HTTP response

Starting in the 1.1.0 release, the `client.documents.search` method accepts a 
`return_response` argument. When that argument is set to `True`, the original response 
is returned. This can be useful for custom processing of the response or debugging requests.

## Referencing a transaction

Starting in the 1.1.0 release, you can reference a 
[REST API transaction](https://docs.marklogic.com/REST/client/transaction-management) via the `tx` 
argument. See [the guide on transactions](../transactions.md) for further information.

## Error handling

If the `client.documents.read` method receives an HTTP response with a status code of 200, then the client will return
a list of `Document` instances. For any other status code, the client will return the `requests` `Response` object, 
providing access to the error details returned by the MarkLogic REST API.

The `status_code` and `text` fields in the `Response` object will typically be of the most interest when 
debugging a problem. Please see 
[Response API documentation](https://docs.python-requests.org/en/latest/api/#requests.Response) for complete information on what's available in this object.

