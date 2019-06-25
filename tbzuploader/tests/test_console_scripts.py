# -*- coding: utf-8 -*-
import unittest

import sys

import mock

from tbzuploader import console_scripts


class TestCase(unittest.TestCase):
    def test_ca_bundle(self):
        sys.argv = ['tbzuploader', '--ca-bundle', 'test.crt', '--no-ssl-cert-verification', './', 'http://www.example.com']
        self.assertRaises(ValueError, console_scripts.main)

        with mock.patch('tbzuploader.utils.upload_list_of_pairs') as upload_mock:
            with mock.patch('tbzuploader.utils.get_pairs_from_directory', return_value=[['test.txt']]):
                with mock.patch('tbzuploader.utils.get_file_age', return_value=60):
                    sys.argv = ['tbzuploader', '--ca-bundle', 'test.crt', './', 'http://www.example.com']
                    console_scripts.main()
                    args, kwargs = upload_mock.call_args
                    self.assertIn('verify', kwargs, msg=kwargs)
                    self.assertEqual('test.crt', kwargs['verify'])