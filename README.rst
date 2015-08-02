========================================
http.upload
========================================

A multithread SimpleHTTPServer with ability to handle POST request for upload files.
It support both Python 2 & 3.
(There are some useful code from `CPython's http.server <https://github.com/python/cpython/blob/master/Lib/http/server.py>`_ )


Usage
========================================

Just like Python's http.server (or SimpleHTTPServer in Python 2) ::

    usage: upload.py [-h] [--bind ADDRESS] [port]

    positional arguments:
    port                  Specify alternate port [default: 8000]

    optional arguments:
    -h, --help            show this help message and exit
    --bind ADDRESS, -b ADDRESS
                            Specify alternate bind address [default: all interfaces]

HTML sample :

.. code-block:: html

    <form method="POST" action="." enctype="multipart/form-data">
    File to upload: <input type="file" name="upload">
    <input type="submit" value="upload">
    </form>


Example :

.. code-block:: sh

    $ python upload.py 5566
    Serving HTTP on 0.0.0.0 port 5566 ...

    $ ./upload.py 5566
    Serving HTTP on 0.0.0.0 port 5566 ...


Todo
========================================

* SSL support (it seems easy)
* option for just upload, no list_directory or other files' GET support
* default upload HTML (let user just need a Python script, no need for another HTML file)
* better HTML for user
