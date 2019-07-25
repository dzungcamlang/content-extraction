# -*- coding: utf-8 -*-

import re
import datetime
import time
from fn.recur import tco
from typing import List
from internal.helper.string_helper import StringHelper
from collections import OrderedDict
from bs4 import BeautifulSoup, NavigableString, Tag


class SoupHelper:
    def __init__(self):
        self.__string_Helper = StringHelper()
        pass

    def unwrap_self_close_tags(self, soup=BeautifulSoup('', 'html.parser')):
        for tag in soup.find_all('area'):
            tag.unwrap()

        for tag in soup.find_all('base'):
            tag.unwrap()

        for tag in soup.find_all('br'):
            tag.unwrap()

        for tag in soup.find_all('col'):
            tag.unwrap()

        for tag in soup.find_all('command'):
            tag.unwrap()

        for tag in soup.find_all('embed'):
            tag.unwrap()

        for tag in soup.find_all('hr'):
            tag.unwrap()

        for tag in soup.find_all('input'):
            tag.unwrap()

        for tag in soup.find_all('label'):
            tag.unwrap()

        for tag in soup.find_all('link'):
            tag.unwrap()

        for tag in soup.find_all('meta'):
            tag.unwrap()

        for tag in soup.find_all('param'):
            tag.unwrap()

        for tag in soup.find_all('source'):
            tag.unwrap()

    def strip_tags(self, soup=BeautifulSoup('', 'html.parser'), invalid_tags=[]):
        for tag in invalid_tags:
            for match in soup.findAll(tag):
                match.replaceWithChildren()

        return soup

    def clone_soup(self, el):
        if isinstance(el, NavigableString):
            return type(el)(el)

        copy = Tag(None, el.builder, el.name, el.namespace, el.nsprefix)
        # work around bug where there is no builder set
        # https://bugs.launchpad.net/beautifulsoup/+bug/1307471
        copy.attrs = dict(el.attrs)
        for attr in ('can_be_empty_element', 'hidden'):
            setattr(copy, attr, getattr(el, attr))
        for child in el.contents:
            copy.append(self.clone_soup(child))

        return copy

    def get_nearest_images_anchors_path(self, soup=BeautifulSoup('', 'html.parser'), path='', is_check_on_anchor=False):
        path_elements = path.split(' ')
        while True:
            if len(path_elements) < 1:
                break

            images, anchors = self.get_image_and_anchor_by_path(soup, ' '.join(path_elements), is_check_on_anchor)
            if len(anchors) >= 1:
                return images, anchors, ' '.join(path_elements)

            path_elements.pop()
        return [], [], ''

    def get_image_and_anchor_by_path(self, soup: BeautifulSoup, path='', is_check_on_anchor=False):
        # Check a tag contain img tag
        nodes = path.split(' ')
        sub_soup = soup

        while len(nodes) > 0:
            node_info = nodes[0].split('_')
            count = 1
            for element in sub_soup.childGenerator():
                if element.name == node_info[0]:
                    if count == int(node_info[1]):
                        sub_soup = element
                        break
                    count += 1
            nodes = nodes[1:]

        images = []
        for image in sub_soup.find_all('img', src=True):
            images.append(image)

        anchors = []
        for anchor in sub_soup.find_all('a', href=True):
            if is_check_on_anchor:
                anchors.append(anchor.getText())
            else:
                if len(anchor.getText()) > 20:
                    anchors.append(anchor.getText())

        return images, anchors

    def convert_text_path_to_path(self, text_path=''):
        nodes = text_path.split(' ')
        return ' '.join(nodes[:len(nodes) - 1])

    def is_href_tag(self, path=''):
        nodes = path.split(' ')
        current_tag = nodes[len(nodes) - 1]
        current_tag_info = current_tag.split('_')
        if current_tag_info[0] == 'a':
            return True
        return False

    def is_standalone_href(self, text_paths=OrderedDict(), text_path=''):
        is_standalone = True
        current_path = ' '.join(text_path.split(' ')[:len(text_path.split(' ')) - 1])
        if not self.is_href_tag(current_path):
            return False

        nodes = current_path.split(' ')
        while current_path.strip() != '':
            supposed_text_path = ' '.join(nodes[:len(nodes) - 1]) + ' text_node'
            for path in text_paths:
                if supposed_text_path == path:
                    is_standalone = False
                    break

            current_path = ' '.join(nodes[:len(nodes) - 1])
            nodes = current_path.split(' ')
        return is_standalone

    def get_soup_by_path(self, soup=BeautifulSoup('', 'html.parser'), path=''):
        nodes = path.split(' ')
        sub_soup = soup
        while len(nodes) > 0:
            node_info = nodes[0].split('_')
            count = 1
            for element in sub_soup.childGenerator():
                if element.name == node_info[0]:
                    if count == int(node_info[1]):
                        sub_soup = element
                        break
                    count += 1
            nodes = nodes[1:]

        return sub_soup

    def get_nearest_parent_path(self, dense_paths=OrderedDict(), path=''):
        path_elements = path.split(' ')
        last_element = path_elements[len(path_elements) - 1]

        while len(path_elements) > 0:
            current_dense_path = ' '.join(path_elements)

            if len(dense_paths[current_dense_path]) > 1:
                return current_dense_path, current_dense_path + ' ' + last_element

            last_element = path_elements.pop()

        return ''

    def get_child_paths_from_parent_path(self, parent_path='', html_tree=OrderedDict()):
        paths = []

        for path, value in html_tree:
            if path.find(parent_path) > -1 and path != parent_path:
                paths.append(path)

        return paths

    def is_in_parent_path(self, parent_text_path='', text_path=''):
        if text_path.find(parent_text_path) == 0:
            return True
        return False

    def get_densest_text_path_and_dense_text_path(self, text_paths=OrderedDict()):
        dense_text_path = OrderedDict()
        highest_point = 0

        for path in text_paths:
            path_elements = path.split(" ")
            current_path = []

            for path_element in path_elements:
                current_path.append(path_element)
                key = ' '.join(current_path)

                if key not in dense_text_path:
                    dense_text_path[key] = []

                dense_text_path[key].append(text_paths[path])
                if highest_point < len(dense_text_path[key]):
                    highest_point = len(dense_text_path[key])

        if len(dense_text_path.keys()) == 0:
            raise Exception('Dense text path is zero.')

        longest_path = ''
        current_highest_point = 0
        for i in dense_text_path:
            if i in ('html_1', 'html_1 body_1', 'html_1 footer_1', 'html_1 head_1', 'html_1 head_1 title_1',
                           'html_1 body_1 footer_1', 'html_1 head_1 body_1'):
                continue

            if highest_point >= len(dense_text_path[i]) >= current_highest_point:
                longest_path = i
                current_highest_point = len(dense_text_path[i])

        return longest_path, dense_text_path

    def get_text_paths(self, soup: BeautifulSoup):
        l_current_path = []
        d_text_paths = OrderedDict()
        d_text_path_container_id = {}
        self.__get_text_paths_recursive(soup, l_current_path, d_text_paths, d_text_path_container_id)
        return d_text_paths, d_text_path_container_id

    def __get_text_paths_recursive(self, soup: BeautifulSoup, l_current_path: List[str],
                                   d_text_paths: dict, d_text_path_container_id: dict):
        if len(l_current_path) > 0 and l_current_path[-1] == 'text_node':
            if soup.name is None:
                text_content = str(soup).strip()
                if text_content != '':
                    text_path_key = ' '.join(l_current_path)
                    d_text_paths[text_path_key] = text_content
            else:
                text_content = soup.getText().strip()
                if text_content != '':
                    text_path_key = ' '.join(l_current_path)
                    d_text_paths[text_path_key] = text_content

        else:
            current_track = {}
            l_current_tracking_text_pattern = []
            text_node_length = 0
            for child in soup.childGenerator():
                if child.name is None:
                    if len(child.strip()) > 0:
                        text_node_length += len(child.strip())
                        l_current_tracking_text_pattern.append(child)

                else:
                    if len(child.getText().strip()) > 0:
                        l_current_tracking_text_pattern.append(child)

            if self.__is_parent_text_node(l_current_tracking_text_pattern) or text_node_length > 300:
                l_current_path.append('text_node')
                text_path_key = ' '.join(l_current_path)
                d_text_path_container_id[text_path_key] = soup['fi_ai_key_id']
                self.__get_text_paths_recursive(soup, l_current_path, d_text_paths, d_text_path_container_id)
                l_current_path.pop()

            else:
                for child in soup.childGenerator():
                    current_tag = child.name
                    count = 0
                    if child.name is not None:
                        while True:
                            count += 1
                            current_key = current_tag + "_" + str(count)

                            if current_key not in current_track:
                                current_track[current_key] = True
                                current_tag = current_key
                                break

                    else:
                        current_tag = "text_node"
                        text_path_key = ' '.join(l_current_path) + ' ' + current_tag
                        d_text_path_container_id[text_path_key] = soup['fi_ai_key_id']

                    l_current_path.append(current_tag)
                    self.__get_text_paths_recursive(child, l_current_path, d_text_paths, d_text_path_container_id)
                    l_current_path.pop()

    def __is_parent_text_node(self, l_tag: List[Tag]):
        if len(l_tag) <= 1:
            return False

        # All tag a is category so we ignore it
        is_contain_all_anchor = True
        for tag in l_tag:
            if tag.name != 'a':
                is_contain_all_anchor = False
                break

        if is_contain_all_anchor:
            return False

        for tag in l_tag:
            if tag.name is None or tag.name == 'a':
                continue

            if tag.getText().strip() == '':
                continue

            # Check if nested struct has invalid text node struct
            # Which is only contain navigatestring not another.
            for child_tag in tag.childGenerator():
                if child_tag.name is None:
                    continue

                if child_tag.getText().strip() == '':
                    continue

                return False

        return True

    def __is_valid_publish_date(self, day: int, month: int, year: int):
        if day < 1 or day > 31:
            return False

        if month < 1 or month > 12:
            return False

        if year < 100:
            if year < 10 or year > 17:
                return False
            else:
                year = year + 2000
        else:
            if year < 2000 or year > 2017:
                return False

        s = "{}/{}/{}".format(day, month, year)
        time_stamp = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
        return datetime.datetime.now().timestamp() > time_stamp

    def __is_publish_date(self, txt=''):
        patterns = [
            r'(?:^|[\ \-\|]+|\()([0-9]+)[\ ]*\.[\ ]*([0-9]+)[\ ]*\.[\ ]*([0-9]+)(?:$|[\ \-\|\,]+|\))',
            r'(?:^|[\ \-\|]+|\()([0-9]+)[\ ]*\/[\ ]*([0-9]+)[\ ]*\/[\ ]*([0-9]+)(?:$|[\ \-\|\,]+|\))',
            r'(?:^|[\ \-\|]+|\()([0-9]+)[\ ]*\-[\ ]*([0-9]+)[\ ]*\-[\ ]*([0-9]+)(?:$|[\ \-\|\,]+|\))',
        ]

        for pattern in patterns:
            date_time_search = re.search(pattern, txt, re.IGNORECASE)
            if date_time_search:
                day = int(date_time_search.group(1))
                month = int(date_time_search.group(2))
                year = int(date_time_search.group(3))
                if self.__is_valid_publish_date(day, month, year) or self.__is_valid_publish_date(year, month, day):
                    return True

        return False

    def __is_article_published_date(self, txt):
        txt = ''.join([i if ord(i) < 128 else ' ' for i in txt])
        txt = ' '.join(list(filter(lambda x: x != '', txt.split(' '))))
        txt = txt.replace('\n', '')

        if len(txt.strip()) < 150 and self.__is_publish_date(txt):
            return True
        return False

    def get_publish_date(self, text_paths: dict) -> dict:
        d_inferred_published_date = {}
        for text_path in text_paths:
            if self.__is_article_published_date(text_paths[text_path]):
                d_inferred_published_date[text_path] = text_paths[text_path]
        return d_inferred_published_date

    def unwrap_except_valid_tags(self, soup=BeautifulSoup('', 'html.parser'), valid_tags=[]):
        for tag in soup.find_all(True):
            if tag.name not in valid_tags:
                tag.unwrap()

    def remove_all_attributes_except(self, soup: BeautifulSoup, l_allow_attributes: List[str]):
        for tag in soup.find_all(True):
                attrs = dict(tag.attrs)

                for attr in attrs:
                    if attr not in l_allow_attributes:
                        del tag.attrs[attr]
        return soup

    def get_general_path(self, text_path):
        soup_helper = SoupHelper()
        path = soup_helper.convert_text_path_to_path(text_path)
        return re.sub(r'_([0-9]*) ', r' ', path)

    def get_container_info_by_path(self, soup: BeautifulSoup, d_page_container_info: dict, path: str) -> dict:
        nodes = path.split(' ')
        sub_soup = soup
        while len(nodes) > 0:
            node_info = nodes[0].split('_')
            count = 1
            for element in sub_soup.childGenerator():
                if element.name == node_info[0]:
                    if count == int(node_info[1]):
                        sub_soup = element
                        break
                    count += 1
            nodes = nodes[1:]
        # if path == 'html_1 body_1 div_2 table_1 tbody_1 tr_1 td_1 div_1 div_1 div_2 div_1':
        #     print(sub_soup)
        container_id = sub_soup['fi_ai_key_id']
        return d_page_container_info[container_id]