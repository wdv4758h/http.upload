#!/usr/bin/env python

# SimpleHTTPServer with upload and multithread support
#
# License: GPLv3, see LICENSE for more details.

from io import BytesIO
import os.path
import re
import sys

py = sys.version_info
py3k = py >= (3, 0, 0)

# if you want truly concurrent, use ForkingMixIn instead of ThreadingMixIn in CPython (it has GIL)

if py3k:
    from socketserver import ThreadingMixIn
    from http.server import SimpleHTTPRequestHandler, BaseHTTPRequestHandler, HTTPServer
else:
    from SocketServer import ThreadingMixIn
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer



class SimplePostRequestHandler(BaseHTTPRequestHandler):
    """
    implement "do_POST"
    """

    def do_POST(self):
        """Serve a POST request."""

        info = self.handle_post_data()

        # this can change to read a HTML file, if someone wants it
        template = """<!DOCTYPE html>
                      <html>
                          <title>Upload Result</title>
                          <body>
                              <h1>Upload Result</h1>
                              <hr/>
                                  <b>{info}</b>
                                  <a href="{return_link}">back</a>
                              <hr/>
                          </body>
                      </html>"""

        result = template.format(info=info, return_link=self.headers['referer'])

        encoded = result.encode()
        f = BytesIO()
        f.write(encoded)
        f.seek(0)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        if f:
            try:
                self.copyfile(f, self.wfile)
            finally:
                f.close()


    def handle_post_data(self):
        """
        example data:

        '-----------------------------1913862203126697615536167098\r\n'
        'Content-Disposition: form-data; name="upload"; filename="samplefile"\r\n'
        'Content-Type: application/x-shellscript\r\n'
        '\r\n'
        'data .........................\n'
        '\r\n'
        '-----------------------------1913862203126697615536167098--\r\n'
        """

        # get boundary !
        if py3k:
            boundary = self.headers.get_boundary()
        else:
            boundary = self.headers.plisttext.split("=")[1]

        total = int(self.headers['content-length'])

        ####################
        # check boundary
        ####################

        line = self.rfile.readline()
        total = total - len(line)

        if not boundary in line.decode():
            return "Fail : Content NOT begin with boundary"

        ####################
        # get filepath
        ####################

        line = self.rfile.readline()
        total = total - len(line)

        files = re.findall(r'Content-Disposition.*; filename="(.*)"', line.decode())

        if not any(files):
            return "Fail : You don't have filename !?"

        # use SimpleHTTPServer's translate_path which will exist later :P
        path = self.translate_path(self.path)

        filepath = os.path.join(path, files[0])

        ####################
        # skip
        ####################

        line = self.rfile.readline()    # content type
        total = total - len(line)

        line = self.rfile.readline()    # empty
        total = total - len(line)

        ####################
        # write file
        ####################

        preline = self.rfile.readline()
        total = total - len(preline)

        try:
            output = open(filepath, 'wb')
        except IOError:
            return "Fail : Can't create file, permission denied."

        with output:

            for line in self.rfile:

                total = total - len(line)

                if total < 0:
                    return "Fail : you have so many data !?"

                try:
                    if boundary in line.decode():
                        output.write(preline.rstrip())
                        return "Success : upload success !"
                except UnicodeDecodeError:
                    # non plain text data may comes here
                    pass

                output.write(preline)
                preline = line


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

class SimpleHTTPRequestWithPostHandler(SimpleHTTPRequestHandler, SimplePostRequestHandler):
    pass



def run(HandlerClass=BaseHTTPRequestHandler,
        ServerClass=HTTPServer, protocol="HTTP/1.0", port=8000, bind=""):
    """from CPython http.server.test

    put it here for both Python 2 & 3 and further modification

    """

    server_address = (bind, port)

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()

    print("Serving HTTP on {} port {} ...".format(sa[0], sa[1]))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        httpd.server_close()
        sys.exit(0)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()


    # run server
    run(HandlerClass=SimpleHTTPRequestWithPostHandler,
        ServerClass=ThreadingSimpleServer,
        bind=args.bind,
        port=args.port)
