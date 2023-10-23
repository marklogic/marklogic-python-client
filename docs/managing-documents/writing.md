---
layout: default
title: Writing documents
nav_order: 1
parent: Managing documents
permalink: /documents/writing
---

The [POST /v1/documents](https://docs.marklogic.com/REST/POST/v1/documents) endpoint in the MarkLogic REST API supports
writing multiple documents with metadata via a multipart HTTP request. The MarkLogic Python client 
simplifies the use of this endpoint via the `client.documents.write` method and the `Document`
class. 

The examples below all assume that you have created a new MarkLogic user named "python-user" as described in the 
[setup guide](../example-setup.md). In addition, each of the examples below requires the following `Client` instance to be created 
first:

```
from marklogic import Client
client = Client('http://localhost:8000', digest=('python-user', 'pyth0n'))
```

## Writing documents with metadata

Writing a document requires specifying a URI, the document content, and at least one update permission (a user with the
"admin" role does not need to specify an update permission, but using such a user in an application is not encouraged).
The example below demonstrates this; the `default_perms` variable is used in subsequent examples. 

```
from marklogic.documents import Document
default_perms = {"rest-reader": ["read", "update"]}
response = client.documents.write(Document("/doc1.json", {"doc": 1}, permissions=default_perms))
```

The `write` method returns a [Response instance](https://requests.readthedocs.io/en/latest/api/#requests.Response) 
from the `requests` API, giving you access to everything returned by the MarkLogic REST API.

The `Document` class supports all of the types of metadata that can be assigned to a document:

```
doc = Document(
    "/doc1.json", 
    {"doc": 1},
    permissions=default_perms,
    collections=["c1", "c2"],
    quality=10,
    metadata_values={"key1": "value1", "key2": "value2"},
    properties={"prop1": "value1", "prop2": 2}
)
client.documents.write(doc)
```

Multiple documents can be written in a single call, each with their own metadata:

```
client.documents.write([
    Document("/doc1.json", {"doc": 1}, permissions=default_perms, collections=["example"]),
    Document("/doc2.json", {"doc": 2}, permissions=default_perms, quality=5),
])
```

## Writing documents with different content types

The examples above create documents with a dictionary as content, resulting in JSON documents in MarkLogic. An XML 
document can be created with content defined via a string, including in the same request that creates a JSON document:

```
client.documents.write([
    Document("/doc1.json", {"doc": 1}, permissions=default_perms),
    Document("/doc2.xml", "<doc>2</doc>", permissions=default_perms),
])
```

Binary documents can be created by passing in binary content:

```
client.documents.write([Document("/doc1.bin", b"example content", permissions=default_perms)])
```

A `Document` has a `content_type` attribute that allows for explicitly defining the 
mimetype of a document. This feature is useful in a scenario where MarkLogic does not 
have a mimetype registered for the URI extension, or there is no extension:

```
client.documents.write([Document(
    "/doc1", "some text", 
    permissions=default_perms, 
    content_type="text/plain"
)])
```

## Specifying default metadata

The documents REST endpoint allows for [default metadata](https://docs.marklogic.com/guide/rest-dev/bulk#id_16015) to 
be specified for one or more documents. The client supports this by allowing a `DefaultMetadata` instance to be 
included before any number of `Document` instances. Each `Document` will use the metadata in the `DefaultMetadata`
instance, unless it specifies its own metadata. 

Consider the following example:

```
from marklogic.documents import Document, DefaultMetadata
client.documents.write([
    DefaultMetadata(permissions=default_perms, collections=["example"]),
    Document("/doc1.json", {"doc": 1}),
    Document("/doc2.json", {"doc": 2}, permissions=default_perms, quality=10)
])
```

The first document will be written with the metadata specified in the first `DefaultMetadata` instance. The second
document will not use the default metadata since it specifies its own metadata. It will have the same permissions, but 
it will have a quality score of 10 and will not be assigned to the "example" collection.

Multiple instances of `DefaultMetadata` can be included in the list passed to the `client.documents.write` method. If
a `Document` instance does not specify any metadata, it will use the metadata found in the `DefaultMetadata` instance
that occurs most recently before it in the list (if one exists). 

## Additional control over writing a document

The "Usage Notes" section in the [POST /v1/documents documentation](https://docs.marklogic.com/REST/POST/v1/documents)
describes how several parameters can be used to control how each document is written. Those parameters are:

1. `extension` = a URI suffix for use when [MarkLogic generates the URI](https://docs.marklogic.com/guide/rest-dev/bulk#id_86768).
2. `directory` = a URI prefix for use when MarkLogic generates the URI.
3. `repair` = level of XML repair to perform for an XML document.
4. `extract` = whether or not to extract metadata for a binary document.
5. `versionId` = can be used when optimistic locking is enabled.
6. `temporal-document` = the logical document URI for a document in a temporal collection.

Each of these can be specified on a `Document` instance, though `versionId` and `temporal-document` are named 
`version_id` and `temporal_document` to align with Python naming conventions.

The following shows an example of writing a document without specifying a URI, where the written document will have a 
URI beginning with "/example/" and ending with ".json", with MarkLogic adding a random identifier in between to 
construct the URI:

```
client.documents.write([Document(None, {"doc": 1}, extension=".json", directory="/example/")])
```

## Providing additional arguments

The `client.documents.write` method provides a `**kwargs` argument, so you can pass in any other arguments you would
normally pass to `requests`. For example:

```
response = client.documents.write(Document("/doc1.json", {"doc": 1}, permissions=default_perms), params={"database": "Documents"})
```

Please see [the application developer's guide](https://docs.marklogic.com/guide/rest-dev/documents#id_11953) for 
more information on writing documents.

## Referencing a transaction

Starting in the 1.1.0 release, you can reference a 
[REST API transaction](https://docs.marklogic.com/REST/client/transaction-management) via the `tx` 
argument. See [the guide on transactions](../transactions.md) for further information.


## Error handling

Because the `client.documents.write` method returns a `requests Response` object, any error that occurs during 
processing of the request will be captured within that `Response` object. The client does not attempt to provide any 
additional information, as the MarkLogic REST API will already provide details within the response body and potentially
the response headers as well.

The `status_code` and `text` fields in the `Response` object will typically be of the most interest when 
debugging a problem. Please see 
[Response API documentation](https://docs.python-requests.org/en/latest/api/#requests.Response) for complete information on what's available in this object.
