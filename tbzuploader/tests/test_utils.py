# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import mock
from tbzuploader import utils


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
