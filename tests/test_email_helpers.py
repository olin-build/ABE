import email
from unittest.mock import Mock, patch

from icalendar import Calendar

from . import abe_unittest, db

# This import must occur after .context sets the environment variables
from abe.helper_functions import email_helpers  # isort:skip

with open('./tests/data/email_script.txt', 'r') as email_file:
    message = email.message_from_string(email_file.read())

with open('./tests/data/cal_script.txt', 'r') as cal_file:
    cal = Calendar.from_ical(cal_file.read())

serv = Mock()
serv.send_message = Mock()
serv.close = Mock()


class EmailHelpersTestCase(abe_unittest.TestCase):

    def test_get_msg_list(self):
        message_txt = [s.encode() for s in ['first line', 'second line']]
        pop_items = ['mock-id 10'.encode()]
        pop_conn = Mock()
        pop_conn.retr = Mock(return_value=(None, message_txt, None))
        messages = email_helpers.get_msg_list(pop_items, pop_conn)
        pop_conn.retr.assert_called_with('mock-id')
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].as_string(), "\nfirst line\nsecond line")

    def test_ical_to_dict(self):
        test_dict, test_sender = email_helpers.ical_to_dict(cal)
        self.assertEqual(test_sender, 'test.case@tests.com')
        self.assertEqual(test_dict['description'], 'Test Event')
        self.assertEqual(test_dict['labels'], ['test'])

    def test_get_messages_from_email(self):
        with patch('poplib.POP3_SSL') as pop_conn_factory:
            pop_conn = pop_conn_factory()
            pop_conn.list = Mock(return_value=(None, ['mid 1'.encode()], None))
            # since there's a separate test for `get_msg_list`, only mock
            # the minimal data for it to return without error, and don't assert
            # its expected value in this test too
            pop_conn.retr = Mock(return_value=(None, [], None))
            messages = email_helpers.get_messages_from_email()
            pop_conn.quit.assert_called()
            self.assertEqual(len(messages), 1)

    def test_get_calendars_from_messages(self):
        cal_list = email_helpers.get_calendars_from_messages([message])
        self.assertEqual(len(cal_list), 1)
        self.assertIsInstance(cal_list[0], Calendar)

    @patch('abe.helper_functions.email_helpers.error_reply', return_value=None)
    @patch('abe.helper_functions.email_helpers.reply_email', return_value=None)
    def test_cal_to_event(self, email_error, email_reply):
        event_dict, exit_code = email_helpers.cal_to_event(cal)
        event = db.Event.objects(id=event_dict['id']).first()

        self.assertIsNotNone(event)
        self.assertEqual(exit_code, 201)
        self.assertEqual(event_dict['description'], event['description'])

    def test_smtp_connect(self):
        with patch('smtplib.SMTP_SSL') as server_factory:
            server = server_factory()
            server.ehlo = Mock()
            server.login = Mock()
            sev, user = email_helpers.smtp_connect()
            server.ehlo.assert_called()
            server.login.assert_called()

    @patch('abe.helper_functions.email_helpers.smtp_connect', return_value=(serv, 'from_addr'))
    def test_error_reply(self, smtp):
        error = Mock()
        error.errors = [12]
        error.message = "This is an error message"
        to = "to_addr"
        email_helpers.error_reply(to, error)
        smtp.assert_called()
        serv.send_message.assert_called()
        serv.close.assert_called()

    @patch('abe.helper_functions.email_helpers.smtp_connect', return_value=(serv, 'from_addr'))
    def test_reply_email(self, smtp):
        event_dict = {'title': 'Test',
                      'start': '2018-04-30 14:51:24',
                      'end': '2018-04-30 14:51:24',
                      'labels': ['test'],
                      'description': 'empty test',
                      'id': 'id_string'}
        to = "to_addr"
        email_helpers.reply_email(to, event_dict)
        smtp.assert_called()
        serv.send_message.assert_called()
        serv.close.assert_called()

    @patch('abe.helper_functions.email_helpers.smtp_connect', return_value=(serv, 'from_addr'))
    @patch('abe.helper_functions.email_helpers.get_messages_from_email', return_value=[message])
    def test_scrape(self, msgs_from_email, smtp):
        completed = email_helpers.scrape()
        self.assertEqual(len(completed), 1)
