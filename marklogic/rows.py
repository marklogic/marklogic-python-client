import json
from requests import Session

"""
Defines a RowManager class to simplify usage of the "/v1/rows" & "/v1/rows/graphql" REST
endpoints defined at https://docs.marklogic.com/REST/POST/v1/rows/graphql
"""


class RowManager:
    """
    Provides a method to simplify sending a GraphQL request to the GraphQL rows endpoint.
    """
    def __init__(self, session: Session):
        self._session = session
        
    def graphql(self, graphql_query, return_response=False, *args, **kwargs):
        """
        Send a GraphQL query to MarkLogic via a POST to the endpoint defined at
        https://docs.marklogic.com/REST/POST/v1/rows/graphql

        :param graphql_query: a GraphQL query string. Note - this is the query string
        only, not the entire query JSON object. See the following for more information:
        https://spec.graphql.org/October2021/#sec-Overview
        https://graphql.org/learn/queries/
        :param return_response: boolean specifying if the entire original response
        object should be returned (True) or if only the data should be returned (False)
        upon a success (2xx) response. Note that if the status code of the response is
        not 2xx, then the entire response is always returned.
        """
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/graphql"
        response = self._session.post(
            "v1/rows/graphql",
            headers=headers,
            data=json.dumps({"query": graphql_query}),
            **kwargs
        )
        return (
            response.json()
            if response.status_code == 200 and not return_response
            else response
        )