---
layout: default
title: Reading Documents
nav_order: 4
---

The [GET /v1/documents](https://docs.marklogic.com/REST/GET/v1/documents) endpoint in the MarkLogic REST API supports
reading multiple documents with metadata via a multipart/mixed HTTP response. The MarkLogic Python client simplifies
handling the response by converting it into a list of `Document` instances via the `client.documents.read` method. 


The examples below all assume that you have constructed a `Client` instance already as described in the 
[Getting Started](getting-started.md) guide. The examples also assume the existence of documents with URIs of 
`/doc1.json`, `/doc2.xml`, and `/doc3.bin`.

## Reading documents

A list of `Document` instances can be obtained for a list of URIs, where each `Document` has its `uri` and `content`
attributes populated but no metadata by default:

    docs = client.documents.read(["/doc1.json", "/doc2.xml"])

The [requests toolbelt](https://toolbelt.readthedocs.io/en/latest/) library is used to process the multipart/mixed
HTTP response returned by MarkLogic. As a result, the `content` attribute of each `Document` will be a binary value. 
The client will convert this into something more useful based on the content types in the table below:

| Content type | `content` attribute type |
| --- | --- |
| application/json | dictionary |
| application/xml | string |
| text/xml | string | 
| text/plain | string |

## Reading documents with metadata

Metadata for each document can be retrieved via the `categories` argument. The acceptable values for this argument
match those of the `category` parameter in the [GET /v1/documents](https://docs.marklogic.com/REST/GET/v1/documents)
documentation: `content`, `metadata`, `metadata-values`, `collections`, `permissions`, `properties`, and `quality`.

The following shows different examples of configuring the `categories` argument:

```
uris = ["/doc1.json", "/doc2.xml"]

# Retrieve content and all metadata for each document.
docs = client.documents.read(uris, categories=["content", "metadata"])

# Retrieve content, collections, and permissions for each document.
docs = client.documents.read(uris, categories=["content", "collections", "permissions"])

# Retrieve only collections for each document; the content attribute will be None.
docs = client.documents.read(uris, categories=["collections"])
```

# Error handling

A GET call to the /v1/documents endpoint in MarkLogic will return an HTTP response with a status code of 200 for a
successful request. For any other status code, the `client.documents.read` method will the `requests` `Response` object,
providing access to the HTTP response returned by MarkLogic.
