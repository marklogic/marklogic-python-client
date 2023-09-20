def test_graphql(client):
    data = client.rows.graphql("query musicianQuery { test_musician { lastName firstName dob } }")
    musicians = data["data"]["test_musician"]
    assert 4 == len(musicians)
    assert 1 == len([m for m in musicians if m["lastName"] == "Armstrong"])


def test_graphql_return_response(client):
    response = client.rows.graphql("query musicianQuery { test_musician { lastName firstName dob } }", return_response=True)
    assert 200 == response.status_code
    data = response.json()
    musicians = data["data"]["test_musician"]
    assert 4 == len(musicians)
    assert 1 == len([m for m in musicians if m["lastName"] == "Armstrong"])


def test_graphql_bad_graphql(client):
    response = client.rows.graphql("query musicianQuery { test_musician { lastName firstName dob } ")
    assert 1 == len(response['errors'])
    assert 'GRAPHQL-PARSE: Error parsing the GraphQL request string => \nquery musicianQuery { test_musician { lastName firstName dob } ' == response['errors'][0]['message']


def test_graphql_bad_user(not_rest_user_client):
    response = not_rest_user_client.rows.graphql("query musicianQuery { test_musician { lastName firstName dob } }")
    assert 403 == response.status_code
