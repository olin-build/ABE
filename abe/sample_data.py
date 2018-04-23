#!/usr/bin/env python
"""Load sample data into the database."""
from collections import namedtuple
from datetime import datetime
from dateutil import parser
import json
from pathlib import Path

import arrow
import click
import isodate

sample_data_dir = Path(__file__).parent.parent / 'tests/data'
sample_events_file = sample_data_dir / 'sample-events.json'
sample_labels_file = sample_data_dir / 'sample-labels.json'

kelly_colors = ['#F2F3F4', '#222222', '#F3C300', '#875692', '#F38400', '#A1CAF1', '#BE0032', '#C2B280', '#848482', '#008856',
                '#E68FAC', '#0067A5', '#F99379', '#604E97', '#F6A600', '#B3446C', '#DCD300', '#882D17', '#8DB600', '#654522', '#E25822', '#2B3D26']

olin_colors = [  # '#009BDF', '#A7A9AC', '#A7A9AC', '#000000',
    '#E31D3C', '#750324',
    '#F47920',
    '#FFC20E', '#C05131',
    '#C0D028',
    '#8EBE3F', '#00653E',
    '#349E49',
    # '#26AAA5', '#00677E',
    '#6BC1D3',
    '#009BDF', '#00458C',
    '#7B5AA6',
    '#C77EB5', '#511C74',
    '#ED037C'
]


sample_ics = [
    {
        "url": "webcal://http://www.olin.edu/calendar-node-field-cal-event-date/ical/calendar.ics"
    }
]


def fix_event_list_dates(events):
    """Recursively replace values at a hard-coded set of fields, by dates or
    datetimes."""
    event_date_fields = {
        'start',
        'end',
        'recurrence_start',
        'recurrence_end',
        'recurrence.until',
        'until'}

    def str2date(s):
        if 'T' in s:
            return isodate.parse_datetime(s)
        else:
            return isodate.parse_date(s)

    def fix_field(name, value, date_fields):
        if name in date_fields and isinstance(value, str):
            return str2date(value)
        if isinstance(value, dict):
            subfields = {k[len(name) + 1:]
                         for k in date_fields
                         if k.startswith(name + '.')}
            return fix_dict_dates(value, subfields)
        return value

    def fix_dict_dates(d, date_fields=event_date_fields):
        return {k: fix_field(k, v, date_fields) for k, v in d.items()}

    return [fix_dict_dates(event) for event in events]


def load_event_data(fp):
    """Load sample event data from a JSON file, and resolve its dates."""
    return fix_event_list_dates(json.load(fp))


def insert_data(db, event_data=None, label_data=None, ics_data=None):
    """Insert data into the database."""
    import logging
    from .helper_functions.sub_event_helpers import find_recurrence_end
    logging.basicConfig(level=logging.DEBUG)
    if event_data:
        logging.info("Inserting sample event data")
        for event in event_data:
            for key, value in event.items():
                if type(value) is datetime:  # convert to UTC from EST
                    event[key] = arrow.get(
                        value,
                        'US/Eastern'
                    ).to('utc').datetime
            new_event = db.Event(**event)
            if 'recurrence' in new_event:
                if new_event.recurrence.forever == False:
                    new_event.recurrence_end = find_recurrence_end(new_event)
                    logging.info("made some end recurrences: {}".format(new_event.recurrence_end))
            new_event.save()
    if label_data:
        logging.info("Inserting sample label data")
        for index, label in enumerate(label_data):
            if 'color' not in label:
                label['color'] = olin_colors[index]
            db.Label(**label).save()
    if ics_data:
        logging.info("Inserting sample ics data")
        for ics in ics_data:
            db.ICS(**ics).save()

SampleData = namedtuple('SampleData', ['events', 'labels', 'icss'])


def load_sample_data():
    """Return hard-coded sample data. Event and label data are read from the test
    data directory. This exists as a separate function so that its data can be
    shared between the Heroku postdeploy script and the --use-defaults
    command-line option."""
    with open(sample_events_file) as fp:
        event_data = load_event_data(fp)
    with open(sample_labels_file) as fp:
        label_data = json.load(fp)
    return SampleData(event_data, label_data, sample_ics)


def load_data(db):
    """Load the database with sample data. The Heroku postdeploy
    script calls this."""
    event_data, label_data, sample_ics = load_sample_data()
    insert_data(db, event_data, label_data, sample_ics)


@click.command()
@click.option('--events', type=click.File())
@click.option('--labels', type=click.File())
def main(events=None, labels=None):
    """Load the database with sample data.

    With no options, uses samples from this source file."""

    from . import database as db
    event_data = load_event_data(events) if events else None
    label_data = json.load(labels) if labels else None
    ics_data = None
    if all(data is None for data in (event_data, label_data, ics_data)):
        event_data, label_data, ics_data = load_sample_data()
    insert_data(db, event_data, label_data, ics_data)

if __name__ == '__main__':  # import data
    main()
