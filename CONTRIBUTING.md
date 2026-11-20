To try this out locally:

- Use Python 3.13 or higher; [pyenv](https://github.com/pyenv/pyenv#installation) is recommended for installing and managing Python versions. 
- Set up the virtual environment and install the project dependencies as described in
[Local setup with the Harness registry](#local-setup-with-the-harness-registry). Dependencies must not be installed
from the public PyPI registry.

VSCode is recommended for development.
- For formatting, the project uses the [Black](https://github.com/psf/black) code formatter, and the
[Black Formatter VSCode extension](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
is recommended.
- For linting, the project uses the [Flake8](https://flake8.pycqa.org/en/latest/) linter and the
[Flake8 extension](https://marketplace.visualstudio.com/items?itemName=ms-python.flake8) is recommended.
These tools are included in the project by pyproject.toml and the settings are in .vscode/settings.json.

You can also get additional information at
[these instructions](https://www.pythoncheatsheet.org/blog/python-projects-with-poetry-and-vscode-part-1) 
for getting setup in VSCode with linting and formatting enabled.

## Local setup with the Harness registry

All Python dependencies come from the private Harness Artifact Registry; the public
PyPI registry is not used. Releases uploaded less than 7 days ago are skipped (supply-chain cool-down), both by Poetry
(`solver.min-release-age` in `poetry.toml`) and by pip (`uploaded-prior-to` in the virtual environment's pip config).

### One-time setup

1. In Harness, create a personal user token with a scope rule of resource type "Artifact registry", organization
"MarkLogic", and only the "View Registry" and "Download" permissions.
2. Copy `.env.example` to `.env` and set `HARNESS_USEREMAIL` (your Progress email) and `HARNESS_TOKEN`. `.env` is
git-ignored; never commit it or share the token.
3. From the project root, run the setup script:

        .\scripts\harness-setup.ps1      # Windows PowerShell
        ./scripts/harness-setup.sh       # macOS / Linux

   The script creates `.venv` if needed, points pip in the virtual environment at Harness only, installs the pinned
   Poetry version (2.5.1) into the virtual environment, and runs `poetry install`. It is safe to re-run. Delete `.venv`
   first if it was created before this setup, so that nothing installed from PyPI remains.
4. Activate the virtual environment (`.\.venv\Scripts\Activate.ps1` or `source .venv/bin/activate`) and run `pytest`.

The virtual environment's pip config (`.venv/pip.ini` or `.venv/pip.conf`) contains your token. It is inside `.venv`,
which is git-ignored.

### Day-to-day

- Open a new VSCode terminal after changing `.env`; set `POETRY_HTTP_BASIC_HARNESS_*` values for `poetry`. In
PowerShell, running the setup script again also refreshes them in the current session (a bash script runs in a child
process, so it cannot). In bash you can load `.env` into the current terminal with `set -a; source .env; set +a`, or set
the values yourself:

```bash
$env:POETRY_HTTP_BASIC_HARNESS_USERNAME = <USEREMAIL>   # PowerShell
$env:POETRY_HTTP_BASIC_HARNESS_PASSWORD = <TOKEN>

export POETRY_HTTP_BASIC_HARNESS_USERNAME=<USEREMAIL>   # bash
export POETRY_HTTP_BASIC_HARNESS_PASSWORD=<TOKEN>
```

- Add or update a dependency with `poetry add <package>` or `poetry update <package>`. Poetry skips versions that are
less than 7 days old.
- After any change to `poetry.lock`, run the cool-down check and commit `poetry.lock` with the change:

        .\scripts\harness-cooldown-check.ps1      # Windows PowerShell
        ./scripts/harness-cooldown-check.sh       # macOS / Linux

  If it fails, a locked version is too new; run `poetry lock --regenerate` and check again.
- If you edit `pyproject.toml` and Poetry reports that `pyproject.toml changed significantly since poetry.lock was last
generated`, run the setup script with `-Lock` (PowerShell) or `--lock` (bash) once.
- If your token changes, update `.env` and run the setup script again.

### Troubleshooting

- `No matching distribution found ... (from versions: none)`: pip hides the underlying HTTP error. A `401` means the
token or email is wrong or expired. A `403` means the token is valid but its scope, or your Harness role, does not allow
viewing and downloading from the MarkLogic organization's Artifact Registry.
- The setup script says `HARNESS_USEREMAIL` and `HARNESS_TOKEN` must be set: `.env` is missing or the values are empty.

## Building the distribution files

From the project root, run:

    python build_distributions.py

This creates the wheel, source distribution, and standalone SPDX SBOM in `dist/`. To write them to a different directory,
pass it with `--output`:

    python build_distributions.py --output <directory>

## Running the tests

Before running any tests, first deploy the test application:

- Use Java 17
- `cd test-app`
- Create a file named `gradle-local.properties` and add `mlPassword=` to it, with the value of the property being
your admin user's password.
- Verify that the host/port/username in `gradle.properties` work for your MarkLogic installation.
- Run `./gradlew -i mlDeploy`
- `cd ..`

Then run all the tests:

    pytest 

To run an individual test:

    pytest tests/test_search.py

To run an individual test method:

    pytest test/test_search.py::test_search

Note that due to the pytest config in the `pyproject.toml` file, all 
[Python logging](https://docs.python.org/3/howto/logging.html) should appear immediately
as tests are executed. If you are using VSCode, you can see the logging by selecting 
"Python Test Log" in the "Output" panel.

## Testing the client in a Python shell

After running `poetry install` as described above, you can start a Python shell and manually test the client. You will 
need to launch the shell in the same Python virtual environment as the one in which you ran `poetry install`. After 
ensuring you've done that, start a new Python shell by running `python`. 

You can then import the client via:

    from marklogic import Client

You can instantiate an instance of the client that communicates with this project's test application via:

    client = Client("http://localhost:8030", digest=("python-test-user", "password"))

And you can then start sending requests with the client - for example:

    r = client.get("/v1/search?format=json&pageLength=2")
    r.json()

You can also use the scripts in the `./shell` directory to initialize a client. The following initializes a client
that connects to this project's test application:

    python -i shell/test_app.py

And this initializes a client that connects to the OOTB App-Services app server, which is used for examples in this 
project's documentation:

    python -i shell/docs.py


## Testing updates in a different local project
If you are using this in another project and making changes for it, use the following command to make the
changes to this local project immediately reflected in a dependent project:
```poetry add <local-path-to-this-project>/marklogic-python-client/```
 
Using this method will allow you to very easily test changes to this project, in a different local project.

Keep in mind that you probably do not want to check that version of the pyproject.toml file into version
control since it is only useful locally.


## Testing the documentation locally

The docs for this project are stored in the `./docs` directory as a set of Markdown files. These are published via
[GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages) using the
configuration found under "Settings / Pages" in this repository. 

You can build and test the docs locally by 
[following these GitHub instructions](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/testing-your-github-pages-site-locally-with-jekyll), 
though you don't need to perform all of those steps since some of the files generated by doing so are already in the 
`./docs` directory. You just need to do the following:

1. Install the latest Ruby (rbenv works well for this).
2. Install Jekyll. 
3. Go to the docs directory - `cd ./docs` .
4. Run `bundle install` (this may not be necessary due to Gemfile.lock being in version control).
5. Run `bundle exec jekyll serve`.

You can then go to http://localhost:4000 to view the docs. 
