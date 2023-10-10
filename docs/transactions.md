---
layout: default
title: Managing transactions
nav_order: 6
---

The [MarkLogic REST transactions service](https://docs.marklogic.com/REST/client/transaction-management)
supports managing a transaction that can be referenced in 
multiple separate calls to other REST API endpoints, with all calls being committed or 
rolled back together. The MarkLogic Python client simplifies usage of these endpoints
via a `Transaction` class that is also a 
[Python context manager](https://docs.python.org/3/reference/datamodel.html#context-managers), 
thereby allowing it to handle committing or rolling back the transaction without any user 
involvement.

The following example demonstrates writing documents via multiple calls to MarkLogic, 
all within the same REST API transaction; the example depends on first following the 
instructions in the [setup guide](example-setup.md):

```
from marklogic import Client
from marklogic.documents import Document
client = Client('http://localhost:8000', digest=('python-user', 'pyth0n'))

default_perms = {"rest-reader": ["read", "update"]}
doc1 = Document("/tx/doc1.json", {"doc": 1}, permissions=default_perms)
doc2 = Document("/tx/doc2.json", {"doc": 2}, permissions=default_perms)

with client.transactions.create() as tx:
    client.documents.write(doc1, tx=tx).raise_for_status()
    client.documents.write(doc2, tx=tx).raise_for_status()
```

The `client.transactions.create()` function returns a `Transaction` instance that acts
as the context manager. When the `with` block completes, the `Transaction` instance 
calls the REST API to commit the transaction. 

As of 1.1.0, each of the functions in the `client.documents` object can include a 
reference to the transaction to ensure that the `read` or `write` or `search` operation 
occurs within the REST API transaction.

## Ensuring a transaction is rolled back 

The `requests` function [`raise_for_status()`](https://requests.readthedocs.io/en/latest/user/quickstart/#errors-and-exceptions)
is used in the example above to ensure that if a request fails, an error is thrown, 
causing the transaction to be rolled back. The following example demonstrates a rolled
back transaction due to an invalid JSON object that causes a `write` operation to fail:

```
doc1 = Document("/tx/doc1.json", {"doc": 1}, permissions=default_perms)
doc2 = Document("/tx/doc2.json", "invalid json", permissions=default_perms)

with client.transactions.create() as tx:
    client.documents.write(doc1, tx=tx).raise_for_status()
    client.documents.write(doc2, tx=tx).raise_for_status()
```

The above will cause a `requests` `HTTPError` instance to be thrown, and the first
document will not be written due to the transaction being rolled back.

You are free to check the status code of the response object returned
by each call as well; `raise_for_status()` is simply a commonly used convenience in the 
`requests` library. 

## Using the transaction request parameter

You can reference the transaction when calling any REST API endpoint that supports the 
optional `txid` request parameter. The following example demonstrates this, reusing the
same `client` instance from the first example:

```
with client.transactions.create() as tx:
    client.post("/v1/resources/my-resource", params={"txid": tx.id})
    client.delete("/v1/resources/other-resource", params={"txid": tx.id})
```

## Getting transaction status

You can get the status of the transaction via the `get_status()` function:

```
with client.transactions.create() as tx:
    print(f"Transaction status: {tx.get_status()}")
```