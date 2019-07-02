# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from future import standard_library

standard_library.install_aliases()

if standard_library.PY2:
    from httplib import responses
    from urlparse import urlparse
elif standard_library.PY3:
    from http.client import responses
    from urllib.parse import urlparse
import collections
import datetime
import logging
import os
import re
import shutil
import time

from collections import defaultdict

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

import requests

logger = logging.getLogger(__name__)


def upload_list_of_pairs(directory, url, list_of_pairs, done_directory, verify=True):
    success = True
    for pairs in list_of_pairs:
        done_dir = upload_list_of_pairs__single(directory, url, pairs, done_directory, verify)
        if not done_dir:
            success = False
    return success


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
    logger.warn('Failed: {}'.format(pairs))
    logger.warn('{} {} {}'.format(
        response,
        responses.get(response.status_code),
        url,  # TODO remove password from URL. See https://stackoverflow.com/questions/46905367/remove-password-from-url
    ))
    logger.warn(response.content)
    return None


def is_absolute_url(url):
    return bool(urlparse(url).scheme)


def relative_url_to_absolute_url(request_url, response_location):
    if not response_location:
        return request_url
    if is_absolute_url(response_location):
        return response_location
    parsed_url = urlparse(request_url)
    return '{}://{}{}'.format(parsed_url.scheme, parsed_url.netloc.split('@')[-1], response_location)


def upload_list_of_pairs__single__success(directory, url, pairs, done_directory, response):
    logger.info('Success :-) %s' % (relative_url_to_absolute_url(url, response.headers.get('Location'))))
    if not os.path.exists(done_directory):
        os.mkdir(done_directory)
    single_done_dir = os.path.join(done_directory, datetime.datetime.now().strftime('%Y-%m-%d--%H-%M-%S--%f'))
    os.mkdir(single_done_dir)
    for file_name in pairs:
        shutil.move(os.path.join(directory, file_name), single_done_dir)
    logger.info('Moved files to: %s' % single_done_dir)
    with open(os.path.join(single_done_dir, 'success.txt'), 'wt') as fd:
        fd.write('%s\n' % url)
    return single_done_dir


def get_pairs_from_directory(directory, list_of_patterns, all_files_in_one_request=False, all_files_in_n_requests=False):
    assert not (all_files_in_one_request and all_files_in_n_requests)
    if not list_of_patterns:
        if all_files_in_one_request:
            return get_pairs_from_directory__all_files__one_request(directory)
        else:
            return get_pairs_from_directory__all_files__n_requests(directory)
    if all_files_in_one_request:
        return get_pairs_from_directory__all_files__one_request(directory, list_of_patterns)
    if all_files_in_n_requests:
        return get_pairs_from_directory__all_files__n_requests(directory, list_of_patterns)

    pairs = []
    for patterns in list_of_patterns:
        pairs.extend(get_pairs_from_directory_single_pattern(directory, patterns))
    check_duplicates(pairs)
    return pairs


def get_pairs_from_directory__all_files__n_requests(directory):
    files = []
    for file_name in sorted(os.listdir(directory)):
        file_abs = os.path.join(directory, file_name)
        if not os.path.isfile(file_abs):
            continue
        files.append((file_name,))
    return files


def join_list_of_patterns_to_one_pattern(list_of_patterns):
    all_patterns = []
    for patterns in list_of_patterns:
        all_patterns.extend(patterns.split())
    return [glob_pattern_to_regex_pattern(pattern) for pattern in all_patterns]


def get_pairs_from_directory__all_files__one_request(directory, list_of_patterns=[]):
    if list_of_patterns:
        regex_patterns = join_list_of_patterns_to_one_pattern(list_of_patterns)
    files = []
    for base_name in sorted(os.listdir(directory)):
        file_abs = os.path.join(directory, base_name)
        if not os.path.isfile(file_abs):
            continue
        if list_of_patterns and not star_part_or_none(base_name, regex_patterns):
            continue
        files.append(base_name)
    if not files:
        return []
    return [tuple(files)]


def get_pairs_from_directory__all_files__n_requests(directory, list_of_patterns=[]):
    if list_of_patterns:
        regex_patterns = join_list_of_patterns_to_one_pattern(list_of_patterns)
    files = []
    for base_name in sorted(os.listdir(directory)):
        file_abs = os.path.join(directory, base_name)
        if not os.path.isfile(file_abs):
            continue
        if list_of_patterns and not star_part_or_none(base_name, regex_patterns):
            continue
        files.append((base_name,))
    return files


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
        glob_sub_part_of_file_name = star_part_or_none(base_name, regex_patterns)
        if not glob_sub_part_of_file_name:
            continue
        matches[glob_sub_part_of_file_name].append(base_name)
    for glob_sub_part_of_file_name, base_names in sorted(matches.items()):
        if len(base_names) == len(regex_patterns):
            pairs.append(base_names)
    return pairs


def star_part_or_none(base_name, regex_patterns):
    for regex in regex_patterns:
        match = regex.match(base_name)
        if not match:
            continue
        return match.group(1)


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
