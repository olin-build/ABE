# ABE

Dev: [![Build Status](https://travis-ci.org/olinlibrary/ABE.svg?branch=dev)](https://travis-ci.org/olinlibrary/ABE/branches)
[![Coverage](https://codecov.io/gh/olinlibrary/abe/branch/dev/graph/badge.svg)](https://codecov.io/gh/olinlibrary/abe)
Master: [![Build Status](https://travis-ci.org/olinlibrary/ABE.svg?branch=master)](https://travis-ci.org/olinlibrary/ABE/branches)

**ABE** (Amorphous Blob of Events) is Olin's student-built store of information
about Olin events. It enables the creation of digital experiences that share
information about past, present, and upcoming events.

## Built With ABE

ABE is a platform. Some online experiences that use the data in ABE include:

* [Olin Events](https://github.com/olinlibrary/abe-web) is a web view of the
  Olin calendar. It can also be used to subscribe other calendar programs, such
  as Google Calendar and desktop and mobile calendar clients, to ABE; and to
  connect ABE to other calendars.
* [FUTUREboard](https://github.com/olinlibrary/futureboard)  is a digital
  signage platform for sharing of media, supplemented by information about
  events happening on campus.
* [ABE Event Schedule](https://github.com/osteele/abe-event-schedule) is an
  experiment in deriving a conference-track-style schedule from ABE events.

## Getting Started

### Environment Variables

There's an [environment variable template](.env.template), which needs to be copied and may need to be changed accordingly:

```shell
$ cp .env.template .env
```

It will be automagically picked up by...

### Pipenv

ABE uses Pipenv for python management.

First, [install pipenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/#installing-pipenv). Most commonly:

```shell
$ pip install --user pipenv
```

To resolve python dependencies:

```shell
$ pipenv install --dev
```

To enter a virtual environment:

```shell
pipenv shell
```

You can either develop within this virtual environment, or execute individual commands from outside with `pipenv run <COMMAND>`.

You will also need to export `ABE_PASS` and `ABE_EMAIL`, as [found here](https://docs.google.com/document/d/1CZ45xYT33sTi5xpFJF8BkEeniCRszaxcfwiBmvMdmbk/edit).

### RabbitMQ

Install rabbitmq and any dependencies. Use [these instructions](http://www.rabbitmq.com/download.html). It will likely require a download of [Erlang](https://packages.erlang-solutions.com/erlang/), which must be installed separately.

### MongoDB

Install MongoDB. Use [these
instructions](https://docs.mongodb.com/getting-started/shell/installation/). On
macOS with [Homebrew](https://brew.sh/) installed, you can instead run `brew install mongodb`.

#### Setup mongo_config.py

In order to connect to a mongodb instance other than your localhost, you can create a copy of [`mongo_config_sample.py`](abe/mongo_config_sample.py) called `mongo_config.py`.
This configuration file is gitignored and can specify a uri for mongodb to connect to.

#### Load Sample Data

To load [sample data](abe/sample_data.py) into the database, run

```shell
python -m abe.sample_data
```

Load additional sample data via the following. Look at the files in
 `./tests/data` to see the format of the event and label JSON files.

```shell
python -m abe.sample_data --events event-data.json
python -m abe.sample_data --labels label-data.json
```

## Development

### Running Locally

In order to launch a local copy of ABE from inside the pipenv shell, run the slightly verbose:

```shell
$ gunicorn -c guniconf.py abe.app:app
```

Visit <http://127.0.0.1:3000>. You should see a top hat.

Visit <http://127.0.0.1:3000/events/>. You should see `[]`. (This is an empty
JSON list of events.)

### Running the celery tasks

To run the celery tasks concurrently with a local version of ABE, set
`ABE_EMAIL_USERNAME` and `ABE_EMAIL_PASSWORD` to credentials for a GMail
account. (Or, additionally set `ABE_EMAIL_HOST` and `ABE_EMAIL_PORT` to use
a non-GMail POP3 SSL account.)

```shell
honcho start -f ProcfileHoncho
```

or

```shell
celery -A tasks worker --beat -l info
```

in a separate terminal. These will run the "beat" and "worker" servers alongside the web server.

### Testing

`python -m unittest`

This should print `OK` at the end:

```shell
$ python -m unittest
…
----------------------------------------------------------------------
Ran 4 tests in 1.124s

OK
```

Test a specific test:

```shell
$ python -m unittest tests/test_recurrences.py
```

View code coverage:

```shell
$ coverage run --source abe -m unittest
$ coverage html
$ open htmlcov/index.html
```

## API Documentation

Interactive API documentation can be found at`/swagger/`, e.g. for local development: <http://127.0.0.1:3000/swagger/>.
