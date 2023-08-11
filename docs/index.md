---
layout: default
title: Introduction
nav_order: 1
---

The [Python `requests` library](https://pypi.org/project/requests/) allows Python developers to easily create 
applications that communicate with the [MarkLogic REST API](https://docs.marklogic.com/guide/rest-dev). The 
MarkLogic Python Client further simplifies usage of the `requests` library by supporting common authentication 
strategies with MarkLogic and improving the user experience with some of the more common endpoints in the MarkLogic
REST API.

The client requires Python 3.9 or higher. It is [available at PyPI](https://pypi.org/project/marklogic-python-client/)
and can be [installed via pip](https://packaging.python.org/en/latest/guides/tool-recommendations/):

    pip install marklogic-python-client

The client's sole dependency with MarkLogic is on the MarkLogic REST API. MarkLogic 10 and higher is supported, and 
earlier versions of MarkLogic that support the MarkLogic REST API are likely to work as well though are not tested.

An instance of the client can be used in the exact same way as the `requests` API:

```
from marklogic import Client
client = Client("http://localhost:8000", digest=("python-user", "pyth0n"))
response = client.get("/v1/search", params={"q": "marklogic and python", "pageLength": 100})
```

The example above and the examples throughout this documentation depend on a MarkLogic user named "python-user". 
If you wish to try these examples on your own installation of MarkLogic, please see [the setup guide](example-setup.md)
for instructions on creating this user. 

Otherwise, please see the [guide on creating a client](creating-client.md) for more information on connecting to a 
MarkLogic REST API instance. The [guide on managing documents](managing-documents/managing-documents.md) provides
more information on how the client simplifies writing and reading multiple documents in a single request.

