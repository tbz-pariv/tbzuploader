# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import glob
import io
import tempfile
import unittest

import mock
import os
from tbzuploader import utils
from tbzuploader.utils import relative_url_to_absolute_url, upload_list_of_pairs__single__success, \
    get_pairs_from_directory__all_files__n_requests, get_pairs_from_directory__all_files__one_request, \
    get_pairs_from_directory


class DummyResponse(object):
    headers=dict()
    status_code=201

class TestCase(unittest.TestCase):
    is_source_from_tbz = True

    def test_get_pairs_from_directory(self):
        with mock.patch('tbzuploader.utils.list_directory',
                        return_value=['ax.pdf', 'ax.xml', 'bx.pdf', 'bx.xml', 'cx.pdf', 'cx.xml']):
            self.assertEqual([['ax.pdf', 'ax.xml'], ['bx.pdf', 'bx.xml']],
                             utils.get_pairs_from_directory('.', ['a*.pdf a*.xml', 'b*.pdf b*.xml']))

    def create_dummy_directory(self):
        directory = tempfile.mkdtemp(prefix='test_upload_list_of_pairs__single_')
        for dummy_file in ['foo.a', 'foo.b', 'bar.a', 'bar.b']:
            with io.open(os.path.join(directory, dummy_file), 'wt') as fd:
                fd.write('x\n')
        return directory

    def test_glob_pattern_to_regex_pattern(self):
        regex = utils.glob_pattern_to_regex_pattern('A*.PDF')
        match = regex.match('abc.pdf')
        self.assertEqual('bc', match.group(1))

    def test_get_pairs_from_directory_single_pattern__simple(self):
        with mock.patch('tbzuploader.utils.list_directory', return_value=['ax.pdf', 'ax.xml']):
            self.assertEqual([['ax.pdf', 'ax.xml']], utils.get_pairs_from_directory_single_pattern('.', '*.pdf *.xml'))

    def test_get_pairs_from_directory_single_pattern__case_insensitive(self):
        with mock.patch('tbzuploader.utils.list_directory', return_value=['ax.PDF', 'ax.xml']):
            self.assertEqual([['ax.PDF', 'ax.xml']], utils.get_pairs_from_directory_single_pattern('.', '*.pdf *.XML'))

    def test_get_pairs_from_directory_single_pattern__between_other_files(self):
        with mock.patch('tbzuploader.utils.list_directory',
                        return_value=['a.pdf', 'b.xml', 'foo.x', 'foo.y', 'ax.pdf', 'ax.xml']):
            self.assertEqual([['ax.pdf', 'ax.xml']], utils.get_pairs_from_directory_single_pattern('.', '*.pdf *.xml'))

    def test_duplicates(self):
        self.assertIsNone(utils.check_duplicates([['a.pdf', 'a.xml'], ['b.pdf', 'b.xml']]))
        self.assertRaises(ValueError, utils.check_duplicates, [['a.pdf', 'a.xml'], ['b.pdf', 'b.xml'], ['b.pdf']])

    def test_filter_files_which_are_too_young__do_filter(self):
        with mock.patch('tbzuploader.utils.get_file_age',
                        return_value=10):
            self.assertEqual([], utils.filter_files_which_are_too_young('.', [['a.xml', 'a.pdf']], min_age_seconds=60))


    def test_filter_files_which_are_too_young__do_not_filter(self):
        with mock.patch('tbzuploader.utils.get_file_age',
                        return_value=100):
            self.assertEqual([['a.xml', 'a.pdf']], utils.filter_files_which_are_too_young('.', [['a.xml', 'a.pdf']], min_age_seconds=60))

    def test_relative_url_to_absolute_url__is_already_with_scheme(self):
        self.assertEqual('https://example.com/abc', relative_url_to_absolute_url('http://google.com/xyz', 'https://example.com/abc'))

    def test_relative_url_to_absolute_url__without_scheme(self):
        self.assertEqual('http://google.com/abc', relative_url_to_absolute_url('http://google.com/xyz', '/abc'))

    def test_relative_url_to_absolute_url__without_scheme_with_user_and_password(self):
        self.assertEqual('http://google.com/abc', relative_url_to_absolute_url('http://user:pwd@google.com/xyz', '/abc'))

    def test_relative_url_to_absolute_url__without_scheme_with_file_url(self):
        self.assertEqual('file:///abc', relative_url_to_absolute_url('http://user:pwd@google.com/xyz', 'file:///abc'))


    def test_upload_list_of_pairs__single__success(self):
        directory = tempfile.mkdtemp()
        with open(os.path.join(directory, 'foo.txt'), 'wt') as fd:
            fd.write(':-)\n')
        done_directory = tempfile.mkdtemp()
        url='https://user:password@example.com/path'
        response=DummyResponse()
        pairs=['foo.txt']
        upload_list_of_pairs__single__success(directory, url, pairs, done_directory, response)
        self.assertEqual(['foo.txt'], [os.path.basename(file_name) for file_name in glob.glob(os.path.join(done_directory, '*', 'foo.txt'))])

    def test_upload_list_of_pairs__single(self):
        def my_post(url, files, allow_redirects, verify):
            return DummyResponse()
        directory = self.create_dummy_directory()
        done_dir = os.path.join(directory, 'done')
        with mock.patch('requests.post', my_post):
            single_done_dir = utils.upload_list_of_pairs__single(directory, 'https://example.com',
                                                                 (os.path.join(directory, 'foo.a'), os.path.join(directory, 'bar.a')),
                                                                 done_dir, verify=False)
        self.assertEqual(['bar.b', 'done', 'foo.b'], [os.path.basename(f) for f in sorted(os.listdir(directory))])
        self.assertTrue(os.path.exists(os.path.join(single_done_dir, 'foo.a')), done_dir)
        self.assertTrue(os.path.exists(os.path.join(single_done_dir, 'bar.a')), done_dir)


    def test_get_pairs_from_directory__all_files__n_requests(self):
        directory = self.create_dummy_directory()
        self.assertEqual([(u'bar.a',), (u'bar.b',), (u'foo.a',), (u'foo.b',)], get_pairs_from_directory__all_files__n_requests(directory))

    def test_get_pairs_from_directory__all_files__one_request(self):
        directory = self.create_dummy_directory()
        self.assertEqual([(u'bar.a', u'bar.b', u'foo.a', u'foo.b')], get_pairs_from_directory__all_files__one_request(directory))

    def test_get_pairs_from_directory__one_request__no_pattern(self):
            self.assertEqual([('bar.a', 'bar.b', 'foo.a', 'foo.b')],
                         get_pairs_from_directory(self.create_dummy_directory(), [], all_files_in_one_request=True))

    def test_get_pairs_from_directory__not_one_request__no_pattern(self):
        self.assertEqual([('bar.a',), ('bar.b',), ('foo.a',), ('foo.b',)], get_pairs_from_directory(
            self.create_dummy_directory(), [], all_files_in_n_requests=True))

    def test_get_pairs_from_directory__one_request__with_pattern(self):
        self.assertEqual([('bar.a', 'foo.a')],
                         get_pairs_from_directory(self.create_dummy_directory(), ['*.a'],
                                                  all_files_in_one_request=True))

    def test_get_pairs_from_directory__n_requests__with_pattern(self):
        self.assertEqual([('bar.b',), ('foo.b',)], get_pairs_from_directory(
            self.create_dummy_directory(), ['*.b'], all_files_in_n_requests=True))

    def test_get_pairs_from_directory__no_match(self):
        self.assertEqual([], get_pairs_from_directory(
            self.create_dummy_directory(), ['*.xyz'], all_files_in_one_request=True))
