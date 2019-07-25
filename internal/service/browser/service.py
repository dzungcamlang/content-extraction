import requests
import time

from abc import ABCMeta, abstractmethod
from internal.helper.string_helper import StringHelper


class IBrowser:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_text_styles(self, url, selectors):
        pass

    @abstractmethod
    def get_page_asset(self, url):
        pass

    @abstractmethod
    def get_page_asset_no_cache(self, url):
        pass


class Browser(IBrowser):
    __end_point = ''
    __string_helper = StringHelper()

    def __init__(self, end_point):
        """

        Args:
            end_point (unicode): browser endpoint

        """
        self.__end_point = end_point

    def __request(self, url, json_data):
        """

        Core request.

        Args:
            url (unicode): url for requesting.
            json_data (dict): Json for requesting.

        Returns:
            Object which include status code and data response.

        """
        request = requests.Request('POST', url, json=json_data)
        request_prepared = request.prepare()

        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('http://', adapter)

        response = session.send(request_prepared, timeout=300)
        json_object = self.__string_helper.load_json(response.content)
        if json_object is None:
            data_response = {}
        else:
            data_response = json_object

        return {
            'status_code': response.status_code,
            'data_response': data_response
        }

    def __request_retry_if_busy(self, end_point_request_url, json_data):

        while True:
            result = self.__request(end_point_request_url, json_data)

            if result['status_code'] != 200:
                error_message = result['data_response']['error_message']
                if error_message.lower() == 'busy':
                    print("receiving 'busy' response. wait for a while and retry")
                    time.sleep(3)
                    continue

                raise RuntimeError('Could request to server. URL: {} Error: {}'.format(end_point_request_url,
                                                                                       error_message))

            return result

    def get_page_asset(self, url):
        """

        Getting content and network activity.

        Args:
            url (unicode): url for getting page asset.

        Returns:
            Object which include content and request entries.

        """
        end_point_request_url = '{0}/get_page_asset'.format(self.__end_point)

        json_data = {'url': url}
        result = self.__request_retry_if_busy(end_point_request_url, json_data)

        return result['data_response']['data']

    def get_page_asset_no_cache(self, url):
        """

        Getting content and network activity (Which is not cached).

        Args:
            url (unicode): url for getting page asset.

        Returns:
            Object which include content and request entries.

        """
        end_point_request_url = '{0}/get_page_asset_no_cache'.format(
            self.__end_point)

        json_data = {'url': url}
        result = self.__request_retry_if_busy(end_point_request_url, json_data)

        return result['data_response']['data']

    def get_text_styles(self, url, selectors):
        """

        Get text styles of specific selectors.

        Args:
            url (unicode): url for getting style.
            selectors (unicode): selector for getting style.

        Returns:
            List of styles.

        """
        end_point_request_url = '{0}/get_text_css'.format(self.__end_point)
        json_data = {
            'url': url,
            'html_selectors': selectors
        }
        result = self.__request_retry_if_busy(end_point_request_url, json_data)

        return list(map(lambda style: style, result['data_response']['data']))

    def get_container_rect(self, url, selectors):
        """

        Get text styles of specific selectors.

        Args:
            url (unicode): url for getting style.
            selectors (unicode): selector for getting style.

        Returns:
            List of styles.

        """
        end_point_request_url = '{0}/get_container_rect'.format(
            self.__end_point)
        json_data = {
            'url': url,
            'selectors': selectors
        }
        result = self.__request_retry_if_busy(end_point_request_url, json_data)

        return list(map(lambda style: style, result['data_response']['data']))

    def get_iframe_comment_content(self, url):
        """

        Getting content and network activity.

        Args:
            url (unicode): url for getting page asset.

        Returns:
            Object which include content and request entries.

        """
        end_point_request_url = '{0}/get_iframe_comment_content'.format(
            self.__end_point)
        json_data = {'url': url}
        result = self.__request_retry_if_busy(end_point_request_url, json_data)

        return result['data_response']['data']

    def get_full_asset(self, url):
        end_point_request_url = '{0}/api/v1/get_full_asset'.format(self.__end_point)
        print(url)

        json_data = {'url': url}
        result = self.__request_retry_if_busy(end_point_request_url, json_data)

        data = result['data_response']['data']
        if data is None:
            raise Exception(
                'Empty response when requesting url: {}'.format(url))

        if data['content'].strip() == '':
            raise Exception(
                'Empty content when requesting url: {}'.format(url))

        if len(data['container_asset'].keys()) == 0:
            raise Exception(
                'Empty container asset when requesting url: {}'.format(url))

        return data
