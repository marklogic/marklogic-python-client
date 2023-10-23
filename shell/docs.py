# Startup script when wanting to hit port 8000 as the user that's setup in the
# documentation.

from marklogic import Client
from marklogic.documents import Document, DefaultMetadata

client = Client("http://localhost:8000", digest=("python-user", "pyth0n"))
