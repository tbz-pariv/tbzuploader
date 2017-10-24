# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from future import standard_library
standard_library.install_aliases()
import collections
import datetime
import logging
import os
import re
import shutil
import time
import urllib.parse
from collections import defaultdict

import requests


def upload_list_of_pairs(directory, url, list_of_pairs, done_directory, verify=True):
    for pairs in list_of_pairs:
        upload_list_of_pairs__single(directory, url, pairs, done_directory, verify)


def upload_list_of_pairs__single(directory, url, pairs, done_directory, verify):
    open_file_list = []
    for file_name in pairs:
        open_file_list.append(('files', open(os.path.join(directory, file_name), 'rb')))
    try:
        response = requests.post(url, files=open_file_list, allow_redirects=False,
                             verify=verify)
    except requests.exceptions.SSLError as exc:
        raise ValueError('%s. Use --no-ssl-cert-verification if you want ....' % exc)
    finally:
        for name, open_file in open_file_list:
            open_file.close()
    if response.status_code == 201:
        return upload_list_of_pairs__single__success(directory, url, pairs, done_directory, response)
    print('Failed: %s' % pairs)
    print('%s %s' % (response, url)) # TODO remove password from URL. See https://stackoverflow.com/questions/46905367/remove-password-from-url
    print(response.content)


def upload_list_of_pairs__single__success(directory, url, pairs, done_directory, response):
    parsed_url = urllib.parse.urlparse(url)
    url = '{}://{}/{}'.format(parsed_url.scheme, parsed_url.netloc.split('@')[1], response.headers['Location'])
    print('Success :-) %s' % (url))
    if not os.path.exists(done_directory):
        os.mkdir(done_directory)
    single_done_dir = os.path.join(done_directory, datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S--%f'))
    os.mkdir(single_done_dir)
    for file_name in pairs:
        shutil.move(os.path.join(directory, file_name), single_done_dir)
    print('Moved files to: %s' % single_done_dir)
    with open(os.path.join(single_done_dir, 'success.txt'), 'wt') as fd:
        fd.write('%s\n' % url)


def get_pairs_from_directory(directory, list_of_patterns):
    if not list_of_patterns:
        return get_pairs_from_directory__all_files__no_pairs(directory)
    pairs = []
    for patterns in list_of_patterns:
        pairs.extend(get_pairs_from_directory_single_pattern(directory, patterns))
    check_duplicates(pairs)
    return pairs

def get_pairs_from_directory__all_files__no_pairs(directory):
    files=[]
    for file_name in sorted(os.listdir(directory)):
        file_abs = os.path.join(directory, file_name)
        if not os.path.isfile(file_abs):
            continue
        files.append(file_name)
    return [(item,) for item in files]

def check_duplicates(pairs):
    single_list = []
    for file_names in pairs:
        single_list.extend(file_names)
    duplicates = [item for item, count in list(collections.Counter(single_list).items()) if count > 1]
    if duplicates:
        raise ValueError('There are duplicates. Upload refused: %s' % duplicates)


def get_pairs_from_directory_single_pattern(directory, patterns):
    """

    Args:
        directory:
        patterns: "*.pdf *.xml"

    Returns:
       [('a.pdf', 'a.xml'), ('b.pdf', 'b.xml')
    """
    regex_patterns = [glob_pattern_to_regex_pattern(pattern) for pattern in patterns.split()]
    matches = defaultdict(list)
    list_of_files = list_directory(directory)
    pairs = []
    for base_name in list_of_files:
        for regex in regex_patterns:
            match = regex.match(base_name)
            if match:
                glob_sub_part_of_file_name = match.group(1)
                matches[glob_sub_part_of_file_name].append(base_name)
    for glob_sub_part_of_file_name, base_names in sorted(matches.items()):
        if len(base_names) == len(regex_patterns):
            pairs.append(base_names)
    return pairs


def filter_files_which_are_too_young(directory, list_of_pairs, min_age_seconds):
    good_pairs = []
    for pairs in list_of_pairs:
        skip = False
        for file_name in pairs:
            age = get_file_age(os.path.join(directory, file_name))
            if age < min_age_seconds:
                logging.info('File too young: %s (Need to wait %ss)' % (file_name, int(min_age_seconds - age)))
                skip = True
                break
        if skip:
            continue
        good_pairs.append(pairs)
    return good_pairs


def list_directory(directory):
    return list(sorted(os.listdir(directory)))


def get_file_age(file_name):
    mtime = os.path.getctime(file_name)
    return abs(time.time() - mtime)


def glob_pattern_to_regex_pattern(glob_pattern):
    if not '*' in glob_pattern:
        raise ValueError('No * found in %r' % glob_pattern)
    magic = 'yxyxyxyxymagicyxyxyxyxy'
    return re.compile('^%s$' % re.escape(glob_pattern.replace('*', magic)).replace(magic, '(.+)'), re.IGNORECASE)
