import logging
from requests import Response, Session

logger = logging.getLogger(__name__)

"""
Defines classes to simplify usage of the REST endpoints defined at
https://docs.marklogic.com/REST/client/transaction-management for managing transactions.
"""


class Transaction:
    """
    Represents a transaction created via
    https://docs.marklogic.com/REST/POST/v1/transactions .

    An instance of this class can act as a Python context manager and can thus be used
    with the Python "with" keyword. This is the intended use case, allowing a user to
    perform one to many calls to MarkLogic within the "with" block, each referencing the
    ID associated with this transaction. When the "with" block concludes, the
    transaction will be automatically committed if no error was thrown, and rolled back
    otherwise.

    :param id: the ID of the new transaction, which is used for all subsequent
    operations involving the transaction.
    :param session: a requests Session object that is required for either committing or
    rolling back the transaction, as well as for obtaining status of the transaction.
    """

    def __init__(self, id: str, session: Session):
        self.id = id
        self._session = session

    def __enter__(self):
        return self

    def get_status(self) -> dict:
        """
        Retrieve transaction status via
        https://docs.marklogic.com/REST/GET/v1/transactions/[txid].
        """
        return self._session.get(
            f"/v1/transactions/{self.id}", headers={"Accept": "application/json"}
        ).json()

    def commit(self) -> Response:
        """
        Commits the transaction via
        https://docs.marklogic.com/REST/POST/v1/transactions/[txid]. This is expected to be
        invoked automatically via a Python context manager.
        """
        logger.debug(f"Committing transaction with ID: {self.id}")
        return self._session.post(
            f"/v1/transactions/{self.id}", params={"result": "commit"}
        )

    def rollback(self) -> Response:
        """
        Rolls back the transaction via
        https://docs.marklogic.com/REST/POST/v1/transactions/[txid]. This is expected to be
        invoked automatically via a Python context manager.
        """
        logger.debug(f"Rolling back transaction with ID: {self.id}")
        return self._session.post(
            f"/v1/transactions/{self.id}", params={"result": "rollback"}
        )

    def __exit__(self, *args):
        response = (
            self.rollback()
            if len(args) > 1 and isinstance(args[1], Exception)
            else self.commit()
        )
        assert (
            204 == response.status_code
        ), f"Could not end transaction; cause: {response.text}"


class TransactionManager:
    def __init__(self, session: Session):
        self._session = session

    def create(self, name=None, time_limit=None, database=None) -> Transaction:
        """
        Creates a new transaction via https://docs.marklogic.com/REST/POST/v1/transactions.
        Contrary to the docs, a Location header is not returned, but the transaction data
        is. And the Accept header can be used to control the format of the transaction data.

        The returned Transaction is a Python context manager and is intended to be used
        via the Python "with" keyword.

        :param name: optional name for the transaction.
        :param time_limit: optional time limit, in seconds, until the server cancels the
        transaction.
        :param database: optional database to associate with the transaction.
        """
        params = {}
        if name:
            params["name"] = name
        if time_limit:
            params["timeLimit"] = time_limit
        if database:
            params["database"] = database

        response = self._session.post(
            "/v1/transactions", params=params, headers={"Accept": "application/json"}
        )
        id = response.json()["transaction-status"]["transaction-id"]
        return Transaction(id, self._session)
