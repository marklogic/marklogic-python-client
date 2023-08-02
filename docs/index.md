---
layout: default
title: Introduction
nav_order: 1
---

**Until the 1.0 release is available**, please follow the instructions in the CONTRIBUTING.md file for installing the 
MarkLogic Python client into a Python virtual environment (this notice will be removed before the release).

The [Python `requests` library](https://pypi.org/project/requests/) allows Python developers to easily create 
applications that communicate with the [MarkLogic REST API](https://docs.marklogic.com/guide/rest-dev). The 
MarkLogic Python Client further simplifies usage of the `requests` library by supporting common authentication 
strategies with MarkLogic and improving the user experience with some of the more common endpoints in the MarkLogic
REST API.

An instance of the client can be easily created and then used in the exact same way as the `requests` API:

```
from marklogic import Client
client = Client("http://localhost:8000", digest=("python-user", "pyth0n"))
response = client.get("/v1/search", params={"q": "marklogic and python", "pageLength": 100})
```

The example above and the examples throughout this documentation depend on a MarkLogic user named "python-user". 
If you wish to try these examples on your own installation of MarkLogic, please see [the setup guide](/setup)
for instructions on creating this user. 

Otherwise, please see the [guide on creating a client](/client) for more information on connecting to a 
MarkLogic REST API instance. The [guide on managing documents](/documents) provides
more information on how the client simplifies writing and reading multiple documents in a single request.

