import requests
import re
import os
import sys, traceback

from bs4 import BeautifulSoup
from internal.helper.string_helper import StringHelper
from internal.helper.url_helper import URLHelper
from internal.service.logger.factory import LoggerFactory


class TrainingCategoryPagination:
    __url = ''
    __domain = ''
    __string_helper = StringHelper()
    __url_helper = URLHelper()
    __logger_service = LoggerFactory().get_logger_service().logger

    def __init__(self, url):
        """

        Args:
            url (unicode): URL for training category pagination.

        """
        self.__url = url
        self.__domain = self.__url_helper.get_domain_from_url(url)

    def training_category_pagination(self):
        try:
            """

            Returns:
                str if found the pagination pattern. None: If can't find the category pagination pattern.

            """
            print('============= Start training category pagination =============')
            print('Preparing for guessing {}'.format(self.__url))

            category_url_without_extension = self.__remove_extension(self.__url)
            inference_category_urls = self.__get_inference_category_urls(
                category_url_without_extension, self.__url)

            classified_category_url_pattern = \
                self.__classify_pattern_inference_category_url(
                    category_url_without_extension, inference_category_urls)

            category_pattern_tier_1 = self.__guess_pagination_pattern_tier_1(
                classified_category_url_pattern)

            if category_pattern_tier_1 is None:
                complete_pattern = self.__guess_pagination_pattern_tier_2(
                    self.__url)

            else:
                complete_pattern = '{}{}'.format(
                    category_url_without_extension, category_pattern_tier_1)

            print('============= Stop training category pagination =============')
        except Exception as err:
            print(str(err))
            traceback.print_exc(file=sys.stdout)
            print("=================")
            print("=================")
            print("=================")

        return complete_pattern

    def __guess_pagination_pattern_tier_2(self, category_url):
        """

        Args:
            category_url (unicode):

        Returns:
            str if found the pagination pattern. None: If can't find the category pagination pattern.

        """
        page_content = self.__get_page_content(category_url)
        page_content_soup = BeautifulSoup(page_content, 'html.parser')
        related_links = set(self.__get_related_links(page_content_soup))

        d_inferred_category_pattern = {}
        category_url_num_matches = self.__get_num_mactches(category_url)
        for category_url_num_match in category_url_num_matches:
            d_inferred_category_pattern[category_url[:category_url_num_match[0]]] = {
                'full_pattern': category_url[:category_url_num_match[0]] + '{integer}' + category_url[category_url_num_match[1]:],
                'candidate': []
            }

        for link in related_links:
            link_num_matches = self.__get_num_mactches(link)
            if len(category_url_num_matches) != len(link_num_matches):
                continue

            for match_group_index in range(0, len(category_url_num_matches), 1):
                current_category_num_group = category_url_num_matches[
                    match_group_index]
                current_link_num_group = link_num_matches[match_group_index]

                current_category_num = int(category_url[current_category_num_group[
                                           0]:current_category_num_group[1]])
                current_link_num = int(
                    link[current_link_num_group[0]:current_link_num_group[1]])

                if current_link_num != current_category_num \
                        and abs(current_link_num - current_category_num) < 100 \
                        and current_link_num < 1000:

                    for pattern in d_inferred_category_pattern:
                        if pattern == link[:current_link_num_group[0]]:
                            d_inferred_category_pattern[pattern]['candidate'].append(link)
        print(d_inferred_category_pattern)

        for pattern in d_inferred_category_pattern:
            if len(d_inferred_category_pattern[pattern]['candidate']) >= 2:
                return d_inferred_category_pattern[pattern]['full_pattern']

        return None

    def __get_num_mactches(self, url):
        return [(m.start(0), m.end(0)) for m in re.finditer(r'([0-9]+)', url)]

    def __get_page_content(self, url):
        """

        Args:
            url (unicode): url for retrieving content.

        Returns:
            str: Content of page.

        """
        try:
            response = requests.get(url, timeout=5)
            page_content = response.content
        except Exception:
            return ''

        return page_content

    def __get_inference_category_urls(self, category_url_without_extension, url):
        """

        Args:
            category_url_without_extension (unicode):
            url (unicode):

        Returns:

        """
        page_content = self.__get_page_content(url)
        page_content_soup = BeautifulSoup(page_content, 'html.parser')
        related_links = self.__get_related_links(page_content_soup)
        non_duplicated_related_links = self.__remove_duplicate_url(
            related_links)
        inference_category_urls = list(filter(
            lambda url: url.find(category_url_without_extension) > -1,
            non_duplicated_related_links
        ))
        return inference_category_urls

    def __guess_pagination_pattern_tier_1(self, classified_category_url_pattern):
        """

        Args:
            classified_category_url_pattern (dict): Category patterns of inference urls.

        Returns:
            str if found the pagination pattern. None: If can't find the category pagination pattern.

        """
        pattern_guess_tier_1 = self.__guess_pagination_pattern_by_frequency(
            classified_category_url_pattern)
        if pattern_guess_tier_1 is not None:
            return pattern_guess_tier_1

        pattern_guess_tier_2 = self.__guess_pagination_pattern_by_pages_similarity(
            classified_category_url_pattern)
        return pattern_guess_tier_2

    def __guess_pagination_pattern_by_pages_similarity(self, classified_category_url_pattern):
        """

        Args:
            classified_category_url_pattern (dict): Category patterns of inference urls.

        Returns:
            str if found the pagination pattern. None: If can't find the category pagination pattern.

        """
        category_patterns = list(classified_category_url_pattern.keys())
        category_patterns.sort(key=len, reverse=False)

        pagination_pattern = self.__guess_pagination_pattern_by_pages_similarity_r(
            category_patterns, classified_category_url_pattern
        )

        return pagination_pattern

    def __guess_pagination_pattern_by_pages_similarity_r(self, patterns, classified_category_url_pattern):
        """

        Args:
            patterns list(unicode):
            classified_category_url_pattern (dict):

        Returns:
            str if found the pagination pattern. None: If can't find the category pagination pattern.

        """
        if len(patterns) < 1:
            return None

        else:
            current_pattern = patterns[0]
            inference_url = classified_category_url_pattern[
                current_pattern][0]['url']
            is_pagination_url = self.__is_pagination_url(
                current_pattern, inference_url)

            print('Guessing pagination for url: {}. With pattern: {}'.format(self.__url, current_pattern))

            if is_pagination_url:
                return current_pattern

            else:
                return self.__guess_pagination_pattern_by_pages_similarity_r(
                    patterns[1:], classified_category_url_pattern
                )

    def __get_category_pagination_pattern(self, left_part, right_part):
        """

        Args:
            left_part (unicode): left part of pattern.
            right_part (unicode): right part of pattern.

        Returns:
            unicode: category pagination pattern.

        """
        return '{}{}{}'.format(left_part, '{integer}', right_part)

    def __is_pagination_url(self, pattern, inference_url):
        """

        Args:
            inference_url (unicode):
            pattern (unicode):

        Returns:
            True: if could find the pattern. False: if could not find the pattern.

        """
        category_url_without_extension = self.__remove_extension(self.__url)
        inference_category_urls = self.__get_inference_category_urls(
            category_url_without_extension, inference_url)
        regex_pattern = self.__get_category_regex_pattern(
            category_url_without_extension)
        p = re.compile(regex_pattern)
        for url in inference_category_urls:
            try:
                matches = p.findall(url)[0]
                if len(matches) > 1 and matches[1] == '':
                    continue

                similarity_count = 0
                category_pattern = self.__get_category_pagination_pattern(matches[
                                                                          0], matches[2])
                cleaned_inference_url = self.__url_helper.clear_hash_tag(
                    inference_url).strip()
                cleaned_url = self.__url_helper.clear_hash_tag(url).strip()

                if category_pattern == pattern and cleaned_url != cleaned_inference_url and int(matches[1]) < 1000:
                    similarity_count += 1

                if similarity_count > 0:
                    return True

            except Exception:
                pass

        return False

    def __get_category_regex_pattern(self, category_url):
        """

        Args:
            category_url (unicode):

        Returns:
            str: regex pattern of current category.

        """
        escaped_root_category_url = re.escape(category_url)
        regex_pattern = r'{}'.format(
            escaped_root_category_url) + r'([^0-9]*)([0-9]*)(.*)'
        return regex_pattern

    def __guess_pagination_pattern_by_frequency(self, classified_category_url_pattern):
        """

        Args:
            classified_category_url_pattern (dict): Category patterns of inference urls.

        Returns:
            str if found the pagination pattern. None: If can't find the category pagination pattern.

        """
        for pattern in classified_category_url_pattern:
            if len(classified_category_url_pattern[pattern]) > 1:
                distances_frequency = self.__get_ordering_distances_frequency(
                    list(map(lambda detail: int(detail['matches'][
                        1]), classified_category_url_pattern[pattern]))
                )

                if 1 in distances_frequency and distances_frequency[1] > 1:
                    return pattern

        return None

    def __remove_duplicate_url(self, list_text):
        """

        Args:
            list_text (list[unicode]): list text with duplicate elements.

        Returns:
            list[unicode]: return list with no duplication.

        """
        return list(set(list_text))

    def __classify_pattern_inference_category_url(self, root_category_url, inference_category_urls):
        """

        Args:
            root_category_url (unicode): Root category url for classifying.
            inference_category_urls (list[unicode]): List of inference category url for classifying pattern.

        Returns:
            dict: return dictionary of inference category url.

        """
        escaped_root_category_url = re.escape(root_category_url)
        regex_pattern = r'{}'.format(
            escaped_root_category_url) + r'([^0-9]*)([0-9]*)(.*)'
        classified_category_url_pattern = {}
        for url in inference_category_urls:
            p = re.compile(regex_pattern)
            matches = p.findall(url)[0]
            if matches[1] == '':
                continue

            category_pattern = '{}{}{}'.format(matches[0], '{integer}', matches[2])
            if category_pattern not in classified_category_url_pattern:
                classified_category_url_pattern[category_pattern] = []

            classified_category_url_pattern[category_pattern].append({
                'matches': matches,
                'url': url
            })

        return classified_category_url_pattern

    def __get_ordering_distances_frequency(self, nums):
        """

        Args:
            nums (list[int]): list nums for getting distance.

        Returns:
            list[int]: list of ordering distance.

        """
        nums.sort()
        if len(nums) < 2:
            return nums

        distances = {}
        for i in range(0, len(nums) - 1, 1):
            distance = nums[i + 1] - nums[i]
            if distance not in distances:
                distances[distance] = 0

            distances[distance] += 1

        return distances

    def __remove_extension(self, text):
        """

        Args:
            text (unicode): String include extension.

        Returns:
            unicode: text without extension.

        """
        base = os.path.basename(text)
        base_parts = base.split('.')

        if len(base_parts) < 2:
            return text

        replaced_text = text[:text.find('.' + base_parts[1])]
        return replaced_text

    def __get_related_links(self, soup):
        """

        Args:
            soup (BeautifulSoup: soup for getting all links.

        Returns:
            list[unicode]: related links in that page.

        """
        a_tags = soup.find_all('a', href=True)
        same_domain_links = list(filter(lambda a_tag: self.__url_helper.is_same_domain(
            self.__domain, a_tag['href']), a_tags))
        cleaned_links = list(map(lambda href: self.__clean_link(
            href['href']), same_domain_links))
        non_error_fulfilled_links = list(filter(
            lambda link: link != '', cleaned_links))

        return non_error_fulfilled_links

    def __clean_link(self, url):
        """

        Args:
            url (unicode):

        Returns:


        """
        fulfilled_url = ''
        try:
            if url[0] == '/':
                fulfilled_url = self.__url_helper.fulfill_domain_path(
                    self.__domain, url)

            else:
                fulfilled_url = url

        except Exception as err:
            self.__logger_service.warn(err)

        return self.__url_helper.clear_hash_tag(fulfilled_url)
