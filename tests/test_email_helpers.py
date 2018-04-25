from unittest import skip
from unittest.mock import Mock, patch

from . import abe_unittest
from .context import abe  # noqa: F401

# This import has to happen after .context sets the environment variables
from abe.helper_functions import email_helpers  # isort:skip


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

    @skip('unimplemented')
    def test_get_attachments(self):
        pass

    @skip('unimplemented')
    def test_email_test(self):
        pass

    @skip('unimplemented')
    def test_ical_to_dict(self):
        pass

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

    @skip('unimplemented')
    def test_get_calendars_from_messages(self):
        pass

    @skip('unimplemented')
    def test_cal_to_event(self):
        pass

    @skip('unimplemented')
    def test_smtp_connect(self):
        pass

    @skip('unimplemented')
    def test_error_reply(self):
        pass

    @skip('unimplemented')
    def test_reply_email(self):
        pass

    @skip('unimplemented')
    def test_send_email(self):
        pass

    @skip('unimplemented')
    def test_scrape(self):
        pass
