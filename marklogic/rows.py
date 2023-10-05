import json
from requests import Session

"""
Defines a RowManager class to simplify usage of the "/v1/rows" & "/v1/rows/graphql" REST
endpoints defined at https://docs.marklogic.com/REST/POST/v1/rows/graphql.
"""


class RowManager:
    """
    Provides a method to simplify sending a GraphQL
    request to the GraphQL rows endpoint.
    """

    def __init__(self, session: Session):
        self._session = session

    def graphql(self, graphql_query: str, return_response: bool = False, **kwargs):
        """
        Send a GraphQL query to MarkLogic via a POST to the endpoint defined at
        https://docs.marklogic.com/REST/POST/v1/rows/graphql.

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

    __accept_switch = {
        "json": "application/json",
        "xml": "application/xml",
        "csv": "text/csv",
        "json-seq": "application/json-seq",
        "mixed": "application/xml, multipart/mixed",
    }

    __query_format_switch = {
        "json": lambda response: response.json(),
        "xml": lambda response: response.text,
        "csv": lambda response: response.text,
        "json-seq": lambda response: response.text,
        "mixed": lambda response: response,
    }

    def query(
        self,
        dsl: str = None,
        plan: dict = None,
        sql: str = None,
        sparql: str = None,
        format: str = "json",
        return_response: bool = False,
        **kwargs
    ):
        """
        Send a query to MarkLogic via a POST to the endpoint defined at
        https://docs.marklogic.com/REST/POST/v1/rows.
        Just like that endpoint, this function can be used for four different types of
        queries: Optic DSL, Serialized Optic, SQL, and SPARQL. The type of query
        processed by the function is dependent upon the parameter used in the call to
        the function.
        For more information about Optic and using the Optic DSL, SQL, and SPARQL,
        see https://docs.marklogic.com/guide/app-dev/OpticAPI.
        If multiple query parameters are passed into the call, the function uses the
        query parameter that is first in the list: dsl, plan, sql, sparql.

        :param dsl: an Optic DSL query
        :param plan: a serialized Optic query
        :param sql: an SQL query
        :param sparql: a SPARQL query
        :param return_response: boolean specifying if the entire original response
        object should be returned (True) or if only the data should be returned (False)
        upon a success (2xx) response. Note that if the status code of the response is
        not 2xx, then the entire response is always returned.
        """
        request_info = self.__get_request_info(dsl, plan, sql, sparql)
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = request_info["content-type"]
        headers["Accept"] = RowManager.__accept_switch.get(format)
        response = self._session.post(
            "v1/rows", headers=headers, data=request_info["data"], **kwargs
        )
        return (
            RowManager.__query_format_switch.get(format)(response)
            if response.status_code == 200 and not return_response
            else response
        )

    def __get_request_info(self, dsl: str, plan: dict, sql: str, sparql: str):
        """
        Examine the parameters passed into the query function to determine what value
        should be passed to the endpoint and what the content-type header should be.

        :param dsl: an Optic DSL query
        :param plan: a serialized Optic query
        :param sql: an SQL query
        :param sparql: a SPARQL query
        dict object returned contains the two values required to make the POST request.
        """
        if dsl is not None:
            return {
                "content-type": "application/vnd.marklogic.querydsl+javascript",
                "data": dsl,
            }
        if plan is not None:
            return {"content-type": "application/json", "data": plan}
        if sql is not None:
            return {"content-type": "application/sql", "data": sql}
        if sparql is not None:
            return {"content-type": "application/sparql-query", "data": sparql}
        else:
            raise ValueError(
                "No query found; must specify one of: dsl, plan, sql, or sparql"
            )
