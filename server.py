#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        print("Yee")
        self.data = self.request.recv(1024).strip().decode("utf-8").split("\r\n")
        self.header = {
            "statusCode": "200 OK",
            "contentType": "text/plain",
            "reponseBody": "",
            "location": ""
        }

        #print ("Got a request of: %s\n" % self.data)

        method = self.data[0].split(' ')[0]
        url = self.data[0].split(' ')[1]
        if method == 'GET':
            location = os.path.abspath("www") + url
            self.pathHandler(location)
        else:
            self.handle405()

        self.request.sendall(bytearray(self.headerHandler(),'utf-8'))
    
    def handle301(self, location):
        self.header["statusCode"] = "301 Moved Permanently"
        self.header["location"] = location + "/"
    def handle404(self):
        self.header["statusCode"] = "404 Not Found"
    def handle405(self):
        self.header["statusCode"] = "405 Method Not Allowed"

    def pathHandler(self, location):
        #print("Location: ", location)
        validation = location.split('/')
        validation = validation[validation.index("www") + 1:]
        counter = 0
        #print("Check list: ", validation)
        for dir in validation:
            if dir == "..":
                counter += 1
        #print("Counter for ..: ", counter)
        if (os.path.exists(location) and counter < len(validation) / 2):
            if (os.path.isdir(location)):
                if (location.endswith("/")):
                    location += "index.html"
                self.fileHandler(location)
            else:
                self.fileHandler(location)

        else:
            self.handle404()

    def fileHandler(self, url):
        try:
            if url.endswith("css"):
                self.header["contentType"] = "text/css"
            elif url.endswith("html"):
                self.header["contentType"] = "text/html"
            self.header["reponseBody"] = open(url).read()
        except FileNotFoundError:
            self.handle404()
        except IsADirectoryError:
            self.handle301(url)


    def headerHandler(self):
        header = "HTTP/1.1 {}\n".format(self.header["statusCode"])

        header +=  "Location: {}\n".format(self.header["location"].split("www", 1)[1]) if self.header["location"] != "" else ""
        header += "Content-Type: {}\n".format(self.header["contentType"])

        header += "Content-Length: {}\n".format(len(self.header["reponseBody"].encode("utf-8")))

        header += "\n{}".format(self.header["reponseBody"])

        header += "Connection: close\n"
        #print("*---------------*\nHeadr: {}\n*---------------*\n".format(header))
        return header


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
