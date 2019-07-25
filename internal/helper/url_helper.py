import re
import os

from urllib.parse import urlparse, parse_qs


class URLHelper:
    def __init__(self):
        pass

    def fulfill_http_protocol(self, url=''):
        compiled_re = re.compile('^http(s)?:\/\/(.)*')

        if compiled_re.match(url) is not None:
            return url

        return 'http://{0}'.format(url)

    def is_same_domain(self, domain='', url=''):
        if len(url) < 1:
            return False

        if url.find('//') == 0:
            return False

        if url[0] == '/':
            return True

        compiled_re = re.compile('http(s)?:\/\/{0}\/?'.format(domain))
        if compiled_re.match(url) is None:
            return False

        return True

    def clear_hash_tag(self, url=''):
        try:
            hasTagIndex = url.index('#')
            return url[:hasTagIndex]

        except ValueError:
            return url

    def fulfill_domain_path(self, domain='', path=''):
        compiled_re = re.compile('^http(s)?:\/\/(.)*')

        if compiled_re.match(path) is not None:
            return path

        path = path.lstrip('/')
        url = 'http://{0}/{1}'.format(domain, path)

        return self.clear_hash_tag(url.lstrip('/'))

    def get_domain_from_url(self, url=''):
        url_struct = urlparse(url)
        return url_struct.hostname

    def get_domain_path_from_url(self, url=''):
        parsed = urlparse(url)
        return '{0}{1}'.format(parsed.hostname, parsed.path)

    def get_path_from_url(self, url=''):
        parsed = urlparse(url)
        return self.clear_hash_tag(parsed.path).lstrip('/')

    def get_query_string_from_url(self, url=''):
        parsed = urlparse(url)
        return parsed.query

    def get_params_from_url(self, url=''):
        parsed = urlparse(url)
        return parse_qs(parsed.query)

    def replace_url_value(self, url='', param_name='', param_new_value=''):
        params = self.get_params_from_url(url)
        if param_name not in params:
            return ''

        return url.replace('{}={}'.format(param_name, params[param_name][0]),
                           '{}={}'.format(param_name, param_new_value))

    def get_file_extension_from_url(self, url=''):
        path = urlparse(url).path
        ext = os.path.splitext(path)[1]
        return ext.lower()
