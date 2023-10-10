---
layout: default
title: Querying for rows
nav_order: 4
---


The [MarkLogic REST rows service](https://docs.marklogic.com/REST/client/row-management) supports
operations for querying for rows via a variety of languages. The MarkLogic Python client simplifies submitting queries
for rows and converting the response into a useful data structure.

## Setup

The examples below require documents to be loaded along with a 
[TDE view](https://docs.marklogic.com/guide/app-dev/TDE) that projects rows from the documents. You must also have 
performed the instructions in the [setup guide](example-setup.md). 

Run the following in a Python shell to load 4 documents, each capturing details about a musician:

```
from marklogic import Client
from marklogic.documents import Document, DefaultMetadata
client = Client('http://localhost:8000', digest=('python-user', 'pyth0n'))

client.documents.write([
    DefaultMetadata(permissions={"rest-reader": ["read", "update"]}, collections=["musician"]),
    Document("/musician1.json", {"lastName": "Armstrong", "firstName": "Louis", "dob": "1901-08-04"}),
    Document("/musician2.json", {"lastName": "Byron", "firstName": "Don", "dob": "1958-11-08"}),
    Document("/musician3.json", {"lastName": "Coltrane", "firstName": "John", "dob": "1926-09-23"}),
    Document("/musician4.json", {"lastName": "Davis", "firstName": "Miles", "dob": "1926-05-26"})
])
```

Now load a TDE view via the following:

```
tde_view = {
    "template": {
        "context": "/",
        "collections": ["musician"],
        "rows": [{
            "schemaName": "example",
            "viewName": "musician",
            "columns": [
                {"name": "lastName", "scalarType": "string", "val": "lastName"},
                {"name": "firstName", "scalarType": "string", "val": "firstName"},
                {"name": "dob", "scalarType": "date", "val": "dob"}
            ]
        }]
    }
}

client.documents.write(
    Document(
        "/tde/musicians.json", tde_view, 
        permissions={"rest-reader": ["read", "update"]}, 
        collections=["http://marklogic.com/xdmp/tde"]
    ),
    params={"database": "Schemas"}
)
```


## Optic queries

The [MarkLogic Optic API](https://docs.marklogic.com/guide/app-dev/OpticAPI) allows for rows to be queried from 
documents via a SQL-like syntax. The [MarkLogic REST API rows service](https://docs.marklogic.com/REST/POST/v1/rows)
accepts Optic queries either as an [Optic Query DSL statement](https://docs.marklogic.com/guide/app-dev/OpticAPI#id_46710) 
or as [a serialized plan](https://docs.marklogic.com/guide/app-dev/OpticAPI#id_11208). 

Since using an Optic DSL query is often the easiest approach, a DSL query can be submitted as the first argument without
any name:

```
client.rows.query("op.fromView('example', 'musician')")
```

The above will return a JSON object that captures each of the matching rows along with definitions for each column. See
the section below on choosing an output format for controlling how data is returned.


You can use a named argument as well:

```
client.rows.query(dsl="op.fromView('example', 'musician')")
```

For some use cases, it may be helpful to capture an Optic query in its serialized form. Such a query can then be 
submitted via the `plan` argument:

```
plan = '{"$optic":{"ns":"op", "fn":"operators", "args":[{"ns":"op", "fn":"from-view", "args":["example", "musician"]}]}}'
client.rows.query(plan=plan)
```

Optic supports many different types of queries and operations; please
[see the documentation]((https://docs.marklogic.com/guide/app-dev/OpticAPI#id_35559)) for further information on 
much more powerful and flexible queries than shown in these examples, which are intended solely for demonstration of 
how to submit an Optic query.


## SQL queries

MarkLogic supports [SQL queries against views](https://docs.marklogic.com/guide/sql). SQL queries can be submitted 
via the `sql` argument:

```
client.rows.query(sql="select * from example.musician order by lastName")
```

This will return a JSON object that captures each of the matching rows along with definitions 
for each column. See the section below on choosing an output format for controlling how data is returned.

## SPARQL queries

MarkLogic supports the [SPARQL query language](https://www.w3.org/TR/sparql11-query/), allowing for 
[SPARQL queries to be run against views](https://docs.marklogic.com/guide/semantics/semantic-searches#id_94155), 
similar to Optic and SQL. SPARQL queries can be submitted via the `sparql` argument:

```
sparql = "PREFIX musician: <http://marklogic.com/column/example/musician/> SELECT * WHERE {?s musician:lastName ?lastName} ORDER BY ?lastName"
client.rows.query(sparql=sparql)
```

This will return a JSON object that captures each of the matching rows along with definitions 
for each column. See the section below on choosing an output format for controlling how data is returned. 

## GraphQL queries

MarkLogic supports [GraphQL queries](https://docs.marklogic.com/REST/POST/v1/rows/graphql) to be run against views. 
A GraphQL query can be submitted via the `graphql` argument:

```
client.rows.query(graphql="query myQuery { example_musician { lastName firstName dob } }")
```

This will return a JSON object containing the matching rows. MarkLogic will only return a JSON object for GraphQL
queries; the `format` argument described below will not have any impact when submitting a GraphQL query.

## Choosing an output format

The [MarkLogic REST endpoint for querying rows](https://docs.marklogic.com/REST/POST/v1/rows) supports several options
for how data is returned via the `format` parameter. The `client.rows.query` function allows for an output format to be 
selected via a `format` argument. The following table defined the possible values:

| `format` value | Output format | 
| --- | --- |
| `json` | JSON object with keys of 'columns' and 'rows'. |
| `xml` | XML document defining the columns and rows. |
| `csv` | CSV text with the first row defining the columns. |
| `json-seq` | A [line-delimited JSON sequence](https://datatracker.ietf.org/doc/html/rfc7464) with the first row defining the columns. |
| `mixed` | TODO Seems like we should remove this as it does the same thing as "return_response". |
