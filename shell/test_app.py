# Startup script when wanting to hit the test-app server on port 8030 in a Python shell.
from marklogic import Client

client = Client("http://localhost:8030", digest=("python-test-user", "password"))
