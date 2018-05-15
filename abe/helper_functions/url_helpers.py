import urllib.parse


def url_add_query_params(url, **kwargs):
    scheme, netloc, path, params, query, fragment = urllib.parse.urlparse(url)
    query1 = urllib.parse.urlencode(urllib.parse.parse_qsl(query) + list(kwargs.items()))
    return urllib.parse.urlunparse((scheme, netloc, path, params, query1, fragment))
