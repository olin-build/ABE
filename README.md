# ABE

Amorphous Blob of Events

## Getting Started

### MongoDB

Install MongoDB. Use [these
instructions](https://docs.mongodb.com/getting-started/shell/installation/). On
macOS with [Homebrew](https://brew.sh/) installed, you can instead run `brew install mongodb`.

### Python

#### Setup Virtual Environment

```shell
pip3 install virtualenv
virtualenv -p python3 venv
source ./venv/bin/activate
```

#### Install Requirements

```shell
pip3 install -r requirements.txt
```

### (Optional) Configure MongoDB connection

In order to connect to a mongodb instance other than your localhost, you can create a copy of [`mongo_config_sample.py`](mongo_config_sample.py) called `mongo_config.py`. This configuration file is gitignored and can specify a uri for mongodb to connect to.

## Development

### Running the API server

`run honcho start -f ProcfileHoncho`

Visit <http://127.0.0.1:5000>. You should see a top hat.

Visit <http://127.0.0.1:5000/events/>. You should see `[]`. (This is an empty
JSON list of events.)

### Testing

`python -m unittest`

This is noisy, but should print `OK` at the end:

```bash
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
