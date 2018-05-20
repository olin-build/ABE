from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl


def url_add_fragment_params(url, **kwargs):
    scheme, netloc, path, params, query, fragment = urlparse(url)
    fragment1 = urlencode(parse_qsl(query) + list(kwargs.items()))
    return urlunparse((scheme, netloc, path, params, query, fragment1))


def url_add_query_params(url, **kwargs):
    scheme, netloc, path, params, query, fragment = urlparse(url)
    query1 = urlencode(parse_qsl(query) + list(kwargs.items()))
    return urlunparse((scheme, netloc, path, params, query1, fragment))


def url_parse_fragment_params(url):
    url = urlparse(url)
    return dict(s.split('=', 2) for s in url.fragment.split('&'))
