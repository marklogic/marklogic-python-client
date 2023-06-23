To try this out locally:

- Use Python 3.9 or higher; [pyenv](https://github.com/pyenv/pyenv#installation) is recommended for installing and managing Python versions. 
- [Install poetry](https://python-poetry.org/docs/)
- `python -m venv .venv` to [create a virtual environment](https://docs.python.org/3/library/venv.html).
- `source .venv/bin/activate` to use that virtual environment.
- `poetry install` to install project dependencies.

VSCode is recommended for development. You can try [these instructions](https://www.pythoncheatsheet.org/blog/python-projects-with-poetry-and-vscode-part-1) 
for getting setup in VSCode with linting and formatting enabled.

To run the tests:

- Use Java 8 or higher
- `cd test-app`
- Verify that the host/port/username/admin in `gradle.properties` work for your ML install
- Run `./gradlew -i mlDeploy`
- `cd ..`
- Run `pytest`

To run an individual test with logging to stdout:

    pytest -s tests/test_search.py

To run an individual test method:

    pytest -s test/test_search.py::test_search