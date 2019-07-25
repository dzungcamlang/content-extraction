import requests
import time
import json
import numpy as np
import matplotlib.pyplot as plt
import math

from sympy import Point, Line
from bs4 import BeautifulSoup, Tag, Comment
from typing import List
from sklearn.cluster import k_means
from sklearn.feature_extraction.text import CountVectorizer
from scipy.spatial.distance import cosine

from internal.helper.soup_helper import SoupHelper
from internal.helper.string_helper import StringHelper



def get_text_paths(soup: BeautifulSoup):
    l_current_path = []
    d_text_paths = {}
    d_text_path_container_id = {}
    get_text_paths_recursive(soup, l_current_path, d_text_paths)
    return d_text_paths, d_text_path_container_id


def get_soup_by_path(self, soup=BeautifulSoup('', 'html.parser'), path=''):
    nodes = path.split(' ')
    sub_soup = soup
    while len(nodes) > 0:
        node_info = nodes[0].split('_')
        count = 1
        for element in sub_soup.childGenerator():
            if count == int(node_info[1]):
                sub_soup = element
                break
            count += 1
        nodes = nodes[1:]

    return sub_soup


def get_text_paths_recursive(soup: BeautifulSoup, l_current_path: List[str], d_text_paths: dict):
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

        if is_parent_text_node(l_current_tracking_text_pattern) or text_node_length > 300:
            l_current_path.append('text_node')
            text_path_key = ' '.join(l_current_path)
            get_text_paths_recursive(soup, l_current_path, d_text_paths)
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

                l_current_path.append(current_tag)
                get_text_paths_recursive(child, l_current_path, d_text_paths)
                l_current_path.pop()

def is_parent_text_node(l_tag: List[Tag]):
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


def get_tag_score_map(soup: BeautifulSoup) -> dict:
    l_tag = list(set([tag.name for tag in soup.find_all()]))
    d_score = {}
    for index, tag in enumerate(l_tag):
        d_score[tag] = index + 1
    return d_score

def get_main_content(content):
    string_helper = StringHelper()
    time_start = time.time()
    content = string_helper.replace_unclose_br_tag(content)
    content = string_helper.replace_unclose_img_tag(content)
    content = string_helper.replace_unclose_input_tag(content)
    soup = BeautifulSoup(content, 'html.parser')
    soup_backup = BeautifulSoup(content, 'html.parser')

    soup_helper = SoupHelper()

    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('iframe')]
    [s.extract() for s in soup('a')]
    [s.extract() for s in soup('header')]
    [s.extract() for s in soup('label')]
    [s.extract() for s in soup('option')]
    [s.extract() for s in soup('head')]
    [s.extract() for s in soup('footer')]
    [s.extract() for s in soup('style')]
    [s.extract() for s in soup('noscript')]
    [s.extract() for s in soup('video')]
    [s.extract() for s in soup('videolist')]
    [s.extract() for s in soup('source')]
    [s.extract() for s in soup('track')]

    comments = soup.findAll(text=lambda text:isinstance(text, Comment))
    [comment.extract() for comment in comments]

    l_content_length = []
    l_content = []
    l_path = []
    d_text_path = get_text_paths(soup)[0]

    def get_node_position(node: str):
        return int(node.split('_')[-1])

    def get_path_score(path: str) -> int:
        score = 0
        l_node = path.split(' ')
        l_node.reverse()
        
        for index, node in enumerate(l_node):
            pos = get_node_position(node)
            score += ((3 ** index) * pos)

        return score

    for text_path in d_text_path:
        if text_path.strip() == 'text_node':
            continue

        if len(d_text_path[text_path].strip()) < 50:
            continue

        path = soup_helper.convert_text_path_to_path(text_path)
        l_path.append(path)
        l_content_length.append(len(d_text_path[text_path]))
        l_content.append(d_text_path[text_path])
    
    # for content in l_content:
    #     print(content)
    #     print("=========")

    X = []
    plot_x = []
    plot_y = []
    for index, element in enumerate(l_content_length):
        X.append([get_path_score(l_path[index]), element])
        plot_x.append(get_path_score(l_path[index]))
        plot_y.append(element)

    X = np.array(X)

    plot_score = []
    plot_num = []
    highest_score = 0
    total_case = len(X) if len(X) < 10 else 10
    for i in range(1, total_case, 1):
        current_kmeans = k_means(X, i)
        if i == 1:
            highest_score = current_kmeans[2]
            num_rate = highest_score / 10
        
        plot_score.append(round(current_kmeans[2], 2))
        plot_num.append(i * num_rate)


    p1 = Point(plot_num[0], plot_score[0], evaluate=False)
    p2 = Point(plot_num[-1], plot_score[-1], evaluate=False)
    line = Line(p1, p2, evaluate=False)
    highest_score = 0
    k = 1

    for i, _ in enumerate(plot_score):
        if i > 1:
            A = Point((plot_num[i-1], plot_score[i-1]), evaluate=False)
            B = (plot_num[i-2], plot_score[i-2])
            distance = float(line.distance(A))
            if highest_score < distance:
                highest_score = distance
                k = i

    kmeans = k_means(X, k)
    plot_cent_x = kmeans[0][:,0]
    plot_cent_y = kmeans[0][:,1]

    l_label = kmeans[1]
    d_label = {}

    for index, label in enumerate(l_label):
        if label not in d_label:
            d_label[label] = []
        d_label[label].append(l_content_length[index])

    candidate_label = 0
    highest_score = 0
    for label in d_label:
        # score = (sum(d_label[label]) / len(d_label[label])) * math.log(len(d_label[label]) + 1, 5) * math.log10(sum(d_label[label]))
        score = sum(d_label[label])
        if score > highest_score:
            highest_score = score
            candidate_label = label

    l_result = []
    l_result_path = []
    for index, label in enumerate(l_label):
        if label == candidate_label:
            l_result.append(l_content[index])
            l_result_path.append(l_path[index])
    
    def get_common_path(l_path):
        laboratory_path = l_path[0]

        while True:
            l_laboratory_node = laboratory_path.split(' ')
            l_laboratory_node = l_laboratory_node[:len(l_laboratory_node) - 1]
            laboratory_path = ' '.join(l_laboratory_node)

            flag = True
            for path in l_path:
                if laboratory_path not in path:
                    flag = False
                    break
            if flag == True:
                return laboratory_path

    # plt.scatter(plot_x, plot_y, s=3)
    # plt.scatter(plot_cent_x, plot_cent_y, color='red', s=4)
    # plt.show()
    return ' '.join(l_result)

# response = requests.get('http://kenh14.vn/hau-truong-chup-anh-cuoi-taeyang-min-hyo-rin-khoe-nguc-sieu-khung-vo-chong-dep-nhu-quay-mv-20180206123553601.chn')
# content = response.text
# print(str(get_main_content(content)))
# exit()


def cosine_similarity(s_1: str, s_2: str):
    tfidf = CountVectorizer(stop_words='english')
    X = tfidf.fit_transform([s_1, s_2])
    return cosine(X[0].toarray(), X[1].toarray())

def LCS(X, Y):
    m = len(X)
    n = len(Y)
    # An (m+1) times (n+1) matrix
    C = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if X[i-1] == Y[j-1]: 
                C[i][j] = C[i-1][j-1] + 1
            else:
                C[i][j] = max(C[i][j-1], C[i-1][j])
    return C

def backTrack(C, X, Y, i, j):
    if i == 0 or j == 0:
        return ""
    elif X[i-1] == Y[j-1]:
        return backTrack(C, X, Y, i-1, j-1) + X[i-1]
    else:
        if C[i][j-1] > C[i-1][j]:
            return backTrack(C, X, Y, i, j-1)
        else:
            return backTrack(C, X, Y, i-1, j)

def get_LCS(X, Y):
    m = len(X)
    n = len(Y)
    C = LCS(X, Y)
    return backTrack(C, X, Y, m, n)

import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('punkt') # if necessary...


stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]

l_result = []
l_old_result = []
l_execution_time = []
for i in range(0, 50, 1):
    if i == 10 or i == 13:
        continue

    # if i != 0:
    #     continue

    with open('{}/{}/{}.txt'.format('CEED', 'Content', i), 'r') as f_1:
        with open('{}/{}/{}.html'.format('CEED', 'HTML', i), 'r') as f_2:
            try:
                print(i, 'step')
                time_start = time.time()
                predict_content = get_main_content(f_2.read())
                # print("=================")
                # print("=================")
                # print(predict_content)
            except Exception as e:
                print(e)
                continue
            l_execution_time.append(time.time() - time_start)
            print("Time spent: {}".format(time.time() - time_start))

            gold_content = f_1.read()
            old_ce_content = ''
            # with open('{}/{}/{}.txt'.format('CEED', 'Article', i), 'r') as f_3:
            #     old_ce_content = f_3.read()

            new_ce_acc = cosine_sim(gold_content, predict_content)
            old_ce_acc = cosine_sim(gold_content, old_ce_content)
            # if cosine_sim(gold_content, predict_content) < 0.5:
            #     print("Weak", i)
            #     #print(predict_content)
            #     print(cosine_sim(gold_content, predict_content))
            print('New CE', new_ce_acc)
            print('Old CE', old_ce_acc)

            l_result.append(new_ce_acc)
            l_old_result.append(old_ce_acc)

print('New CE acc:', sum(l_result) / len(l_result))            
print('Old CE acc:', sum(l_old_result) / len(l_old_result))
print(sum(l_execution_time) / len(l_execution_time))
