# Contributing to ABE

:+1::tada: First off, thanks for taking the time to contribute to ABE! :tada::+1:

## Help Needed

Please check out the [the open issues][issues].

## Project setup

### Pipenv

ABE uses [Pipenv][pipenv] for Python management.

First, [install pipenv](https://docs.pipenv.org/#install-pipenv-today). Most commonly:

```shell
$ pip install --user pipenv
```

Install this project's package dependencies:

```shell
$ pipenv install --dev
```

To enter a virtual environment:

```shell
pipenv shell
```

You can either develop within this virtual environment, or execute individual
commands with `pipenv run <COMMAND>`.

To test email, you will also need to export `ABE_PASS` and `ABE_EMAIL`, as [found here](https://docs.google.com/document/d/1CZ45xYT33sTi5xpFJF8BkEeniCRszaxcfwiBmvMdmbk/edit).

### RabbitMQ

@kylecombes 10/7/2020: Unclear if this is necessary, but I'll leave it for now. You can probably skip this though.

Install RabbitMQ and any dependencies. Use [these
instructions](http://www.rabbitmq.com/download.html). It will likely require a
download of [Erlang](https://packages.erlang-solutions.com/erlang/), which must
be installed separately.

## Development

### Running Locally

Launch the API server:

```shell
pipenv run server
```

This runs the server in debug mode. In this mode, it will reload files as you
edit them. You don't need to quit and re-launch the server after each change.)

Visit <http://127.0.0.1:3000>. You should see a top hat.

Visit <http://127.0.0.1:3000/events/>. You should see some event data.

### Running the celery tasks

To run the celery tasks concurrently with a local version of ABE, set
`EMAIL_USERNAME` and `EMAIL_PASSWORD` to credentials for a GMail
account. (Or, additionally set `EMAIL_HOST` and `EMAIL_PORT` to use
a non-GMail POP3 SSL account.)

In order to launch a local copy of ABE from inside the pipenv shell, run the slightly verbose:

```shell
honcho start -f ProcfileHoncho
```

or

```shell
celery -A tasks worker --beat -l info
```

in a separate terminal. These will run the "beat" and "worker" servers alongside the web server.

### Committing and Pushing changes

Please make sure to run the tests before you commit your changes. Run
`./scripts/pre-commit-check`. This runs the test suite and the linter.

You can also run test and lint separately, for more control over which test
files to run:

#### Testing

`pipenv run pytest`

This should print `OK` at the end:

```shell
$ pipenv run pytest
…
----------------------------------------------------------------------
Ran 4 tests in 1.124s

OK
```

Test a specific test:

```shell
$ pipenv run pytest tests/test_recurrences.py
```

View code coverage:

```shell
$ pipenv run pytest --cov=. --cov-report html:htmlcov
$ open htmlcov/index.html
```

The test suite will print some `DeprecationWarning`s from files in `…/site-packages/mongoengine/` (#151). It is safe to ignore these.

#### Linting

```shell
$ pipenv run lint
```

## Style Guides

### Python Style Guide

Code should follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) and [PEP
257](https://www.python.org/dev/peps/pep-0257/).

Run `pipenv run lint` to check your code.

Run `pipenv run format` to reformat code in the `abe` and `tests` directories to
comply with PEP 8.

### Markdown Style Guide

Markdown should pass [markdown-lint](https://github.com/remarkjs/remark-lint).

The following editor plugins keep code in compliance with markdown-lint:

* Atom: [linter-markdown](https://atom.io/packages/linter-markdown)
* Visual Studio Code:
  * [markdownlint](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)
    lints Markdown files.
  * [remark](https://marketplace.visualstudio.com/items?itemName=mrmlnc.vscode-remark)
    beautifies Markdown files.

[issues]: https://github.com/olin-build/ABE/issues
[pipenv]: https://docs.pipenv.org/
