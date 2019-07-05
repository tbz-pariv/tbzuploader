.. image:: https://travis-ci.org/tbz-pariv/tbzuploader.svg?branch=master
    :target: https://travis-ci.org/tbz-pariv/tbzuploader


tbzuploader
===========

Generic http upload tool.

If the http upload was successfull, local files get moved to a "done" sub directory.

The upload is considered successfull by tbzuploader if the servers replies with http status `201 Created <https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#2xx_Success>`_

Additional features: Handles pairs of files.

For example you have four files: a.pdf, a.xml, b.pdf, b.xml

The first upload should take a.pdf and a.xml, and the second upload b.pdf and b.xml. See the docs for `--patterns`.

Example
=======

::

    user@host> tbzuploader my-local-dir https://user:password@myhost/upload-files

This will upload files from directory "my-local-dir" to the specified URL. If the upload was successful (server returned http status "201 created"),
then the local files in "my-local-dir" get moved to "my-local-dir/done".

Usage
=====

::

    usage: tbzuploader [-h] [--patterns= LIST_OF_PATTERNS]
                       [--min-age-seconds MIN_AGE_SECONDS]
                       [--done-directory DONE_DIRECTORY]
                       [--all-files-in-one-request] [--all-files-in-n-requests]
                       [--no-ssl-cert-verification] [--dry-run]
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
      --all-files-in-one-request
                            Upload all files in one request (if you give not
                            --pattern). Upload all matching files in one request
                            (if you give --pattern)
      --all-files-in-n-requests
                            Upload all files in N requests (if you give not
                            --pattern). Upload all matching files in N requests
                            (if you give --pattern)
      --no-ssl-cert-verification
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

It would very cool if tbzuploader could support it: https://tus.io/

Pull requests are welcome.


About
=====

Developed for our products `modwork <http://www.tbz-pariv.de/produkte/modwork>`_ and `modarch <http://www.tbz-pariv.de/produkte/modarch>`_.


