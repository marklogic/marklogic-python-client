# MarkLogic Python Client

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

Please see [the user guide](https://marklogic.github.io/marklogic-python-client/) to start using the client.
