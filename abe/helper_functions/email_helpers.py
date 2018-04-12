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
# from .helper_functions.ics_helpers import ics_to_dict, extract_ics

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

def email_test():
    """ TO DO: determine best way to test. Currently, file does
    not exist in this framework.
    """
    with open('test_email.txt', 'r') as myfile:
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
                    cal = ic.Calendar.from_ical(decoded)
                    calendars.append(cal)
                    for event in cal.walk('vevent'):
                        date = event.decoded('dtstart')
                        summary = event.decoded('summary')

                        print(date)
                        print(summary)
    return calendars

if __name__ == '__main__':
    messages = get_messages_from_email()
    calendars = get_calendars_from_messages(messages)
    for calendar in calendars:
        print(calendar)