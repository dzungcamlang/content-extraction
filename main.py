# -*- coding: utf-8 -*-

import time
import requests
import os
import json
import traceback
import logging

from bs4 import BeautifulSoup
from flask_cors import CORS
from flask import Flask
from flask import request
from concurrent.futures import ProcessPoolExecutor
from internal.handler.extract_data import ExtractData
from internal.service.logger.factory import LoggerFactory
from internal.service.browser.factory import BrowserFactory
from internal.helper.string_helper import StringHelper
from internal.helper.file_helper import FileHelper
from internal.handler.trainer import Trainer
from internal.handler.training_category_pagination import TrainingCategoryPagination
from internal.helper.url_helper import URLHelper
from internal.constant.constant import Constant


processes = {}
url_helper = URLHelper()
string_helper = StringHelper()
file_helper = FileHelper()
constant = Constant()

logger_service = LoggerFactory().get_logger_service().logger
logger_service.setLevel(logging.DEBUG)
billion = 10**9

mbm_endpoint = os.getenv(
    'MAGIC_BROWSER_MASTER_ENDPOINT', 'http://localhost:5000')
is_test_api = os.getenv(
    'IS_TEST_API', '0')

MAX_WORKER = int(os.getenv('MAX_WORKER', 20))

app = Flask(__name__)
app.debug = True
CORS(app)

# constants for kafka
# TOPIC_DEBUG = 'debug'
TOPIC_LINKS = 'links'
TOPIC_RECORDS = 'records'
TOPIC_AMBIGUOUS_LINK = 'ambiguous-link'
TOPIC_HEARTBEAT = 'heartbeat'
# TOPIC_KAFKA_TRACKING = 'kafka-tracking'
TOPIC_TRAINING_ASSETS = 'training-assets'
TOPIC_REQUEST_CRAWLER_NEWS = 'request-crawler-news'
TOPIC_REQUEST_TRAINING_DOMAIN = 'request-training-domain'
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
# GROUP_ID = None
GROUP_ID = 'crawler-news-group'
AUTO_OFFSET_RESET = 'smallest'  # or 'latest',

BOOTSTRAP_SERVERS = os.getenv('BOOTSTRAP_SERVERS', '103.234.37.70:9002')
PROCESSING_QUOTA = int(os.getenv('PROCESSING_QUOTA', '1000'))

logger_service.debug(BOOTSTRAP_SERVERS)

workers_count = 0


def json2Str(data):
    return json.dumps(data).encode('utf-8')


@app.route('/test_is_article', methods=['POST'])
def test_is_article():
    try:
        request_asset = request.get_json(force=True)
        url = request_asset['url'].strip()
        record_type = get_record_type(url)

    except Exception as err:
        print(traceback.format_exc())
        return json.dumps({'error_code': 1, 'error_message': err}), 500

    return json.dumps({'error_code': 0, 'error_message': '', 'data': record_type})


@app.route('/test_get_data', methods=['POST'])
def test_get_data():
    try:
        request_asset = request.get_json(force=True)
        url = request_asset['url'].strip()
        url_type = int(request_asset['url_type'])

        # extract_data_job(url_type, url, {}, '123')

        if url_type in (constant.RECORD_UNKNOW, constant.RECORD_AMBIGUOUS):
            record_type = get_record_type(url)
        else:
            record_type = url_type

        if record_type == constant.RECORD_ARTICLE:
            browser_service = BrowserFactory().get_browser_service(mbm_endpoint)
            page_asset = browser_service.get_full_asset(url)
            page_content = page_asset['content']
            page_container_info = page_asset['container_asset']
            current_record = get_article_data(
                url, page_content, page_container_info, "test")

        elif record_type == constant.RECORD_CATEGORY:
            response = requests.get(url)
            page_content = response.content
            current_record = get_navigation_data(url, page_content, "Test")

        else:
            current_record = {
                'url': url,
                'url_type': -2
            }

    except Exception as err:
        print(traceback.format_exc())
        return json.dumps({'error_code': 1, 'error_message': str(err)}), 500

    return json.dumps({'error_code': 0, 'error_message': '', 'data': current_record})


def get_record_type(url):
    browser_service = BrowserFactory().get_browser_service(mbm_endpoint)
    page_asset = browser_service.get_full_asset(url)
    trainer = Trainer(url, mbm_endpoint)
    record_type = trainer.get_record_type(url, page_asset)
    return record_type


def get_article_data(url, page_content, page_container_info, tracking_id):
    extract_data = ExtractData(url, mbm_endpoint)
    title, description, main_content, raw_main_content, comment, published_at = extract_data.extract_data(
        url, page_content, page_container_info)

    fb_graph_url = u'http://graph.facebook.com/?fields=og_object{likes.summary(true).limit(0)},share&id=' + url
    graph_info = requests.get(fb_graph_url)
    graph_content = graph_info.content
    graph_json = json.loads(graph_content)

    share_count = 0
    comment_count = 0
    like_count = 0
    if graph_json.get('share', None) is not None:
        share_count = graph_json.get('share').get('share_count')
        comment_count = graph_json.get(
            'share').get('comment_count')

    if graph_json.get('og_object') is not None:
        like_count = graph_json.get('og_object').get(
            'likes').get('summary').get('total_count')

    current_record = {
        'domain': url_helper.get_domain_from_url(url),
        'path': url_helper.get_path_from_url(url),
        'title': title,
        'description': description,
        'content': main_content,
        'raw_content': raw_main_content,
        'comments': '',
        'share_count': share_count,
        'comment_count': comment_count,
        'like_count': like_count,
        'published_at': published_at,
        'tracking_id': tracking_id
    }

    return current_record


def get_navigation_data(url, page_content, tracking_id, is_ignore_training_category=False):
    related_links = []
    soup = BeautifulSoup(page_content, 'html.parser')
    for a_tag in soup.find_all('a', href=True):
        if url_helper.is_same_domain(url_helper.get_domain_from_url(url), a_tag['href']):
            if a_tag['href'][0] == '/':
                fulfill_link = url_helper. \
                    fulfill_domain_path(
                        url_helper.get_domain_from_url(url), a_tag['href'])
                related_links.append(
                    url_helper.clear_hash_tag(fulfill_link))

            else:
                related_links.append(
                    url_helper.clear_hash_tag(a_tag['href']))

    if is_ignore_training_category:
        pattern = None
    else:
        training_category_pattern_handler = TrainingCategoryPagination(url)
        pattern = training_category_pattern_handler.training_category_pagination()
        if pattern is None:
            logger_service.warn(
                'Could not find the pattern of url: {}'.format(url))

    data = {
        'tracking_id': tracking_id,
        'link_root': url,
        'links': list(set(related_links)),
        'category_pattern': pattern
    }
    return data


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(5500), threaded=True)

    logger_service.debug('Goodbye, see you later')
