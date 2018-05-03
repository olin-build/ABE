import logging

from celery import Celery

from abe import database as db
from abe.helper_functions.email_helpers import scrape
from abe.helper_functions.ics_helpers import update_ics_feed

# Specify mongodb host and datababse to connect to
BROKER_URL = db.return_uri()

celery = Celery('EOD_TASKS', broker=BROKER_URL)

# Loads settings for Backend to store results of jobs
celery.config_from_object('celeryconfig')


@celery.task
def refresh_calendar():
    update_ics_feed()
    logging.info("updated the ICS feed")


@celery.task
def parse_email_icals():
    scrape()
    logging.info("scraped the emails")
