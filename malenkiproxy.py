'''
Created on Oct 14, 2015

@author: mft
'''

#!/usr/bin/env python
import BaseHTTPServer
import urllib2
import quopri
import sys


class MalenkiProxyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        
    def do_POST(s):
        MalenkiProxyHandler.do_GET(s)    
    
    def requesturl(s):
        try:
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', s.headers['user-agent'])]
            response = opener.open(s.path)
            return response
        except:
            print "urllib2 was not successful"
            print str(sys.exc_info()[0])
            return None
    
    def getURLfilename(s):
        arrurlparts = s.path.split("/")
        # replace some .. stuff to countermeasure directory traversal (but probably not all)
        newfilename = arrurlparts[len(arrurlparts)-1].replace("..", "")
        if newfilename == "":
            newfilename = "index"
            
        return newfilename
    
    def do_GET(s):
        """Respond to a GET request."""
        
        print "Acessing %s" % s.path
        
        response = MalenkiProxyHandler.requesturl(s)
        if response == None:
            return
        
        # read data/header
        data = response.read()
        headerdict = response.info().dict
        
        # get the filename of the current request
        newfilename = MalenkiProxyHandler.getURLfilename(s)
        
        # replace files
        if newfilename == "duckbox.pdf":
            # replace file
            print response.info().dict
            responsefile = open("wikileaks.pdf", "rb")
            data = responsefile.read()
            headerdict["content-length"] = str(len(data))
            print "new len : %s" % headerdict["content-length"]
            responsefile.close()
        else:
            # save the file
            curfile = open("files/" + newfilename, "wb")
            curfile.write(data)
            curfile.close()
        
        # read the code        
        code = response.getcode()
        s.send_response(code)
        
        for headerkey in headerdict:
            s.send_header(headerkey, headerdict[headerkey])
        s.end_headers()
        
        s.wfile.write(data)        


if __name__ == '__main__':
    server_host = 'localhost'
    server_port = 8080
    
    httpd = BaseHTTPServer.HTTPServer((server_host, server_port), MalenkiProxyHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
    