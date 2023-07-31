---
layout: default
title: Managing Documents
nav_order: 3
has_children: true
permalink: /docs/managing-documents
---

The [/v1/documents endpoint](https://docs.marklogic.com/REST/client/management) in the MarkLogic REST API simplifies
operations that involve writing or reading a single document. It also supports operations that involve multiple 
documents, though those require use of a potentially complex multipart HTTP request or response. The MarkLogic Python
client simplifies those operations by hiding the details of multipart requests and responses.

## Setup for examples

The examples shown in [Reading Documents](reading.md) and [Searching Documents](searching.md) assume that you have 
created a new MarkLogic user named "python-user" as described in the [Getting Started](getting-started.md) guide. 
The examples also depend on documents being created by the below script. If you would like to run each of the examples, 
please run the script below, which will create a `Client` instance that interacts with the out-of-the-box "Documents"
database in MarkLogic.

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
