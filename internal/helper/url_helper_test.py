# -*- coding: utf-8 -*-

import unittest

from internal.helper.url_helper import URLHelper


class TestURLHelper(unittest.TestCase):
    __url_helper = URLHelper()

    def test_fulfill_http_protocol(self):
        url = 'news.zing.vn'
        processed_url = self.__url_helper.fulfill_http_protocol(url)
        expect_result = 'http://news.zing.vn'

        self.assertEqual(processed_url, expect_result, '{} should be {}'.format(processed_url, expect_result))

        url = 'http://news.zing.vn'
        processed_url = self.__url_helper.fulfill_http_protocol(url)
        expect_result = 'http://news.zing.vn'

        self.assertEqual(processed_url, expect_result, '{} should be {}'.format(processed_url, expect_result))

    def test_is_same_domain(self):
        domain = 'news.zing.vn'
        url = 'http://news.zing.vn/kham-pha'
        is_same_domain = self.__url_helper.is_same_domain(domain, url)
        expect_result = True

        self.assertEqual(is_same_domain, expect_result, '{} should be {}'.format(is_same_domain, expect_result))

        domain = 'news.zing.vn'
        url = '/kham-pha'
        is_same_domain = self.__url_helper.is_same_domain(domain, url)
        expect_result = True

        self.assertEqual(is_same_domain, expect_result, '{} should be {}'.format(is_same_domain, expect_result))

    def test_clear_hash_tag(self):
        url = 'http://news.zing.vn/kham-pha#123'
        processed_url = self.__url_helper.clear_hash_tag(url)
        expect_result = 'http://news.zing.vn/kham-pha'

        self.assertEqual(processed_url, expect_result, '{} should be {}'.format(processed_url, expect_result))

    def test_fulfill_domain_path(self):
        domain = 'news.zing.vn'
        url = 'http://news.zing.vn/kham-pha'
        processed_url = self.__url_helper.fulfill_domain_path(domain, url)
        expect_result = 'http://news.zing.vn/kham-pha'

        self.assertEqual(processed_url, expect_result, '{} should be {}'.format(processed_url, expect_result))

        domain = 'news.zing.vn'
        url = '/kham-pha'
        processed_url = self.__url_helper.fulfill_domain_path(domain, url)
        expect_result = 'http://news.zing.vn/kham-pha'

        self.assertEqual(processed_url, expect_result, '{} should be {}'.format(processed_url, expect_result))

    def test_get_domain_from_url(self):
        url = 'http://news.zing.vn/kham-pha'
        domain = self.__url_helper.get_domain_from_url(url)
        expect_result = 'news.zing.vn'

        self.assertEqual(domain, expect_result, '{} should be {}'.format(domain, expect_result))

    def test_get_domain_path_from_url(self):
        url = 'http://news.zing.vn/kham-pha'
        domain_path = self.__url_helper.get_domain_path_from_url(url)
        expect_result = 'news.zing.vn/kham-pha'

        self.assertEqual(domain_path, expect_result, '{} should be {}'.format(domain_path, expect_result))

    def test_get_path_from_url(self):
        url = 'http://news.zing.vn/kham-pha'
        path = self.__url_helper.get_path_from_url(url)
        expect_result = '/kham-pha'

        self.assertEqual(path, expect_result, '{} should be {}'.format(path, expect_result))

    def test_get_query_string_from_url(self):
        url = 'http://news.zing.vn/kham-pha?query=123'
        path = self.__url_helper.get_query_string_from_url(url)
        expect_result = 'query=123'

        self.assertEqual(path, expect_result, '{} should be {}'.format(path, expect_result))

        url = 'http://news.zing.vn/kham-pha?'
        path = self.__url_helper.get_query_string_from_url(url)
        expect_result = ''

        self.assertEqual(path, expect_result, '{} should be {}'.format(path, expect_result))

if __name__ == '__main__':
    unittest.main()