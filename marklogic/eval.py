import json

from requests import Session

"""
Defines an EvalManager class to simplify usage of the "/v1/eval" REST
endpoint defined at https://docs.marklogic.com/REST/POST/v1/eval.
"""


class EvalManager:
    """
    Provides a method to simplify sending an XQuery or
    JavaScript eval request to the eval endpoint.
    """

    def __init__(self, session: Session):
        self._session = session

    def xquery(
        self, xquery: str, vars: dict = None, return_response: bool = False, **kwargs
    ):
        """
        Send an XQuery script to MarkLogic via a POST to the endpoint
        defined at https://docs.marklogic.com/REST/POST/v1/eval.

        :param xquery: an XQuery string
        :param vars: a dict containing variables to include
        :param return_response: boolean specifying if the entire original response
        object should be returned (True) or if only the data should be returned (False)
        upon a success (2xx) response. Note that if the status code of the response is
        not 2xx, then the entire response is always returned.
        """
        return self.__send_request({"xquery": xquery}, vars, return_response, **kwargs)

    def javascript(
        self,
        javascript: str,
        vars: dict = None,
        return_response: bool = False,
        **kwargs
    ):
        """
        Send a JavaScript script to MarkLogic via a POST to the endpoint
        defined at https://docs.marklogic.com/REST/POST/v1/eval.

        :param javascript: a JavaScript string
        :param vars: a dict containing variables to include
        :param return_response: boolean specifying if the entire original response
        object should be returned (True) or if only the data should be returned (False)
        upon a success (2xx) response. Note that if the status code of the response is
        not 2xx, then the entire response is always returned.
        """
        return self.__send_request(
            {"javascript": javascript}, vars, return_response, **kwargs
        )

    def __send_request(
        self, data: dict, vars: dict = None, return_response: bool = False, **kwargs
    ):
        """
        Send a script (XQuery or JavaScript) and possibly a dict of vars
        to MarkLogic via a POST to the endpoint defined at
        https://docs.marklogic.com/REST/POST/v1/eval.
        """
        if vars is not None:
            data["vars"] = json.dumps(vars)
        response = self._session.post("v1/eval", data=data, **kwargs)
        return (
            self._session.process_multipart_mixed_response(response)
            if response.status_code == 200 and not return_response
            else response
        )
