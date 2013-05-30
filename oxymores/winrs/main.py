# coding: utf-8

'''
Created on 3 may 2012

@author: Marc-Antoine Gouillart
@license: Apache v2
'''

from consts import *
import uuid
import httplib
import xml.etree.ElementTree as ET
import base64
import sys
from threading import Thread
from xml.sax.saxutils import escape

class WinRSConnection:
    """Represents a connection to a remote Windows server or client"""
    hc = None # The HTTP Connection
    debug = True
    user = None
    password = None
    address = None
    url = None
		
    def WinRSCommand(self, shellEPR, cmd, args):
        if self.debug:
            print u"**************************************************\nSTARTING COMMAND\n**************************************************"
        
        COMMAND_MESSAGE = SOAP_ENVELOPE_XML.replace("{Url}", self.url). \
                    replace("{ResourceUri}", WINRS_CMD_URI).replace("{ActionUri}", WINRS_COMMAND_URI).replace("{MessageId}", str(uuid.uuid1())).\
                    replace("<!--SelectorSet-->",  WINRS_SELECTORSET %shellEPR).replace("<!--OptionSet-->", WINRS_COMMAND_OPTION_XML).\
                    replace("<!--Body-->", WINRS_COMMAND_BODY_XML).replace("{Command}", escape(cmd)).replace("{Arguments}", escape(args)) 
        if self.debug:
            print COMMAND_MESSAGE
        
        commandResponse = self.ExecuteHTTPRequest(COMMAND_MESSAGE);
        
        # Extract command id
        commandId = commandResponse.find(".//{http://schemas.microsoft.com/wbem/wsman/1/windows/shell}CommandId").text
        #commandId = SelectSingleNodeValue(commandResponse, "//rsp:CommandResponse/rsp:CommandId");
        return commandId;
    
    
    def WinRSReceive(self, shellEPR, commandId, openFile, background = False, sequenceId=0):
        done = False
        
        if self.debug:
            print u"**************************************************\nSTARTING RECEIVE\n**************************************************"
        
        while (not done):
            receiveXml = SOAP_ENVELOPE_XML.replace("{Url}", self.url).replace("{ResourceUri}", WINRS_CMD_URI).\
                replace("{ActionUri}", WINRS_RECEIVE_URI).replace("{MessageId}", str(uuid.uuid1())).\
                replace("<!--SelectorSet-->", WINRS_SELECTORSET %shellEPR).replace("<!--Body-->", WINRS_RECEIVE_BODY_XML).\
                replace("{SequenceId}", str(sequenceId)).replace("{CommandId}", commandId)
            if self.debug:
                print receiveXml
        
            receiveResponse = self.ExecuteHTTPRequest(receiveXml);
            res = receiveResponse
            
            output = res.findall(".//{http://schemas.microsoft.com/wbem/wsman/1/windows/shell}Stream")
            #output = SelectNodeValues(receiveResponse, "//rsp:ReceiveResponse/rsp:Stream[@Name='stdout' or @Name='stderr']", true);
            for o in output:
                if o is not None and o.text is not None:
                    #openFile.write( base64.b64decode( o.text))
                    #openFile.flush(
                    print base64.b64decode( o.text)
                    sys.stdout.flush()
            sequenceId = sequenceId + 1
        
            cmdState = res.find(".//{http://schemas.microsoft.com/wbem/wsman/1/windows/shell}CommandState")
            #cmdState = SelectSingleNodeValue(receiveResponse, "//rsp:ReceiveResponse/rsp:CommandState/@State");
            if (cmdState.attrib["State"] == "http://schemas.microsoft.com/wbem/wsman/1/windows/shell/CommandState/Done"):
                done = True;
            
            if (not done and background):
                t = Thread(target=self.WinRSReceive, kwargs={'shellEPR':shellEPR, 'commandId':commandId, 'openFile':openFile, 'sequenceId':sequenceId})
                t.start()
                break
    
    
    def WinRSSend(self, shellEPR, commandId, textFlow):
        if self.debug:
            print "**************************************************\nSTARTING SEND\n**************************************************"
        
        createXml = SOAP_ENVELOPE_XML.replace("{Url}", self.url).replace("{ResourceUri}", WINRS_CMD_URI).\
            replace("{ActionUri}", WINRS_SEND_URI).replace("{MessageId}", str(uuid.uuid1())).\
            replace("<!--SelectorSet-->", WINRS_SELECTORSET %shellEPR).replace("<!--Body-->", WINRS_SEND_BODY_XML).\
            replace("{CommandId}", commandId).replace("{Base64Flow}", base64.encodestring(textFlow))
        if self.debug:
            print "SendRequest:\n" + createXml
        
        response = self.ExecuteHTTPRequest(createXml);
        return response.find(".//{http://schemas.microsoft.com/wbem/wsman/1/windows/shell}SendResponse").text  # should be empty. This find is to detect failure.  
         
    
    def WinRSCreate(self, user, password, host, port = "5985"):
        if self.debug:
            print "**************************************************\nSTARTING CREATE\n**************************************************"
        self.user = user
        self.password = password
        self.address = "%s:%s" %(host, port)
        self.url = "http://%s/wsman" %self.address
		
        createXml = SOAP_ENVELOPE_XML.replace("{Url}", self.url).replace("{ResourceUri}", WINRS_CMD_URI).\
            replace("{ActionUri}", WINRS_CREATE_URI).replace("{MessageId}", str(uuid.uuid1())).\
            replace("<!--Body-->", WINRS_CREATE_BODY_XML)
        if self.debug:
            print "CreateRequest:\n" + createXml
        
        reponse = self.ExecuteHTTPRequest(createXml);
        return reponse.find(".//{http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd}Selector").text
      
           
    def ExecuteHTTPRequest(self, message):
        self.hc = httplib.HTTPConnection(self.address) 
        
        auth = "Basic %s" % (":".join([self.user, self.password]).encode("Base64").strip("\r\n"))
        
        self.hc.putrequest("POST", self.url)
        self.hc.putheader("User-Agent", "pyWinRS")
        self.hc.putheader("Content-Type", "application/soap+xml;charset=UTF-8")
        self.hc.putheader("Content-Length", str(len(message)))
        self.hc.putheader("Authorization", auth)
        self.hc.endheaders();
        self.hc.send(message);
        
        # Get response
        responseO = self.hc.getresponse(True)
        response = responseO.read()
        if self.debug:
                print "*****Receive*****\nHTTP return code: " + str(responseO.status) + "\nReason: " + responseO.reason
        if self.debug:
            print response
                
        if (response is None or response == ""):
            raise Exception("Server answer to request was empty. HTTP code: %s" %responseO.status)
        x = ET.fromstring(response)
        if (x is None):
            raise Exception("Server answer cannot be parsed as XML. HUGE problem")
        
        # Check if WS-MAN error - throw an exception in that case
        err = x.find(".//{http://www.w3.org/2003/05/soap-envelope}Fault")
        if not err is None:
            abstract = x.find(".//{http://www.w3.org/2003/05/soap-envelope}Text").text
            raise Exception(abstract)
        
        # If no error, return full XML SOAP response as a XML object
        return x
        
        
    def WinRSDelete(self, shellEPR):
        if self.debug:
            print "**************************************************\nSTARTING DELETE\n**************************************************"
        deleteXml = SOAP_ENVELOPE_XML.replace("{Url}", self.url).replace("{ResourceUri}", WINRS_CMD_URI).\
            replace("{ActionUri}", WINRS_DELETE_URI).replace("{MessageId}", str(uuid.uuid1())).\
            replace("<!--SelectorSet-->", WINRS_SELECTORSET %shellEPR)
        if self.debug:
            print "DeleteRequest:\n" + deleteXml
        
        self.ExecuteHTTPRequest( deleteXml); # No need to check return object.
    
