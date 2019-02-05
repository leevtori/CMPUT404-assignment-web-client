#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
from urllib.parse import urlparse


def help():
    print("httpclient.py [GET/POST] [URL]\n")

# return the response object and print to stdout
class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
        self.__str__()
    
    def __str__(self):
        print(self.code)
        print(self.body)

class HTTPClient(object):
    def get_host_port(self,url):
        u = urlparse(url)
        host = u.hostname
        port = u.port
        if port == None:
            port = 80
        return (host, port)

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        # split by line, code is the second item on first line
        d = data.split()
        return int(d[1])

    def get_headers(self,data):
        d = data.split("\r\n\r\n")
        return d[0]

    def get_body(self, data):
        # split by headers, and the msg body is after
        d = data.split("\r\n\r\n")
        return d[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # to handle 4XX errors
    def get_path(self, url):
        u = urlparse(url)
        if u.path == '':
            return '/'
        return u.path

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # get the host and port
        host, port = self.get_host_port(url)
        # make the connection
        self.connect(host, port)
        # make and send the request
        request = "GET "+self.get_path(url)+" HTTP/1.1\r\nHost: "+host+"\r\nAccept: */*\r\nConnection: Close\r\n\r\n"
        self.sendall(request)
        # get the response
        response = self.recvall(self.socket)
        # get the code and body of response
        code = self.get_code(response)
        body = self.get_body(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # get the host and port
        host, port = self.get_host_port(url)
        # make the connection
        self.connect(host, port)
        # make and send the request
        request = "POST "+self.get_path(url)+" HTTP/1.1\r\nHost: "+host+"\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: "
        if args:
            data = urllib.parse.urlencode(args)
            dataLength = len(data)
            request += str(dataLength) + "\r\n\r\n"+data
        else :
            request += "0\r\n\r\n"

        self.sendall(request)

        # get the response
        response = self.recvall(self.socket)
        # get the code and body of response
        code = self.get_code(response)
        body = self.get_body(response)
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
