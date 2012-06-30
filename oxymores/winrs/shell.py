'''
Created on 10 may 2012

@author: user1
'''

from main import WinRSConnection
import cmd
#import readline
import sys
from threading import Thread
from time import sleep
import traceback

class WindowsRemoteShell(cmd.Cmd):
    _connected = False
    _mode = "batch"
    
    def preloop(self):
        """Initialization code goes here"""
        self.con = WinRSConnection()
        self.con.debug = False
        self.prompt = "winrs# "
        #self.use_rawinput = False
        
    def default(self, line):
        # Default is a windows command for the remote system
        # so give it to the WINRS web service
        if (not self._connected):
            raise Exception("You are not connected to a remote system. Use connect.")
        
        if self._mode == "batch":
            cc = line.split(" ")[0]
            r = str.join(" ", line.split(" ")[1:])
            if r is None or r == "":
                r = " "
            
            self.commandid = self.con.WinRSCommand(self.c, cc, r)
            self.con.WinRSReceive(self.c, self.commandid, sys.stdout)
        elif self._mode == "interactive":
            self.con.WinRSSend(self.c, self.commandid, line + "\n")


    def do_connect(self, line):
        print "Connecting... (Ctrl-C to cancel)"    
        self._connected = True
        self.c = self.con.WinRSCreate()
        print "New WinRS session id is: " + self.c


    def do_disconnect(self, line):
        if (self._connected):
            self.con.WinRSDelete(self.c)
        self._connected = False


    def do_quit(self, line):
        if (self._connected):
            self.con.WinRSDelete(self.c)
        sys.exit()

        
    def do_interactive(self, line):
        t = Thread(target = self.test)
        t.start()
        if (not self._connected):
            raise Exception("You are not connected to a remote system. Use connect.")
        self._mode = "interactive"
        self.commandid = self.con.WinRSCommand(self.c, "cmd.exe", "/k dir c:")
        self.con.WinRSReceive(self.c, self.commandid, sys.stdout, True)
        
        while True:
            r = raw_input("XXXX")
            self.default(r)

        
    def onecmd(self, line):
        try:
            return cmd.Cmd.onecmd(self, line)
        except Exception, e:
            print "An error has occurred : %s" %e 
            #traceback.print_last()
            
    
    def emptyline(self):
        """Do not do anything on empty input lines"""
        pass
    
    def test(self, i = 0):
        sleep(1)
        #print (i+1)
        self.test(i+1)
    
shell = WindowsRemoteShell();
shell.cmdloop("Python Windows Remote Shell 0.0.1")
