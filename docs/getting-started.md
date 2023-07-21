---
layout: default
title: Getting Started
nav_order: 2
---

**Until the 1.0 release is available**, please follow the instructions in the CONTRIBUTING.md file for installing the 
MarkLogic Python client into a Python virtual environment.

## Connecting to MarkLogic

The `Client` class is the primary API to interact with in the MarkLogic Python client. The
`Client` class extends the `requests` 
[`Session` class](https://docs.python-requests.org/en/latest/user/advanced/#session-objects), thus exposing all methods
found in both the `Session` class and the `requests` API. You can therefore use a `Client` object in the same manner 
as you'd use either the `Session` class or the `requests` API.

To try out any of the examples below or in the rest of this guide, you will first need to create a new MarkLogic user. 
To do so, please go to the Admin application for your MarkLogic instance - e.g. if you are running MarkLogic locally, 
this will be at <http://localhost:8001>, and you will authenticate as your "admin" user. Then perform the following 
steps to create a new user:

1. Click on "Users" in the "Security" box.
2. Click on "Create".
3. In the form, enter "python-user" for "User Name" and "pyth0n" as the password. 
4. Scroll down until you see the "Roles" section. Click on the "rest-reader" and "rest-writer" checkboxes. 
5. Scroll to the top or bottom and click on "OK" to create the user.

A `Client` instance can be constructed either by providing a base URL for all requests along with authentication:

```
from marklogic import Client
client = Client('http://localhost:8000', digest=('python-user', 'pyth0n'))
```

Or via separate arguments for each of the parts of a base URL:

```
from marklogic import Client
client = Client(host='localhost', port='8000', digest=('python-user', 'pyth0n'))
```

After constructing a `Client` instance, each of the methods in the `requests` API for sending an HTTP request can be 
used without needing to specify the base URL nor the authentication again. For example:

```
response = client.post('/v1/search')
response = client.get('/v1/documents', params={'uri': '/my-doc.json'})
```

Because the `Client` class extends the `Sessions` class, it can be used as a context manager:

```
with Client('http://localhost:8000', digest=('python-user', 'pyth0n')) as client:
    response = client.post('/v1/search')
    response = client.get('/v1/documents', params={'uri': '/my-doc.json'})
```

## Authentication

The `Client` constructor includes a `digest` argument as a convenience for using digest authentication:

```
from marklogic import Client
client = Client('http://localhost:8000', digest=('python-user', 'pyth0n'))
```

An `auth` argument is also available for using any authentication strategy that can be configured
[via the requests `auth` argument](https://requests.readthedocs.io/en/latest/user/advanced/#custom-authentication). For 
example, just like with `requests`, a tuple can be passed to the `auth` argument to use basic authentication:

```
from marklogic import Client
client = Client('http://localhost:8000', auth=('python-user', 'pyth0n'))
```

### MarkLogic Cloud Authentication

When connecting to a [MarkLogic Cloud instance](https://developer.marklogic.com/products/cloud/), you will need to set 
the `cloud_api_key` and `base_path` arguments. You only need to specify a `host` as well, as port 443 and HTTPS will be
used by default. For example:

```
from marklogic import Client
client = Client(host='example.marklogic.cloud', cloud_api_key='some-key-value', base_path='/ml/example/manage')
```

You may still use a full base URL if you wish:

```
from marklogic import Client
client = Client('https://example.marklogic.cloud', cloud_api_key='some-key-value', base_path='/ml/example/manage')
```

MarkLogic Cloud uses an access token for authentication; the access token is generated using the API key value. In some 
scenarios, you may wish to set the token expiration time to a value other than the default used by MarkLogic Cloud. To 
do so, set the `cloud_token_duration` argument to a number greater than zero that defines the token duration in 
minutes:

```
from marklogic import Client
# Sets a token duration of 10 minutes.
client = Client(host='example.marklogic.cloud', cloud_api_key='some-key-value', base_path='/ml/example/manage', 
    cloud_token_duration=10)
```

## SSL 

Configuring SSL connections is the same as 
[documented for the `requests` library](https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification). 
As a convience, the `Client` constructor includes a `verify` argument so that it does not need to be configured on the 
`Client` instance after it's been constructed nor on every request:

```
from marklogic import Client
client = Client('https://localhost:8000', digest=('python-user', 'pyth0n'), verify='/path/to/cert.pem')
```

When specifying the base URL via separate arguments, the `scheme` argument can be set for HTTPS connections:

```
from marklogic import Client
client = Client(host='localhost', port='8000', scheme='https', digest=('python-user', 'pyth0n'), verify=False)
```
