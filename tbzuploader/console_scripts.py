# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import logging
import os

from tbzuploader import utils

default_min_age_seconds=60

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('local_directory')
    parser.add_argument('url')
    parser.add_argument('--patterns=',
                        help='List of file endings which should get uploaded together. --patterns="*.pdf *.xml" foo.pdf and foo.xml get uploaded together',
                        dest='list_of_patterns', action='append')
    parser.add_argument('--min-age-seconds', help='Skip files which are too young. Default: %s' % default_min_age_seconds,
                        default=default_min_age_seconds, type=int)
    parser.add_argument('--done-directory files get moved to this directory after successful upload. Defaults to {local_directory}/done',
                        dest='done_directory')
    args = parser.parse_args()
    if not args.list_of_patterns:
        raise ValueError('At least one --patterns=... is needed')
    done_directory=args.done_directory
    if not done_directory:
        done_directory=os.path.join(args.local_directory, 'done')
    if not os.path.exists(done_directory):
        os.mkdir(done_directory)
    list_of_pairs = utils.get_pairs_from_directory(args.local_directory, args.list_of_patterns)
    list_of_pairs = utils.filter_files_which_are_too_young(args.local_directory, list_of_pairs, args.min_age_seconds)
    if not list_of_pairs:
        logging.info('No pairs to upload found.')
        return
    utils.upload_list_of_pairs(args.local_directory, args.url, list_of_pairs, done_directory)


