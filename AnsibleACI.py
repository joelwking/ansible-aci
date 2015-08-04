#
#  AnsibleACI.py
#
"""
   Module for connection between a Python application and a APIC controller

   Copyright (c) 2015 World Wide Technology, Inc.
                  
   Author: Joel W. King, World Wide Technology

# Version     Date           Comments
# ----------- ------------   -------------------------------------------------
# 2.0         7 April 2015   Refactored for github
# 2.1        15 April 2015   Removed ppXML, we are using json
# 2.2         4 Aug   2015   use HTTPs, included "verify=False"
# 
#
"""
import requests
import xml
import xml.dom.minidom
import time
#
class Connection(object):
    """
      Connection class for Python to APIC controller REST Calls
   
    """
    def __init__(self):                               
        self.version = "Ver 2.2"                      # Version information
        self.debug = False                            # When enabled, prints more info for debugging
        self.transporttypes = ["http", "https"]       # Valid transport types
        self.transport = self.transporttypes[1]       # use HTTPs
                                                      
        self.controllername = "192.0.2.1"             # IP address or hostname of the controller
        self.username = "admin"
        self.password = "admin"
        self.cookie = None 
        self.content = None
        self.creationTime = 0
        self.my_creationTime = 0
        self.refreshTimeoutSeconds = 0
                                                      # Headers field to the REST call, XML format 
        self.HEADER = {'content-type':"application/xml"} 

                                                      # specific templates for core functions
        self.aaaLogin_XML_template = '<aaaUser name="%s" pwd="%s" />'
        self.aaaLogout_XML_template = '<aaaUser name="%s" />'
                                                      # generic templates for all other REST Calls
        self.generic_XML = None
        self.generic_URL = "%s://%s/api/mo/uni.xml"   # Used by both GET and POST
        return
#
#
#
    def aaaLogout(self):
        """ logs off the controller"""
        URL = "%s://%s/api/aaaLogout.xml" % (self.transport,self.controllername)
        XML = self.aaaLogout_XML_template % self.username
        try:
            r = requests.post(URL, data=XML, cookies=self.cookie, headers=self.HEADER, verify=False)
        except:
            if self.debug:
                print "aaaLogout failure XML: %s " % (XML)
            return(999)
        else:
            self.content =  r.content.encode("utf-8")
            self.creationTime = 0                          # when creationTime is zero, assume loggedout
        return r.status_code

#
#  
#
    def aaaLogin(self):
        """ create session with APIC an store off the cookie 
            r.content contains "token=" which is the same value as in the cookie
            r.conent also has refreshTimeoutSeconds="600" and creationTime="1399878720"
            time.time() gives the current time in seconds since the Epoch, similar to creationTime
        """

        URL = "%s://%s/api/aaaLogin.xml" % (self.transport,self.controllername)
        XML = self.aaaLogin_XML_template % (self.username,self.password)
        try:
            r = requests.post(URL, data=XML, headers=self.HEADER, verify=False)
        except requests.ConnectionError as e: 
            print "aaaLogin failure\nURL:\t%s \nXML:\t%s " % (URL, XML)
            return(999)
        else:
           try:
               self.cookie = {'APIC-cookie':r.cookies['APIC-cookie']}
           except KeyError:
               print "aaaLogin failure\nURL:\t%s \nXML:\t%s " % (URL, XML)
               return(999)
           else:
               self.content =  r.content.encode("utf-8")   
               self.savecreationTime(self.content)
               self.saverefreshTimeoutSeconds(self.content)
               if self.debug: 
                   print "Successful aaaLogin\nURL:\t%s \nXML:\t%s \ncontent:\t%s \ncreationTime:\t%s \ntimeout:\t%s \ncookie:\t%s" % \
                          (URL, XML, self.content,self.creationTime,self.refreshTimeoutSeconds,self.cookie)
               return(r.status_code)
#
#
#
    def is_connected(self):
        """ return true if we are connected to the controller, self.creationTime is 0 when not connected or logged out
            otherwise, it has a interger timestame that will evaluate to true 
        """
        return self.creationTime
# 
#
#
    def setUsername(self,username):
        " sets username to authenticate to the controller "
        self.username = username
#
#  
#
    def setPassword(self,password):
        " sets password to authenticate to the controller "
        self.password = password
#
#   
#
    def setcontrollerIP(self,controllerIP):
        "sets controller IP address or hostname"
        self.controllername = controllerIP
#
#  
#
    def setDebug(self,debugvalue):
        """ sets the debug value """ 
        self.debug = debugvalue
#
#
#
    def parsecontent(self,content,string):
       """
           Parses out the value from the HTTP content variable of the given string. 
           The last character of the string is assumed to be the trailing delimiter, eg
           If we have creationTime="1399957021" in content, we pass 'creationTime="' as
           our string. Return a string to the caller.
       """
       x = content.split(string)
       delimiter = string[-1]                              # get the last character of the string, 
       try:
           y = x[1].split(delimiter)
       except:
            y = ["0",None]                                 # Didn't find the value, return a zero
            if self.debug: 
                print "\nparsecontent failure: \nstring:%s \ncontent:%s" % (string,content)
       return y[0]
#
#
#
    def savecreationTime(self, content):
        "saves the time in seconds from the Epoch of a successful login"
        self.creationTime = int(self.parsecontent(self.content,'creationTime="'))
        self.my_creationTime = int(time.time())             # my clock and the APIC clock may not both synced
#
#
#
    def saverefreshTimeoutSeconds(self, content):
        "saves the refreshTimeout from a successful login"
        self.refreshTimeoutSeconds = int(self.parsecontent(self.content,'refreshTimeoutSeconds="'))
#
#
#
    def setgeneric_XML(self,XML):
        """ sets the generic XML template """
        self.generic_XML  = XML  
#
#
#
    def setgeneric_URL(self,URL):
        """ sets the generic URL template """
        self.generic_URL = URL
#
#
#
    def genericPOST(self):
        """ Issue generic POST request """
        URL = self.generic_URL % (self.transport,self.controllername)
        self.content = None
        try:
            r = requests.post(URL, data=self.generic_XML, cookies=self.cookie, headers=self.HEADER, verify=False)
        except requests.ConnectionError as e: 
            print "genericPOST failure\nURL:\t%s \nXML:\t%s " % (URL, self.generic_XML)
            return(999)
        else:
            self.content =  r.content.encode("utf-8")
            if self.debug: 
               print "genericPOST\nstatus_code:\t%s \nurl:\t%s \ncontent:\t%s \nXML:\t%s" % \
                     (r.status_code, r.url, self.content, self.generic_XML)            
            return(r.status_code)
#
#
#
    def genericGET(self):
        """ Issue generic GET request """
        URL = self.generic_URL % (self.transport, self.controllername)
        self.content = None
        try:
            r = requests.get(URL, cookies=self.cookie, headers=self.HEADER, verify=False)
        except requests.ConnectionError as e: 
            print "genericGET failure\nURL:\t%s " % (URL)
            return(999)
        else:
            self.content =  r.content.encode("utf-8")
            if self.debug: 
               print "genericGET\nstatus_code:\t%s \nurl:\t%s \ncontent:\t%s " % \
                     (r.status_code, r.url, self.content)            
            return(r.status_code)

#
#
#
    def get_content(self):
        " return the content of the web query "
        return self.content
#
#
#
#
