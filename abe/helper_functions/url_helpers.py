from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl, unquote_plus


def url_add_fragment_params(url, **kwargs):
    """Replace the fragment with `kwargs` encoded as query params. None-valued
    params are omitted.

    >>> url_add_fragment_params('http://example', a=1, b='a value', c=None)
    http://example#a=1&b=a+value
    """
    scheme, netloc, path, params, query, _fragment = urlparse(url)
    fragment1 = urlencode([(k, v) for k, v in kwargs.items() if v is not None])
    return urlunparse((scheme, netloc, path, params, query, fragment1))


def url_add_query_params(url, **kwargs):
    """Append query `kwargs`, encoded as query params. None-valued params are
    omitted.

    >>> url_add_query_params('http://example', a=1, b='a value', c=None)
    http://example?a=1&b=a+value
    """
    scheme, netloc, path, params, query, fragment = urlparse(url)
    query1 = urlencode(parse_qsl(query) +
                       [(k, v) for k, v in kwargs.items() if v is not None])
    return urlunparse((scheme, netloc, path, params, query1, fragment))


def url_parse_fragment_params(url):
    """Parse the URL fragment as a string of query parameters.
    Requests parameter values, e.g. 'a=1' but not 'a'.

    >>> url_parse_fragment_params('http://example#a=1&b=a+value')
    {'a': '1', 'b': 'a value'}
    """
    fragment = urlparse(url).fragment
    return {k: unquote_plus(v)
            for s in fragment.split('&')
            if '=' in s
            for k, v in [s.split('=', 2)]}
