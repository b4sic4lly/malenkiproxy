#!/usr/bin/env python
import BaseHTTPServer
import urllib2
import quopri
import sys
import ConfigParser
import argparse
import traceback
from urllib2 import HTTPError
import os

class MalenkiProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
    def do_POST(self):
        MalenkiProxyHandler.do_GET(self)    
    
    def requesturl(self):
        try:
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', self.headers['user-agent'])]
            response = opener.open(self.path)
            return response
        except HTTPError as e:
             print "Response: %d: %s" % (e.code , e.reason)            
        except:
            print "urllib2 was not successful"
            traceback.print_exc()
            return None
        
    
    def getURLfilename(self):
        arrurlparts = self.path.split("/")
        # replace some .. stuff to countermeasure directory traversal (but probably not all)
        newfilename = arrurlparts[len(arrurlparts)-1].replace("..", "")
        if newfilename == "":
            newfilename = "index"
        
        # but return only 255 chars incase it is too long
        return newfilename[0:255]
    
    def log_message(self, format, *args):
        return
        
    def do_GET(self):
        """Respond to a GET request."""
        
        print "-----------------------------------------------------"
        print "Request: %s" % self.path
        
        response = MalenkiProxyHandler.requesturl(self)
        if response == None:
            return
        
        # read data/header
        data = response.read()
        headerdict = response.info().dict
        code = response.getcode()
        
        # print something
        print "Response: %d" %  code
        
        # get the filename of the current request
        newfilename = MalenkiProxyHandler.getURLfilename(self)
        
        # replace files
        for item in config.items("FileReplace"):
            if newfilename == item[0]:
                # replace file
                responsefile = open(item[1], "rb")
                data = responsefile.read()
                headerdict["content-length"] = str(len(data))
                print "Replacing file %s with %s. New length %s Bytes" % (item[0], item[1], headerdict["content-length"])
                responsefile.close()
        
        # save the file
        if args.save_files == True:
            if not os.path.exists("files"):
                os.makedirs("files")
            print "Saving file %s" % ("files/" + newfilename)
            curfile = open("files/" + newfilename, "wb")
            curfile.write(data)
            curfile.close()
            
        # read the returned code and set it        
        self.send_response(code)
        
        # set the header
        for headerkey in headerdict:
            self.send_header(headerkey, headerdict[headerkey])
        self.end_headers()
        
        self.wfile.write(data)        


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='specify config file')
    parser.add_argument('-s', '--save-files', action="store_true", default=False, help='if set, proxy saves every transaction in a file')
    args = parser.parse_args()
    
    if args.config == None:
        parser.print_help()
    else:
        # load the config file for replacing files
        config = ConfigParser.RawConfigParser()
        config.read(args.config)
        server_host = config.get('General', 'host')
        server_port = config.getint('General', 'port')
        
        
        httpd = BaseHTTPServer.HTTPServer((server_host, server_port), MalenkiProxyHandler)
        try:
            print "Starting MalenkiProxy..."
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
        