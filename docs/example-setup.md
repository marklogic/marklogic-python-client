---
layout: default
title: Setup for examples
nav_order: 2
permalink: /setup
---

The examples in this documentation depend on a particular MarkLogic username and password. If you 
would like to try these examples out against your own installation of MarkLogic, you will need to create this 
MarkLogic user. To do so, please go to the Admin application for your MarkLogic instance - e.g. if you are running MarkLogic locally, this will be at <http://localhost:8001> - and authenticate as your "admin" user. 
Then perform the following steps to create a new user:

1. Click on "Users" in the "Security" box.
2. Click on "Create".
3. In the form, enter "python-user" for "User Name" and "pyth0n" as the password. 
4. Scroll down until you see the "Roles" section. Click on the "rest-reader", "rest-writer", and "security" checkboxes. 
5. Scroll to the top or bottom and click on "OK" to create the user.

(The `security` role is only needed to allow for the user to load documents into the out-of-the-box Schemas database 
in MarkLogic; in a production application, an admin or admin-like user would typically be used for this use case.)

You can verify that you correctly created the user by accessing the REST API for the out-of-the-box REST API 
server in MarkLogic that listens on port 8000. Go to <http://localhost:8000/v1/search> (changing "localhost" to 
the correct name of your MarkLogic host if you are not running it locally) in a web browser and enter the 
username and password for the new user you created. The browser should then display a search response returned by 
MarkLogic, verifying that the user is able to access the MarkLogic REST API.
