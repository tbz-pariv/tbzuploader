.. image:: https://travis-ci.org/tbz-pariv/tbzuploader.svg?branch=master
    :target: https://travis-ci.org/tbz-pariv/tbzuploader


tbzuploader - Generic HTTP Uploading
====================================

A lot of daily work is based on regular files.

tbzuploader is a command line tool which detects uploadable files and posts them via HTTP while conforming to the
standardized `HTTP Status Codes <https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#2xx_Success>`_.


Upload Protocol
===============

tbzuploader conforms to the generally accepted upload protocol.


201 Created
***********

If the HTTP upload is successful, the server responds with "201 Created".
The files will then be moved to a "done" directory.

400 Bad Request
***************

If the HTTP upload is not successful and it is a client error (such as wrong files or corrupted files),
the server responds with "400 Bad Request".
The files will then be moved to a "failed" directory.

In case you want to inform an admin, specify an email address which gets notified in that case, because
failed files won't be retried.


500 Internal Server Error and others
************************************

If the HTTP upload was not successful (such as an login page, outage, programming error or overload),
the server responds with other status codes (such as 500 Internal Server Error).
tbzuploader will then retry to post the files next time.


Features
========

- pairs of arbitrary size (tuples, triplets, etc.)

  - For example you have four files: a.pdf, a.xml, b.pdf, b.xml
  - The first upload should take a.pdf and a.xml, and the second upload b.pdf and b.xml.
  - See the docs for `--patterns`.

- mail to admin if broken files are uploaded


Example
=======

::

    user@host> tbzuploader my-local-dir https://user:password@myhost/upload-files

This will upload files from directory "my-local-dir" to the specified URL.

If the upload was **successful** (server returned http status "201 Created"),
then the local files in "my-local-dir" get moved to "my-local-dir/done".

If the upload **failed** because the server rejects the files (400 Bad Request),
then the local files in "my-local-dir" get moved to "my-local-dir/failed".

If there was another error (network timeout, server overload, ...), the files stay in the current location and the next call of the command line tool will try to upload the files again.

Usage
=====

::

    >>> bin/tbzuploader --help
    usage: tbzuploader [-h] [--patterns= LIST_OF_PATTERNS]
                       [--min-age-seconds MIN_AGE_SECONDS]
                       [--done-directory DONE_DIRECTORY]
                       [--failed-directory FAILED_DIRECTORY]
                       [--smtp-server SMTP_SERVER] [--mail-from MAIL_FROM]
                       [--mail-to MAIL_TO] [--all-files-in-one-request]
                       [--all-files-in-n-requests] [--no-ssl-cert-verification]
                       [--ca-bundle CA_BUNDLE] [--dry-run]
                       local_directory url

    positional arguments:
      local_directory
      url                   URL can contain http-basic-auth like this:
                            https://apiuser:mypwd@example.com/input-process-
                            output/

    optional arguments:
      -h, --help            show this help message and exit
      --patterns= LIST_OF_PATTERNS
                            List of file endings which should get uploaded
                            together. Example: --patterns="*.pdf *.xml" The pairs
                            (a.pdf, a.xml) and (b.pdf, b.xml) get uploaded
                            together
      --min-age-seconds MIN_AGE_SECONDS
                            Skip files which are too young. Default: 60
      --done-directory DONE_DIRECTORY
                            files get moved to this directory after successful
                            upload. Defaults to {local_directory}/done
      --failed-directory FAILED_DIRECTORY
                            files get moved to this directory after failed upload
                            due to broken files. Defaults to
                            {local_directory}/failed
      --smtp-server SMTP_SERVER
                            SMTP server which sends mails in case broken files
                            were tried to be uploaded.
      --mail-from MAIL_FROM
                            Sender of mails in case broken files were tried to be
                            uploaded.
      --mail-to MAIL_TO     Recipient of mails in case broken files were tried to
                            be uploaded.
      --all-files-in-one-request
                            Upload all files in one request (if you give not
                            --pattern). Upload all matching files in one request
                            (if you give --pattern)
      --all-files-in-n-requests
                            Upload all files in N requests (if you give not
                            --pattern). Upload all matching files in N requests
                            (if you give --pattern)
      --no-ssl-cert-verification
      --ca-bundle CA_BUNDLE
      --dry-run             Do not upload. Just print the pair of files which
                            would get uploaded together

Install
=======

Install for usage from `pypi <https://pypi.python.org/pypi/tbzuploader/>`_::

    pip install tbzuploader


Development Install on Python2
==============================

Install tbzuploader for development on Python2::

    virtualenv tbzuploader-env
    cd tbzuploader-env
    . ./bin/activate
    pip install -e git+https://github.com/guettli/tbzuploader.git#egg=tbzuploader

Development Install on Python3
==============================

Install tbzuploader for development on Python3::

    python3 -m venv tbzuploader-py3env
    cd tbzuploader-py3env
    . ./bin/activate
    pip install --upgrade pip
    pip install -e git+https://github.com/guettli/tbzuploader.git#egg=tbzuploader

Development Testing
===================

Testing::

    pip install -r src/tbzuploader/requirements.txt
    cd src/tbzuploader
    pytest # all test ok?
    pyCharm src/tbzuploader/...
    pytest # all test still ok?
    .... I am waiting for your pull request :-)

Protocol for resumable uploads 
==============================

Unfortunately, tbzuploader does not support resumable uploads up to now.

There is already a spec for it. 

It would very cool if tbzuploader could support this spec: https://tus.io/

Pull requests are welcome.


Trivia: Why 201?
================

Why does the http status 201 gets used, and not 200? In the beginning we used "200" for "successful upload". But somewhere was a bug on the server and the server took the upload request, ignored the files and showed the login-page and replied with http status "200". Hence the files got trashed, since the client thought the upload was successful. But of course the files were not lost. They were still in the done-directory.

That's why 201 gets used.

