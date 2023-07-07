---
layout: default
title: Getting Started
nav_order: 2
---

**Until the 1.0 release is available**, please follow the instructions in the CONTRIBUTING.md file for installing the 
MarkLogic Python client into a Python virtual environment.

## Connecting to MarkLogic

(TODO This will almost certainly be reorganized before the 1.0 release.)

The `Client` class is the primary API to interact with in the MarkLogic Python client. The
`Client` class extends the `requests` 
[`Session` class](https://docs.python-requests.org/en/latest/user/advanced/#session-objects), thus exposing all methods
found in both the `Session` class and the `requests` API. You can therefore use a `Client` object in the same manner 
as you'd use either the `Session` class or the `requests` API.

A `Client` instance can be constructed either by providing a base URL for all requests along with authentication:

    from marklogic.client import Client
    client = Client('http://localhost:8030', digest=('username', 'password'))

Or via separate arguments for each of the parts of a base URL:

    from marklogic.client import Client
    client = Client(host='localhost', port='8030', digest=('username', 'password'))

After constructing a `Client` instance, each of the methods in the `requests` API for sending an HTTP request can be 
used without needing to specify the base URL nor the authentication again. For example:

    response = client.post('/v1/search')
    response = client.get('/v1/documents', params={'uri': '/my-doc.json'})

Because the `Client` class extends the `Sessions` class, it can be used as a context manager:

    with Client('http://localhost:8030', digest=('username', 'password')) as client:
        response = client.post('/v1/search')
        response = client.get('/v1/documents', params={'uri': '/my-doc.json'})

## Authentication

The `Client` constructor includes a `digest` argument as a convenience for using digest authentication:

    from marklogic.client import Client
    client = Client('http://localhost:8030', digest=('username', 'password'))

An `auth` argument is also available for using any authentication strategy that can be configured
[via the requests `auth` argument](https://requests.readthedocs.io/en/latest/user/advanced/#custom-authentication). For 
example, just like with `requests`, a tuple can be passed to the `auth` argument to use basic authentication:

    from marklogic.client import Client
    client = Client('http://localhost:8030', auth=('username', 'password'))

## SSL 

Configuring SSL connections is the same as 
[documented for the `requests` library](https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification). 
As a convience, the `Client` constructor includes a `verify` argument so that it does not need to be configured on the 
`Client` instance after it's been constructed nor on every request:

    from marklogic.client import Client
    client = Client('https://localhost:8030', digest=('username', 'password'), verify='/path/to/cert.pem')

When specifying the base URL via separate arguments, the `scheme` argument can be set for HTTPS connections:

    from marklogic.client import Client
    client = Client(host='localhost', port='8030', scheme='https', digest=('username', 'password'), verify=False)
