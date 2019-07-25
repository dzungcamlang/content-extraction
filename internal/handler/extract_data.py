# -*- coding: utf-8 -*-

import json
import re

from typing import List
from internal.handler.base_handler import BaseHandler
from internal.helper.url_helper import URLHelper
from internal.helper.string_helper import StringHelper
from internal.helper.detector import Detector
from internal.service.logger.factory import LoggerFactory
from internal.helper.soup_helper import SoupHelper
from bs4 import BeautifulSoup, NavigableString, Comment, Doctype


class ExtractData(BaseHandler):
    __logger_service = LoggerFactory().get_logger_service().logger
    __url_helper = URLHelper()
    __string_helper = StringHelper()
    __soup_helper = SoupHelper()
    __browser_service = None
    __text_styles = {}
    __domain = ''

    def __init__(self, url, browser_endpoint):
        """

        Args:
            url (unicode): URL for extracting data.
            browser_endpoint (unicode): Browser endpoint for requesting.

        """
        self.__text_styles = {}
        self.__domain = self.__url_helper.get_domain_from_url(url)

    def array_chunks(self, elements=[], chunk_size=10):
        for i in range(0, len(elements), chunk_size):
            yield elements[i:i + chunk_size]

    def __is_anchor_group(self, content: str):
        content_parts = content.split(' ')
        total_text = 0
        total_space = 0
        for content in content_parts:
            if content.strip() == '':
                total_space += 1
            else:
                total_text += 1

        return float(total_space) / total_text > 2

    def __get_text_node_container_info(self, text_path: str, d_text_path_container_id: dict, d_page_container_info: dict) -> dict:
        container_id = d_text_path_container_id[text_path]
        return d_page_container_info[container_id]

    def extract_data(self, url: str, html: str, d_page_container_info: dict):
        html = self.__string_helper.replace_unclose_br_tag(html)
        soup = BeautifulSoup(self.__string_helper.replace_unclose_meta_tag(
            self.__string_helper.replace_unclose_img_tag(html)), 'html.parser')

        if len(str(soup)) < 1000:
            raise Exception('Something goes wrong with content. URL: {}'.format(url))

        hack_title_content = ''
        hack_publish_date = ''
        if url.find('soctrang.gov.vn') > -1:
            hack_title_content = soup.find(id="titlehidden").getText()
            hack_publish_date = '' if len(soup.select('#divtitle span')) < 1 else soup.select('#divtitle span')[0].getText()

        fallback_soup = ''
        meta_description = ''
        meta_tag = soup.find('meta', {'name': 'description'})
        if meta_tag is not None:
            if meta_tag.has_attr('content'):
                meta_description = meta_tag['content']

        meta_tag = soup.find(
            'meta', {'property': 'og:description'})
        if meta_tag is not None:
            if meta_tag.has_attr('content'):
                meta_description = meta_tag['content']

        meta_title = ''
        title = soup.select('head title')
        if len(title) > 0:
            meta_title = title[0].getText()

        if meta_title.strip() == '':
            meta_tag = soup.find('meta', {'name': 'title'})
            if meta_tag is not None:
                if meta_tag.has_attr('content'):
                    meta_title = meta_tag['content']

            meta_tag = soup.find('meta', {'property': 'title'})
            if meta_tag is not None:
                if meta_tag.has_attr('content'):
                    meta_title = meta_tag['content']

            meta_tag = soup.find(
                'meta', {'property': 'og:title'})
            if meta_tag is not None:
                if meta_tag.has_attr('content'):
                    meta_title = meta_tag['content']

            meta_tag = soup.find(
                'meta', {'name': 'og:title'})
            if meta_tag is not None:
                if meta_tag.has_attr('content'):
                    meta_title = meta_tag['content']

        detector = Detector()
        d_css_selector = detector.get_available_article_css_selector(url, html)
        if d_css_selector is not None:
            title = detector.get_title(html, d_css_selector)
            description = detector.get_description(html, d_css_selector)
            main_content = detector.get_main_content(html, d_css_selector)
            comment = {}
            published_date = detector.get_published_at(html, d_css_selector)

            if description.strip() == '':
                description = meta_description
            return title, description, main_content, html, comment, published_date

        # Clean unused tag
        [s.extract() for s in soup('script')]
        [s.extract() for s in soup('style')]
        [s.extract() for s in soup('noscript')]
        [s.extract() for s in soup('video')]
        [s.extract() for s in soup('videolist')]
        [s.extract() for s in soup('source')]
        [s.extract() for s in soup('track')]
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

        clonned_soup = self.__soup_helper.clone_soup(soup)
        clonned_soup_v2 = self.__soup_helper.clone_soup(soup)

        text_paths, d_text_path_container_id = self.__soup_helper.get_text_paths(soup)
        content_paths = []
        densest_text_path, dense_text_paths = self.__soup_helper.get_densest_text_path_and_dense_text_path(
            text_paths)

        last_text_path = ''
        for text_path in text_paths:
            if not self.__soup_helper.is_in_parent_path(densest_text_path, text_path):
                continue

            text_path_elements = text_path.split(' ')
            text_path_elements.pop()

            images, anchors, path = self.__soup_helper.get_nearest_images_anchors_path(
                soup, ' '.join(text_path_elements))

            if len(text_paths[text_path]) < 70:
                continue

            if path == '':
                continue

            anchor_length = 1 if len(anchors) == 0 else len(anchors)
            if len(dense_text_paths[path]) <= 15:
                total_anchor_content_length = 1
                for i in anchors:
                    total_anchor_content_length += len(i)

                if (len(dense_text_paths[path]) - anchor_length > 3 and self.__string_helper.is_paragraph(text_paths[text_path])) \
                        or (float(len(text_paths[text_path])) / total_anchor_content_length >= 2)\
                        or (len(text_paths[text_path]) >= 200):
                   last_text_path = text_path
                   content_paths.append(text_path)

            else:
                if (float(len(dense_text_paths[path])) / anchor_length > 1.2 and self.__string_helper.is_paragraph(text_paths[text_path])) \
                        or len(text_paths[text_path]) >= 200:
                    last_text_path = text_path
                    content_paths.append(text_path)

        preceding_tex_paths = []
        for text_path in text_paths:
            preceding_tex_paths.append(text_path)
            if text_path == last_text_path:
                break

        title_text_path, title_top_position = self.__get_title_path(text_paths, d_text_path_container_id, d_page_container_info)
        description_text_path = self.__get_description_path(title_text_path, title_top_position, text_paths,
                                                       d_text_path_container_id, d_page_container_info)

        content_path = self.__get_content_path(title_text_path, content_paths)

        inferred_published_dates_map = self.__soup_helper.get_publish_date(text_paths)
        published_date = ''
        nearest_distance = 10000000

        # Check date below title
        for path in inferred_published_dates_map:
            container_info = self.__soup_helper.get_container_info_by_path(soup, d_page_container_info, path)
            if title_top_position - int(container_info['top']) < -1:
                distance = abs(title_top_position - int(container_info['top']))
                if distance < 300 and distance < nearest_distance:
                    nearest_distance = distance
                    published_date = inferred_published_dates_map[path]

        # Check date above of title
        if published_date == '':
            for path in inferred_published_dates_map:
                container_info = self.__soup_helper.get_container_info_by_path(soup, d_page_container_info, path)
                if title_top_position - int(container_info['top']) >= 0:
                    distance = abs(title_top_position - int(container_info['top']))
                    if distance < 300 and distance < nearest_distance:
                        nearest_distance = distance
                        published_date = inferred_published_dates_map[path]

        raw_main_content_soup = self.__soup_helper.get_soup_by_path(
            clonned_soup, content_path)
        main_content_soup = self.__soup_helper.get_soup_by_path(
            soup, content_path)
        main_content_text_paths, _ = self.__soup_helper.get_text_paths(
            main_content_soup)
        _, main_content_dense_text_paths = self.__soup_helper.get_densest_text_path_and_dense_text_path(
            main_content_text_paths)

        inferred_main_content = {}
        for dense_text_path in main_content_dense_text_paths.keys():
            text_path_elements = dense_text_path.split(' ')
            if dense_text_path.find('text_node') > -1:
                text_path_elements.pop()

            images, anchors, path = self.__soup_helper.get_nearest_images_anchors_path(
                main_content_soup, ' '.join(text_path_elements), True)

            if path == '':
                continue

            non_anchor_contents = self.__get_real_non_anchor_text_paths(path, main_content_text_paths)
            total_non_anchor_content_length = 1
            for i in non_anchor_contents:
                total_non_anchor_content_length += len(self.__string_helper.convert_vietnamese_to_eng(i))

            if total_non_anchor_content_length < 70:
                continue

            inferred_main_content[self.__get_real_path(content_path, path).strip()] = total_non_anchor_content_length

        title_path = self.__soup_helper.convert_text_path_to_path(title_text_path)
        title_container_info = self.__get_text_node_container_info(title_text_path, d_text_path_container_id, d_page_container_info)
        bound_top = title_container_info['top']

        highest_text = -1
        real_main_content_path = ''
        for path in inferred_main_content:
            container_info = self.__soup_helper.get_container_info_by_path(soup, d_page_container_info, path)
            if container_info['top'] == 0 or abs(container_info['top'] - bound_top) > 800 or container_info['top'] < 150:
                continue

            if title_path.strip() == path.strip():
                continue

            if inferred_main_content[path] > highest_text:
                highest_text = inferred_main_content[path]
                real_main_content_path = path

        if real_main_content_path == '':
            raise Exception('Cant find real main content path of url: {}'.format(url))

        new_soup = self.__soup_helper.get_soup_by_path(soup, real_main_content_path)
        main_content_text_paths, _ = self.__soup_helper.get_text_paths(
            new_soup)

        _, main_content_dense_text_paths = self.__soup_helper.get_densest_text_path_and_dense_text_path(
            main_content_text_paths)

        main_content_sub_soups = []
        hidden_content_sub_soups = []
        unnumber_path_dict = dict([])
        for dense_text_path in main_content_dense_text_paths.keys():
            real_path = self.__get_real_path(real_main_content_path, dense_text_path)
            container_info = self.__soup_helper.get_container_info_by_path(soup, d_page_container_info, real_path)

            container_width = int(container_info['width'])
            container_visibility = container_info['visibility'].lower()
            container_display = container_info['visibility'].lower()
            container_font_size = container_info['fontSize'].lower()
            if container_width < 350 or container_visibility in ('hidden', 'collapse') or container_display == 'none' \
                    or container_font_size == '0px':
                hidden_content_sub_soups.append(self.__soup_helper.get_soup_by_path(new_soup, dense_text_path))

            if dense_text_path.find('text_node') < 0:
                continue

            text_path_elements = dense_text_path.split(' ')
            text_path_elements.pop()

            current_text_path = ' '.join(text_path_elements)
            images, anchors, path = self.__soup_helper.get_nearest_images_anchors_path(
                main_content_soup, current_text_path, False)

            if len(main_content_text_paths[dense_text_path]) < 70:
                main_content_sub_soups.append(self.__soup_helper.get_soup_by_path(new_soup, current_text_path))

            if self.__is_anchor_group(main_content_text_paths[dense_text_path]):
                main_content_sub_soups.append(self.__soup_helper.get_soup_by_path(new_soup, current_text_path))

            if dense_text_path.find('a_') > -1:
                main_content_sub_soups.append(self.__soup_helper.get_soup_by_path(new_soup, current_text_path))

            non_anchor_contents = self.__get_real_non_anchor_text_paths(path, main_content_text_paths)
            total_non_anchor_content_length = 1
            for i in non_anchor_contents:
                total_non_anchor_content_length += len(self.__string_helper.convert_vietnamese_to_eng(i))

            total_anchor_content_length = 1
            for i in anchors:
                total_anchor_content_length += len(self.__string_helper.convert_vietnamese_to_eng(i))

            if self.__soup_helper.is_standalone_href(main_content_text_paths, dense_text_path):
                main_content_sub_soups.append(self.__soup_helper.get_soup_by_path(new_soup, current_text_path))

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

        # Improve for removing title of category group
        for unnumber_path in unnumber_path_dict:
            if len(unnumber_path_dict[unnumber_path]) < 2:
                continue

            current_anchor_paths = unnumber_path_dict[unnumber_path]
            for path in current_anchor_paths:
                real_parent_path = get_real_parent_anchor_path(
                    path, current_anchor_paths
                )
                main_content_sub_soups.append(self.__soup_helper.get_soup_by_path(new_soup, real_parent_path))

        for sub_soup in main_content_sub_soups:
            if (len(sub_soup.getText()) < highest_text / 10) or len(sub_soup.getText()) < 150:
                sub_soup.extract()

        for sub_soup in hidden_content_sub_soups:
            sub_soup.extract()

        for img in new_soup.findAll('img'):
            container_info = d_page_container_info[img['fi_ai_key_id']]
            if container_info['width'] < 250 or str(img).find('.gif') > -1:
                img.extract()

        title = text_paths[title_text_path]
        description = ''
        if description_text_path in text_paths:
            description = text_paths[description_text_path]

        else:
            self.__logger_service.debug(
                'Description not found in url: {}'.format(url))

        if fallback_soup != '':
            new_soup = fallback_soup

        if len(new_soup.getText()) < 50:
            new_soup = raw_main_content_soup

        for tag in new_soup.findAll():
            if tag.getText().strip() == title.strip() and title.strip() != '':
                tag.extract()
            if tag.getText() == description.strip() and description.strip() != '':
                tag.extract()

        new_soup = self.__soup_helper.remove_all_attributes_except(
            new_soup, ['src', 'href'])
        self.__soup_helper.unwrap_except_valid_tags(
            new_soup, ['p', 'img', 'a'])

        if meta_description != '':
            description = meta_description

        if meta_title.strip() != '':
            title = meta_title

        if hack_title_content.strip() != '':
            title = hack_title_content

        if hack_publish_date.strip() != '':
            published_date = hack_publish_date

        comment = json.dumps([])

        new_soup = new_soup
        if len(new_soup.getText()) < 200:
            new_soup = raw_main_content_soup

        new_soup = str(new_soup)
        raw_main_content_soup = str(raw_main_content_soup)
        return title, description, new_soup, raw_main_content_soup, comment, published_date

    def __load_json(self, json_string=''):
        try:
            json_object = json.loads(json_string)
        except ValueError:
            return None

        return json_object

    def __get_title_path(self, text_paths: List[str], text_path_container_id: dict, container_info: dict):
        title_path = ''
        title_top_position = 0
        title_font_size = -1
        for text_path in text_paths:
            container_id = text_path_container_id[text_path]
            container_margin_top = int(container_info[container_id]['top'])
            container_width = int(container_info[container_id]['width'])
            container_visibility = container_info[container_id]['visibility']
            container_display = container_info[container_id]['display']
            container_font_size = container_info[container_id]['fontSize']

            if not (container_margin_top != 0 and container_margin_top < 1000):
                continue

            if not (container_width > 300 and container_visibility not in ('hidden', 'collapse')
                    and container_display != 'none'):
                continue

            current_font_size = int(container_font_size.replace('px', ''))
            if current_font_size > title_font_size:
                title_font_size = current_font_size
                title_path = text_path
                title_top_position = container_margin_top

        return title_path, title_top_position

    def __get_description_path(self, title_path: str, title_top_position: int, text_paths: List[str], text_path_container_id: dict, container_info: dict):
        start_capture = False
        description_path = ''

        for text_path in text_paths:
            container_id = text_path_container_id[text_path]
            container_margin_top = int(container_info[container_id]['top'])
            container_width = int(container_info[container_id]['width'])
            container_visibility = container_info[container_id]['visibility']
            container_display = container_info[container_id]['display']
            container_font_size = container_info[container_id]['fontSize']
            container_font_weight = container_info[container_id]['fontWeight']
            container_font_style = container_info[container_id]['fontStyle']

            if start_capture:
                if abs(container_margin_top - title_top_position) > 300:
                    continue

                if container_width < 250:
                    continue

                if container_visibility in ('hidden', 'collapse') or container_display == 'none':
                    continue

                if container_font_weight.isdigit() and int(container_font_weight) > 500:
                    description_path = text_path
                    break

                else:
                    if container_font_weight in('bold', 'bolder'):
                        description_path = text_path
                        break
                    elif container_font_style == 'italic':
                        description_path = text_path
                        break

            else:
                if text_path == title_path:
                    start_capture = True

        return description_path

    def __get_content_path(self, title_path='', content_paths=[]):
        title_path_elements = title_path.split(' ')

        while len(title_path_elements) > 0:
            current_title_path = ' '.join(title_path_elements)

            total_match = 0
            for content_path in content_paths:
                if content_path.find(current_title_path) > -1:
                    total_match += 1

            if total_match == len(content_paths):
                return current_title_path

            title_path_elements.pop()

        return ''

    def __get_real_non_anchor_text_paths(self, dense_text_path, main_content_text_paths):
        contents = []
        for text_path in main_content_text_paths.keys():
            if text_path.find(dense_text_path) == 0 and text_path.find('a_') < 0:
                non_accent_text = self.__string_helper.convert_vietnamese_to_eng(main_content_text_paths[text_path])
                if len(non_accent_text) > 20:
                    contents.append(main_content_text_paths[text_path])
        return contents

    def __get_real_path(self, previous_path, current_path):
        return previous_path.strip() + ' ' + current_path.strip()

    def __remove_number_path(self, path):
        return re.sub('(_[0-9]+)', '', path)
