---
layout: default
title: Setup for examples
nav_order: 2
permalink: /setup
---

The examples in this documentation depend on a particular MarkLogic user with a role containing specific privileges. 
If you would like to try these examples out against your own installation of MarkLogic, you will need to create this 
MarkLogic user and role. To do so, please go to the Admin application for your MarkLogic instance - e.g. if you are 
running MarkLogic locally, this will be at <http://localhost:8001> - and authenticate as your "admin" user. 
Then perform the following steps to create a new role:

1. Click on "Roles" in the "Security" box. 
2. Click on "Create".
3. In the form, enter "python-docs-role" for "Role Name".
4. Scroll down and select the "rest-extension-user", "rest-reader", "rest-writer", and "tde-admin" roles.
5. Scroll further down and select the "xdbc:eval", "xdbc:invoke", and "xdmp:eval-in" privileges.
6. Scroll to the top or bottom and click on "OK" to create the role.

After creating the role, return to the Admin application home page and perform the following steps:

1. Click on "Users" in the "Security" box.
2. Click on "Create".
3. In the form, enter "python-user" for "User Name" and "pyth0n" as the password. 
4. Scroll down until you see the "Roles" section and select the "python-docs-role" role. 
5. Scroll to the top or bottom and click on "OK" to create the user.

(Note that you could use the `admin` role instead to grant full access to all features in MarkLogic, but this is 
generally discouraged for security reasons.)

You can verify that you correctly created the user by accessing the REST API for the out-of-the-box REST API 
server in MarkLogic that listens on port 8000. Go to <http://localhost:8000/v1/search> (changing "localhost" to 
the correct name of your MarkLogic host if you are not running it locally) in a web browser and enter the 
username and password for the new user you created. The browser should then display a search response returned by 
MarkLogic, verifying that the user is able to access the MarkLogic REST API.
