# ABE
Amorphous Blob of Events

## Getting Started

### MongoDB

- [installation instructions](https://docs.mongodb.com/getting-started/shell/installation/)

### Python

#### Pipenv

[Install pipenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/#installing-pipenv), most commonly:
```shell
$ pip install --user pipenv
```

To resolve dependencies:
```shell
$ pipenv install
```

To enter a virtual environment:
```shell
pipenv shell
```

#### mongo_config.py

In order to connect to a mongodb instance other than your localhost, you can create a copy of [`mongo_config_sample.py`](abe/mongo_config_sample.py) called `mongo_config.py`. This configuration file is gitignored and can specify a uri for mongodb to connect to.

### Running Locally

In order to launch a local copy of ABE from inside the pipenv shell, run the slightly verbose:

```shell
$ gunicorn -c guniconf.py abe.app:app
```

## API

### abe.olin.build/events/

| HTTP Method | Action |
| ------------- | ------------- |
| GET | retrieve all events |
| POST | create new event |

### abe.olin.build/events/24

| HTTP Method | Action |
| ------------- | ------------- |
| GET | retrieve event with id 24 |
| PUT | update event with id 24 |
| DELETE | delete event with id 24 |

### abe.olin.build/events/ShortScarletFrog

| HTTP Method | Action |
| ------------- | ------------- |
| GET | retrieve event with id "ShortScarletFrog" |
| PUT | update event with id "ShortScarletFrog" |
| DELETE | delete event with id "ShortScarletFrog" |

### abe.olin.build/labels/

| HTTP Method | Action |
| ------------- | ------------- |
| GET | retrieve all labels |
| PUT | create new label |

### abe.olin.build/labels/clubs

| HTTP Method | Action |
| ------------- | ------------- |
| GET | retrieve label with name "clubs" |
| PUT | update label with name "clubs" |
| DELETE | delete label with name "clubs" |
