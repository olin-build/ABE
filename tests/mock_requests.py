import sys
from collections import namedtuple
from pathlib import Path

REQUEST_FIXTURES_DIR = Path(__file__).parent / 'data/requests'
REQUEST_FIXTURES_MAP = {
    'http://www.olin.edu/calendar-node-field-cal-event-date/ical/2018-05/calendar.ics': 'olin-edu-2018-05.ics',
}

MockRequest = namedtuple('MockRequest', ['content'])


class RequestsMock:
    def get(self, url):
        assert url in REQUEST_FIXTURES_MAP, f"{url} needs an entry in {__file__}.REQUEST_FIXTURES_MAP"
        content = (REQUEST_FIXTURES_DIR / REQUEST_FIXTURES_MAP[url]).read_bytes()
        return MockRequest(content)


sys.modules['requests'] = RequestsMock()
