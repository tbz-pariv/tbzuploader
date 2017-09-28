tbzuploader
===========

Generic http upload tool.

If the http upload was successfull, files get moved to a "done" sub directory.

Handles pairs of files.

For example you have for files: a.pdf, a.xml, b.pdf, b.xml

The first upload should take a.pdf and a.xml, and the second upload b.pdf and b.xml.

The upload is considered successfull by tbzuploader if the servers replies with http status `201 Created <https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#2xx_Success>`_


About
=====

Developed for you products `modwork <http://www.tbz-pariv.de/produkte/modwork>`_ and `modarch <http://www.tbz-pariv.de/produkte/modarch>`_.

