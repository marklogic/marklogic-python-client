# Copyright (c) 2023-2025 Progress Software Corporation and/or its subsidiaries or affiliates. All Rights Reserved.


import requests
import time
from marklogic import Client
from marklogic.documents import Document
from requests.exceptions import HTTPError

PERMS = {"python-tester": ["read", "update"]}


def test_write_two_docs(client: Client):
    with client.transactions.create() as tx:
        collections = ["tx-test"]
        doc1 = Document("/t1.json", {}, permissions=PERMS, collections=collections)
        doc2 = Document("/t2.json", {}, permissions=PERMS, collections=collections)
        client.documents.write(doc1, tx=tx)
        client.documents.write(doc2, tx=tx)

        msg = "Neither doc should be returned since the read is outside the transaction"
        docs = client.documents.read(["/t1.json", "/t2.json"])
        assert len(docs) == 0, msg

        msg = "Both documents should be returned as the call is within the transaction"
        docs = client.documents.read(["/t1.json", "/t2.json"], tx=tx)
        assert len(docs) == 2, msg
        docs = client.documents.search(collections=collections, tx=tx)
        assert len(docs) == 2, msg
        response = client.get(
            "/v1/search",
            params={"collection": collections, "txid": tx.id, "format": "json"},
        )
        assert response.json()["total"] == 2, msg

        tx_status = tx.get_status()
        assert "update" == tx_status["transaction-status"]["transaction-mode"]

    docs = client.documents.read(["/t1.json", "/t2.json"])
    assert len(docs) == 2


def test_write_invalid_doc(client: Client):
    try:
        with client.transactions.create() as tx:
            doc1 = Document("/t1.json", {}, permissions=PERMS)
            doc2 = Document("/t2.json", "invalid JSON, should fail", permissions=PERMS)
            client.documents.write(doc1, tx=tx)
            client.documents.write(doc2, tx=tx).raise_for_status()

    except requests.exceptions.HTTPError as error:
        msg = "Second write should have failed due to invalid JSON"
        assert 400 == error.response.status_code, msg

        msg = """Because the two writes occurred in a transaction, the second should
        have caused the transaction to be rolled back."""
        docs = client.documents.read(["/t1.json", "/t2.json"])
        assert len(docs) == 0, msg


def test_time_limit(client: Client):
    """
    Verifies that when a time limit is set and the transaction is committed after that
    time limit has elapsed, the transaction fails to be committed.
    """
    try:
        with client.transactions.create(time_limit=1) as tx:
            time.sleep(1.1)
            doc1 = Document("/t1.json", {}, permissions=PERMS)
            client.documents.write(doc1, tx=tx)

    except HTTPError as error:
        assert error.args[0].startswith("Could not end transaction")
        assert "No transaction with identifier" in error.args[0]
        assert "XDMP-NOTXN" in error.args[0]


def test_database_and_name_args(client: Client):
    """
    Verifies that setting the optional 'name' and 'database' args doesn't cause any
    problems.
    """
    tx_name = "python-tx"
    db_name = "python-client-test-content"
    with client.transactions.create(name=tx_name, database=db_name) as tx:
        doc1 = Document("/t1.json", {}, permissions=PERMS)
        client.documents.write(doc1, tx=tx)
        status = tx.get_status()
        assert tx_name == status["transaction-status"]["transaction-name"]

    assert 1 == len(client.documents.read("/t1.json"))
