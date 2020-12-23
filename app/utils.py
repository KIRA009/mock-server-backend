import re


def format_and_regex_endpoint(endpoint):
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    if not endpoint.endswith('/'):
        endpoint += '/'
    regex_endpoint = endpoint
    pat = re.compile(r':(.*?)/')
    for url_param in pat.findall(endpoint):
        regex_endpoint = regex_endpoint.replace(f':{url_param}', f'<{url_param}>')
    return endpoint, regex_endpoint
