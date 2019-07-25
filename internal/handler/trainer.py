# -*- coding: utf-8 -*-
import re

from internal.constant.constant import Constant
from internal.handler.base_handler import BaseHandler
from internal.helper.url_helper import URLHelper
from internal.helper.string_helper import StringHelper
from internal.service.browser.factory import BrowserFactory
from internal.helper.soup_helper import SoupHelper
from bs4 import BeautifulSoup, NavigableString, Comment, Doctype
from internal.helper.detector import Detector


class Trainer(BaseHandler):
    __url_helper = URLHelper()
    __string_helper = StringHelper()
    __soup_helper = SoupHelper()
    __comment_links = {}
    __domain = ''

    def __init__(self, url, browser_endpoint):
        """

        Args:
            url (unicode): Source for training.
            browser_endpoint (unicode): Virtual browser for requesting.

        """
        self.__constant = Constant()
        self.__browser_service = BrowserFactory().get_browser_service(browser_endpoint)
        self.__comment_links = {}
        self.__domain = self.__url_helper.get_domain_from_url(url)

    def array_chunks(self, elements=[], chunk_size=10):
        for i in range(0, len(elements), chunk_size):
            yield elements[i:i + chunk_size]

    def __get_browser_height(self, container_info: dict):
        browser_height = 0
        for container_id in container_info:
            if browser_height < int(container_info[container_id]['height']):
                browser_height = int(container_info[container_id]['height'])
        return browser_height

    def __get_inferred_footer_height(self, height: int):
        if height < 2000:
            return height / 10
        else:
            return height / 10 if height / 10 <= 500 else 500

    def get_record_type(self, url: str, page_asset: dict):
        html = page_asset['content']
        container_info = page_asset['container_asset']

        if len(html) < 1000:
            raise Exception('Something goes wrong with content. URL: {}'.format(url))

        detector = Detector()
        if detector.is_article(url, html):
            return self.__constant.RECORD_ARTICLE

        if self.__url_helper.get_path_from_url(url).strip() == '':
            return self.__constant.RECORD_CATEGORY

        html = self.__string_helper.replace_unclose_img_tag(html)
        html = self.__string_helper.replace_unclose_br_tag(html)
        soup = BeautifulSoup(html, 'html.parser')

        browser_height = self.__get_browser_height(container_info)
        footer_height = self.__get_inferred_footer_height(browser_height)
        content_path_boundary_footer_position = browser_height - footer_height
        content_path_boundary_height_position = 120

        # Clean unused tag
        [s.extract() for s in soup('source')]
        [s.extract() for s in soup('track')]
        [s.extract() for s in soup('script')]
        [s.extract() for s in soup('style')]
        [s.extract() for s in soup('br')]
        [s.extract() for s in soup('iframe')]
        [s.extract() for s in soup('noscript')]
        [s.extract() for s in soup('videolist')]
        [s.extract() for s in soup('select')]

        self.__soup_helper.unwrap_self_close_tags(soup)

        [item.extract() for item in soup.contents if isinstance(item, Doctype)]
        [item.extract()
         for item in soup.contents if isinstance(item, NavigableString)]

        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]

        lineBreaks = soup.findAll(
            text=lambda text: text == '\n' or text == '\r')
        [lineBreak.extract() for lineBreak in lineBreaks]

        text_paths, d_text_path_container_id = self.__soup_helper.get_text_paths(soup)
        densest_text_path, dense_text_paths = self.__soup_helper.get_densest_text_path_and_dense_text_path(
            text_paths)

        main_content_sub_soups = []
        unnumber_path_dict = dict([])

        total_time = 0
        for dense_text_path in dense_text_paths.keys():
            if dense_text_path.find('text_node') < 0:
                continue

            text_path_elements = dense_text_path.split(' ')
            text_path_elements.pop()

            current_text_path = ' '.join(text_path_elements)
            images, anchors, path = self.__soup_helper.get_nearest_images_anchors_path(
                soup, current_text_path, True)

            non_anchor_contents = self.__get_real_non_anchor_text_paths(path, text_paths)
            total_non_anchor_content_length = 1
            for i in non_anchor_contents:
                total_non_anchor_content_length += len(i)

            total_anchor_content_length = 1
            for i in anchors:
                total_anchor_content_length += len(i)

            if dense_text_path.find('a_') > -1:
                unnumber_path = self.__remove_number_path(current_text_path)
                if unnumber_path not in unnumber_path_dict:
                    unnumber_path_dict[unnumber_path] = []
                unnumber_path_dict[unnumber_path].append(current_text_path)

        def get_real_parent_anchor_path(path, similarity_paths):
            def get_parent_path(path, similarity_path):
                path_parts = path.split(' ')
                similarity_parts = similarity_path.split(' ')

                path_parts.reverse()
                similarity_parts.reverse()
                parent_parts = path_parts[:]
                level = 0

                while level != len(path_parts) - 1:
                    if path_parts[level] != similarity_parts[level]:
                        parent_parts.reverse()
                        return ' '.join(parent_parts), level
                    level += 1
                    parent_parts.pop(0)

                return path, 0

            current_level = 0
            current_parent_path = path
            for i in similarity_paths:
                if i == path:
                    continue

                inferred_parent_path, inferred_level = get_parent_path(path, i)
                if current_level < inferred_level:
                    current_level = inferred_level
                    current_parent_path = inferred_parent_path

            return current_parent_path

        ignore_paths = []
        main_content_sub_path = []
        # Improve for removing title of category group
        for unnumber_path in unnumber_path_dict:
            if len(unnumber_path_dict[unnumber_path]) < 2:
                continue

            current_anchor_paths = unnumber_path_dict[unnumber_path]
            for path in current_anchor_paths:
                real_parent_path = get_real_parent_anchor_path(
                    path, current_anchor_paths
                )
                main_content_sub_path.append(real_parent_path)
                main_content_sub_soups.append(self.__soup_helper.get_soup_by_path(soup, real_parent_path))

        current_text = len(soup.getText())
        for index in range(len(main_content_sub_soups)):
            if len(main_content_sub_soups[index].getText()) < (float(current_text) / 10) or \
                            len(main_content_sub_soups[index].getText()) < 150:
                ignore_paths.append(main_content_sub_path[index])

        content_paths = []
        for text_path in text_paths:
            if not self.__soup_helper.is_in_parent_path(densest_text_path, text_path):
                continue

            is_ignored = False
            for path in ignore_paths:
                if text_path.find(path) == 0:
                    is_ignored = True
                    break

            if is_ignored:
                continue

            if text_path in content_paths:
                continue

            content_paths.append(text_path)

        count = 0
        for text_path in content_paths:
            container_id = d_text_path_container_id[text_path]
            container_width = int(container_info[container_id]['width'])
            container_visibility = container_info[container_id]['visibility'].lower()
            container_display = container_info[container_id]['visibility'].lower()
            container_font_size = container_info[container_id]['fontSize'].lower()
            if container_width == 0 or container_visibility in ('hidden', 'collapse') or container_display == 'none' \
                    or container_font_size == '0px':
                continue

            print(container_width)
            print(text_paths[text_path])
            print("=========")

            if (container_width >= 350 and container_visibility not in ('hidden', 'collapse') and container_display != 'none') and len(text_paths[text_path].strip()) > 150:
                if len(text_paths[text_path]) > 400:
                    count += len(text_paths[text_path]) / 150
                count += 1

        if count >= 2:
            return self.__constant.RECORD_ARTICLE

        elif 0 < count < 2:
            return self.__constant.RECORD_AMBIGUOUS

        else:
            return self.__constant.RECORD_CATEGORY

    def __get_real_non_anchor_text_paths(self, dense_text_path, main_content_text_paths):
        contents = []
        for text_path in main_content_text_paths.keys():
            if text_path.find(dense_text_path) == 0 and text_path.find('a_') < 0:
                non_accent_text = self.__string_helper.convert_vietnamese_to_eng(main_content_text_paths[text_path])
                if len(non_accent_text) > 20:
                    contents.append(main_content_text_paths[text_path])
        return contents

    def __remove_number_path(self, path):
        return re.sub('(_[0-9]+)', '', path)