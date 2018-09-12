# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import glob
import io
import tempfile
import unittest

import mock
import os
from tbzuploader import utils
from tbzuploader.utils import relative_url_to_absolute_url, upload_list_of_pairs__single__success


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
        directory = tempfile.mkdtemp(prefix='test_upload_list_of_pairs__single_')
        file_a = os.path.join(directory, 'foo.a')
        with io.open(file_a, 'wt') as fd:
            fd.write('a')
        file_b = os.path.join(directory, 'foo.b')
        with io.open(file_b, 'wt') as fd:
            fd.write('b')
        done_dir = os.path.join(directory, 'done')
        with mock.patch('requests.post', my_post):
            single_done_dir = utils.upload_list_of_pairs__single(directory, 'https://example.com', (file_a, file_b), done_dir, verify=False)
        self.assertFalse(set(os.listdir(directory)) - set(['done']))
        self.assertTrue(os.path.exists(os.path.join(single_done_dir, 'foo.a')), done_dir)
        self.assertTrue(os.path.exists(os.path.join(single_done_dir, 'foo.b')), done_dir)
