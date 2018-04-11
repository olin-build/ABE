# ABE

Amorphous Blob of Events

## Getting Started

### Pipenv
ABE uses Pipenv for python management. 

First, [install pipenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/#installing-pipenv). Most commonly:
```shell
$ pip install --user pipenv
```

To resolve python dependencies:
```shell
$ pipenv install
```

To enter a virtual environment:
```shell
pipenv shell
```

You can either develop within this virtual environment, or execute individual commands from outside with `pipenv run <COMMAND>`.

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

## Development

### Running Locally

In order to launch a local copy of ABE from inside the pipenv shell, run the slightly verbose:

```shell
$ gunicorn -c guniconf.py abe.app:app
```

Visit <http://127.0.0.1:3000>. You should see a top hat.

Visit <http://127.0.0.1:3000/events/>. You should see `[]`. (This is an empty
JSON list of events.)

### Testing

`python -m unittest`

This is noisy, but should print `OK` at the end:

```shell
$ python -m unittest
…
----------------------------------------------------------------------
Ran 4 tests in 1.124s

OK
```

## API Documentation

### abe.olin.build/events/

| HTTP Method | Action              |
| ----------- | ------------------- |
| GET         | retrieve all events |
| POST        | create new event    |

### abe.olin.build/events/24

| HTTP Method | Action                    |
| ----------- | ------------------------- |
| GET         | retrieve event with id 24 |
| PUT         | update event with id 24   |
| DELETE      | delete event with id 24   |

### abe.olin.build/events/ShortScarletFrog

| HTTP Method | Action                                    |
| ----------- | ----------------------------------------- |
| GET         | retrieve event with id "ShortScarletFrog" |
| PUT         | update event with id "ShortScarletFrog"   |
| DELETE      | delete event with id "ShortScarletFrog"   |

### abe.olin.build/labels/

| HTTP Method | Action              |
| ----------- | ------------------- |
| GET         | retrieve all labels |
| PUT         | create new label    |

### abe.olin.build/labels/clubs

| HTTP Method | Action                           |
| ----------- | -------------------------------- |
| GET         | retrieve label with name "clubs" |
| PUT         | update label with name "clubs"   |
| DELETE      | delete label with name "clubs"   |
