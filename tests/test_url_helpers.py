
from abe.helper_functions.url_helpers import url_add_fragment_params, url_add_query_params, url_parse_fragment_params


def test_url_add_fragment_params():
    assert url_add_fragment_params('http://example', a=1) == 'http://example#a=1'
    assert url_add_fragment_params('http://example', a=1, b=2) == 'http://example#a=1&b=2'
    assert url_add_fragment_params('http://example', a=1, b=None) == 'http://example#a=1'


def test_url_add_query_params():
    assert url_add_query_params('http://example:3000') == 'http://example:3000'
    assert url_add_query_params('http://example:3000/path') == 'http://example:3000/path'
    assert url_add_query_params('http://example:3000/path?q=1') == 'http://example:3000/path?q=1'
    assert url_add_query_params('http://example:3000/path', a=1) == 'http://example:3000/path?a=1'
    assert url_add_query_params('http://example:3000/path?q=1', a=2) == 'http://example:3000/path?q=1&a=2'
    assert (url_add_query_params('http://example:3000/path?q=1&r=2', a=3, b=4) ==
            'http://example:3000/path?q=1&r=2&a=3&b=4')
    assert (url_add_query_params('http://example:3000/path?q=1&#frag', a=2) ==
            'http://example:3000/path?q=1&a=2#frag')


def test_url_parse_fragment_params():
    assert url_parse_fragment_params('http://example?a=1') == {}
    assert url_parse_fragment_params('http://example#a=1') == {'a': '1'}
    assert url_parse_fragment_params('http://example#a=1&b=2') == {'a': '1', 'b': '2'}
    assert url_parse_fragment_params('http://example#a=1+2') == {'a': '1 2'}
