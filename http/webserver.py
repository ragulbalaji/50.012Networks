#!/usr/bin/env python2

import SimpleHTTPServer
import SocketServer

class CS144Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    # Disable logging DNS lookups
    def address_string(self):
        return str(self.client_address[0])


PORT = 8080

Handler = CS144Handler
httpd = SocketServer.TCPServer(("", PORT), Handler)
print "Server1: httpd serving at port", PORT
httpd.serve_forever()
