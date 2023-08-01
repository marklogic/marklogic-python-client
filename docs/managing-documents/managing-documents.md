---
layout: default
title: Managing documents
nav_order: 3
has_children: true
permalink: /documents
---

The [/v1/documents endpoint](https://docs.marklogic.com/REST/client/management) in the MarkLogic REST API supports
operations that involve writing or reading a single document. It also supports operations that involve multiple 
documents, though those require use of a potentially complex multipart HTTP request or response. The MarkLogic Python
client simplifies those operations by hiding the details of multipart requests and responses.
