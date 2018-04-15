import os
import sys
import time
import poplib
import email
from io import StringIO
from datetime import datetime
import base64
import icalendar as ic
# from . import database as db
from abe.helper_functions.ics_helpers import ics_to_dict

from email import parser

def get_msg_list(pop_items, pop_conn):
    """ Takes a list of items and the pop3 connection
    (resp, items, octets = pop3conn.list())
    and returns a list of email.message.Message
    objects.
    """
    messages = []
    for item in pop_items:
        id, size = item.decode().split(' ')
        resp, text, octets = pop_conn.retr(id)

        text = [x.decode() for x in text]
        text = "\n".join(text)
        file = StringIO(text)

        orig_email = email.message_from_file(file)
        messages.append(orig_email)
    return messages

def get_attachments(message):
    """ Given a message object,
    checks for an attachment
    and returns it if one exists.
    """
    payload = message.get_payload()
    if len(payload) >= 2:
        attachment = payload[1]
        print(attachment.get_content_type())
        return attachment
    return None

def email_test(filename):
    """ TO DO: determine best way to test. Currently, file does
    not exist in this framework.
    """
    with open(filename, 'r') as myfile:
        data = myfile.read()

    message = email.message_from_string(data)
    calendars = []
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == 'text/calendar':
                decoded = base64.b64decode(part.get_payload()).decode('utf-8')
                # print(base64.b64decode(part.get_payload()))
                cal = ic.Calendar.from_ical(decoded)
                for event in cal.walk('vevent'):
                    date = event.decoded('dtstart')
                    summary = event.decoded('summary')

                    print(date)
                    print(summary)
                print("-------------------------------------------------------------")
                print(decoded)
                calendars.append(cal)
    return calendars

def ical_to_dict(cal):
    """ Given a calendar, creates a dictionary as
    specified in ics_to_dict.
    :input: calendar object
    :return: a list of event dictionaries
    """
    # event_def = {}
    # utc = pytz.utc
    # convert_timezone = lambda a: a.astimezone(utc) if isinstance(a, datetime) else a
    event = cal.walk('vevent')[0]
    event_def = ics_to_dict(event, None)
    return event_def

    # event_def['title'] = str(event.get('summary'))
    # event_def['description'] = str(component.get('description'))
    # event_def['location'] = str(component.get('location'))
    # event_def['start'] = convert_timezone(component.get('dtstart').dt)
    # event_def['end'] = convert_timezone(component.get('dtend').dt)

    # if isinstance(event_def['end'], datetime):
    #     if event_def['end'].time() == datetime.time(hours=0, minutes=0, seconds=0):
    #         event_def['end'] -= timedelta(days=1)
    #         event_def['end'].replace(hours=23, minutes=59, seconds=59)
    # elif isinstance(event_def['end'], date):
    #     event_def['end'] = event_def['end'] - timedelta(days=1)
    #     midnight_time = time(23, 59, 59)
    #     event_def['end'] = datetime.combine(event_def['end'], midnight_time)
    #     event_def['allDay'] = True

    # if component.get('recurrence-id'): # if this is the ics equivalent of a sub_event
    #     event_def['rec_id'] = convert_timezone(component.get('recurrence-id').dt)
    # else: # if this is a normal event or a parent event
    #     event_def['ics_id'] = ics_id

    # event_def['UID'] = str(component.get('uid'))

    # standard = cal.walk('standard')[0]
    """

    event_def['labels'] = labels
    
    if component.get('recurrence-id'): # if this is the ics equivalent of a sub_event
        event_def['rec_id'] = convert_timezone(component.get('recurrence-id').dt)
    else: # if this is a normal event or a parent event
        event_def['ics_id'] = ics_id

    event_def['UID'] = str(component.get('uid'))

    if component.get('rrule'): # if this is an event that defines a recurrence
        rrule = component.get('rrule')
        rec_def = {}
        rec_def['frequency'] = str(rrule.get('freq')[0])
        if 'until' in rrule:
            rec_def['until'] = convert_timezone(rrule.get('until')[0])
        elif 'count' in rrule:
            rec_def['count'] = str(rrule.get('count')[0])
        else:
            rec_def['forever'] = True
        if 'BYDAY' in rrule:
            rec_def['by_day'] = rrule.get('BYDAY')
        if 'BYMONTHDAY' in rrule:
            rec_def['by_month_day'] = [str(x) for x in rrule.get('BYMONTHDAY')]
        if 'INTERVAL' in rrule:
            rec_def['interval'] = str(rrule.get('INTERVAL')[0])
        else:
            rec_def['interval'] = '1'

        event_def['recurrence'] = rec_def
    return(event_def)"""

def get_messages_from_email():
    """ Fetches unread emails from the email address
    specified by the environmental variable ABE_EMAIL
    (password given by env var ABE_PASS). Returns a 
    list of messages.

    :return: List of email message objects
    """
    pop_conn = poplib.POP3_SSL('pop.gmail.com')
    pop_conn.user(os.environ['ABE_EMAIL']) # should be 'abe.at.olin@gmail.com'
    pop_conn.pass_(os.environ['ABE_PASS']) # should be 'abe@olin'
    pop3info = pop_conn.stat() #access mailbox status
    resp, items, octets = pop_conn.list()

    messages = get_msg_list(items, pop_conn)
    pop_conn.quit()
    return messages

def get_calendars_from_messages(messages):
    """ Returns any icals found as Calendar
    objects from the icalendar library.
    
    :inputs:
        messages:   List of email Message instances
    :return:        List of Calendar instances
    """
    calendars = []

    for message in messages:
        if message.is_multipart():
            for part in message.walk():
                # print(part.get_content_type(), part)
                if part.get_content_type() == 'text/calendar':
                    decoded = base64.b64decode(part.get_payload())
                    # print(base64.b64decode(part.get_payload()))
                    cal = ic.Calendar(decoded)
                    calendars.append(cal)
    return calendars

if __name__ == '__main__':
    cals = email_test('test_email.txt')
    for cal in cals:
        ical_to_dict(cal)
    # messages = get_messages_from_email()
    # calendars = get_calendars_from_messages(messages)
    # for calendar in calendars:
    #     print(calendar)