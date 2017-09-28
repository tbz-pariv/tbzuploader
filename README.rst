tbzuploader
===========

Generic http upload tool.

If the http upload was successfull, files get moved to a "done" sub directory.

Handles pairs of files.

For example you have for files: a.pdf, a.xml, b.pdf, b.xml

The first upload should take a.pdf and a.xml, and the second upload b.pdf and b.xml.

The upload is considered successfull by tbzuploader if the servers replies with http status `201 Created <https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#2xx_Success>`_

Usage
=====

Usage::

    usage: tbzuploader [-h] [--patterns= LIST_OF_PATTERNS]
                       [--min-age-seconds MIN_AGE_SECONDS]
                       [--done-directory DONE_DIRECTORY]
                       [--no-ssl-cert-verification]
                       local_directory url

    positional arguments:
      local_directory
      url

    optional arguments:
      -h, --help            show this help message and exit
      --patterns= LIST_OF_PATTERNS
                            List of file endings which should get uploaded
                            together. --patterns="*.pdf *.xml" foo.pdf and foo.xml
                            get uploaded together
      --min-age-seconds MIN_AGE_SECONDS
                            Skip files which are too young. Default: 60
      --done-directory DONE_DIRECTORY
                            files get moved to this directory after successful
                            upload. Defaults to {local_directory}/done
      --no-ssl-cert-verification

About
=====

Developed for you products `modwork <http://www.tbz-pariv.de/produkte/modwork>`_ and `modarch <http://www.tbz-pariv.de/produkte/modarch>`_.

