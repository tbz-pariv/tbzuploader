# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import logging
import os

import sys
from tbzuploader import utils

default_min_age_seconds = 60


def set_up_logging(level=logging.INFO):
    global logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s %(name)s: %(levelname)-8s [%(process)d] %(message)s', '%Y-%m-%d %H:%M:%S'))
    root_logger.addHandler(handler)
    logger = logging.getLogger(os.path.basename(sys.argv[0]))


def main():
    set_up_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('local_directory')
    parser.add_argument('url', help='URL can contain http-basic-auth like this: https://apiuser:mypwd@example.com/input-process-output/')
    parser.add_argument('--patterns=',
                        help='List of file endings which should get uploaded together. Example: --patterns="*.pdf *.xml" The pairs (a.pdf, a.xml) and (b.pdf, b.xml) get uploaded together',
                        dest='list_of_patterns', action='append')
    parser.add_argument('--min-age-seconds', help='Skip files which are too young. Default: %s' % default_min_age_seconds,
                        default=default_min_age_seconds, type=int)
    parser.add_argument('--done-directory', help='files get moved to this directory after successful upload. Defaults to {local_directory}/done',
                        dest='done_directory')

    parser.add_argument('--all-files-in-one-request',
                        help='Upload all files in one request (if you give not --pattern). Upload all matching files in one request (if you give --pattern)',
                        action='store_true')
    parser.add_argument('--all-files-in-n-requests',
                        help='Upload all files in N requests (if you give not --pattern). Upload all matching files in N requests (if you give --pattern)',
                        action='store_true')
    parser.add_argument('--no-ssl-cert-verification', action='store_true')
    parser.add_argument('--ca-bundle')
    parser.add_argument('--dry-run', help='Do not upload. Just print the pair of files which would get uploaded together',
                        action='store_true')
    args = parser.parse_args()
    done_directory = args.done_directory
    if not done_directory:
        done_directory = os.path.join(args.local_directory, 'done')
    if not os.path.exists(done_directory):
        os.mkdir(done_directory)
    if args.all_files_in_one_request and args.all_files_in_n_requests:
        raise ValueError('--all-files-in-one-request and --all-files-in-n-requests are mutual exclusive')
    if args.ca_bundle and args.no_ssl_cert_verification:
        raise ValueError('''You can't use --ca-bundle and --no-ssl-cert-verification together.''')
    list_of_pairs = utils.get_pairs_from_directory(args.local_directory, args.list_of_patterns,
                                                   all_files_in_one_request=args.all_files_in_one_request,
                                                   all_files_in_n_requests=args.all_files_in_n_requests)
    list_of_pairs = utils.filter_files_which_are_too_young(args.local_directory, list_of_pairs, args.min_age_seconds)
    if not list_of_pairs:
        logging.info('No pairs to upload found.')
        return
    if args.dry_run:
        for pairs in list_of_pairs:
            print('I would upload this in one request: {}'.format(' '.join(pairs)))
        return
    success = utils.upload_list_of_pairs(
        args.local_directory,
        args.url,
        list_of_pairs,
        done_directory,
        verify=args.ca_bundle if args.ca_bundle else not args.no_ssl_cert_verification
    )
    if not success:
        sys.exit(1)
