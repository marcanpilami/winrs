# coding: utf-8

'''
Created on 10 may 2012

@author: Marc-Antoine Gouillart
@license: Apache v2
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
        l = line.split()
        if len(l) < 3:
            print u'invalid arguments'
            return
        user = l[0]
        password = l[1]
        host = l[2]
        port=5985
        if len(l) == 4:
            port=l[3]

        print "Connecting with user [%s] to server [%s] (Ctrl-C to cancel)" %(user, host)
        self.c = self.con.WinRSCreate(user, password, host, port)
        self._connected = True
        print u"New WinRS session id is: " + self.c

    def help_connect(self):
        print u'Opens an HTTP (not HTTPS) connection. Server must be configured to allow simple HTTP auth.\n\n\tconnect username password hostname [HTTP port]'
        print u'\n\tEXEMPLE\n\n\t\tconnect administrateur Pata1952 192.168.0.2 5985'

    def do_disconnect(self, line):
        if (self._connected):
            self.con.WinRSDelete(self.c)
        self._connected = False

    def help_disconnect(self):
        print u'Disconnects from the server (ends the session). Also called by "quit"'

    def do_quit(self, line):
        self.do_disconnect(line)
        sys.exit()

    def help_quit(self):
        print u'disconnects if ncesseray from the server and quits the program'
        
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

    def help_interactive(self):
        print u'VERY EXPERIMENTAL. Not finished in any way - many formatting issues\n\nInteractive cmd.exe shell.'
        
    def onecmd(self, line):
        try:
            return cmd.Cmd.onecmd(self, line)
        except Exception, e:
            print u"An error has occurred: %s" %e
            #traceback.print_last()
            
    
    def emptyline(self):
        """Do not do anything on empty input lines"""
        pass
    
    def test(self, i = 0):
        sleep(1)
        #print (i+1)
        self.test(i+1)
    
    def help_running_commands(self):
        print u'Once you are connected (see the "connect" command), simply type the commands in the prompt. They will be executed without an active shell, so most often you will want to have cmd.exe or powershell.exe in your command.'
        print u'\n\tC:\\Windows\\System32\\cmd.exe /C dir'
        print u'\tC:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -Command ls'

shell = WindowsRemoteShell();
shell.cmdloop(u"Python Windows Remote Shell 0.0.1")
