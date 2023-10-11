import json
from requests import Session
from marklogic.internal.util import response_has_no_content


"""
Defines classes to simplify usage of the REST rows service defined at
https://docs.marklogic.com/REST/client/row-management.
"""


class RowManager:
    def __init__(self, session: Session):
        self._session = session

    __accept_switch = {
        "json": "application/json",
        "xml": "application/xml",
        "csv": "text/csv",
        "json-seq": "application/json-seq",
    }

    __query_format_switch = {
        "json": lambda response: response.json(),
        "xml": lambda response: response.text,
        "csv": lambda response: response.text,
        "json-seq": lambda response: response.text,
    }

    def query(
        self,
        dsl: str = None,
        plan: dict = None,
        sql: str = None,
        sparql: str = None,
        graphql: str = None,
        format: str = "json",
        return_response: bool = False,
        **kwargs,
    ):
        """
        Sends a query to an endpoint at the MarkLogic rows service defined at
        https://docs.marklogic.com/REST/client/row-management.

        One of 'dsl', 'plan', 'sql', 'sparql', or 'graphql' must be defined.
        For more information about Optic and using the Optic DSL, SQL, and SPARQL,
        see https://docs.marklogic.com/guide/app-dev/OpticAPI. If one or more of these
        are passed into the call, the function uses the query parameter that is first
        in the prior list.

        :param dsl: an Optic DSL query
        :param plan: a serialized Optic query
        :param sql: an SQL query
        :param sparql: a SPARQL query
        :param graphql: a GraphQL query string. This is the query string
        only, not the entire query JSON object. See
        https://docs.marklogic.com/REST/POST/v1/rows/graphql for more information.
        :param format: defines the format of the response. Valid values are "json",
        "xml", "csv", and "json-seq". If a GraphQL query is submitted, this parameter
        is ignored and a JSON response is always returned.
        :param return_response: boolean specifying if the entire original response
        object should be returned (True) or if only the data should be returned (False)
        upon a success (2xx) response. Note that if the status code of the response is
        not 2xx, then the entire response is always returned.
        """
        path = "v1/rows/graphql" if graphql else "v1/rows"
        headers = kwargs.pop("headers", {})
        data = None
        if graphql:
            data = json.dumps({"query": graphql})
            headers["Content-Type"] = "application/graphql"
        else:
            request_info = self.__get_request_info(dsl, plan, sql, sparql)
            data = request_info["data"]
            headers["Content-Type"] = request_info["content-type"]
            if format:
                value = RowManager.__accept_switch.get(format)
                if value is None:
                    msg = f"Invalid value for 'format' argument: {format}; "
                    msg += "must be one of 'json', 'xml', 'csv', or 'json-seq'."
                    raise ValueError(msg)
                else:
                    headers["Accept"] = value

        response = self._session.post(path, headers=headers, data=data, **kwargs)
        if response.ok and not return_response:
            if response_has_no_content(response):
                return []
            return (
                response.json()
                if graphql
                else RowManager.__query_format_switch.get(format)(response)
            )
        return response

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
