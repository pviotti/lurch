#!/usr/bin/env python

#Created on May 10, 2010
#@author: Paolo VIOTTI

import sys, readline

import lurch.NetworkManager as NetworkManager
import lurch.CCNxManager as CCNxManager

# TODO:
#     tc -s -d qdisc show 

# CCNx MODIFIED FILES:
# - VLC: ccn.c (logging, chunk size)
# - SegmentationProfile.java  (chunk size)
# - ccnd.c, ccnd_private.c, ccnd_stats.c (logging, LRU)
# - ccncatchunks2.c

welcome = \
"""================================================
              Welcome to Lurch
================================================
* Type 'h' for a brief help
"""

help = """
* Help:
    General commands:                                 CCNx commands:
        help,  h: this help                                startccn, sccn: start ccnd
        howto, ht: how-to                                  killccn, kccn: kill ccnd 
        quit, q: quit                                      upccn, uccn: update ccn from git [!!]
                                                           startrepo, srepo: start ccnx repository 
    Network commands:                                      killrepo, krepo: kill ccnx repository 
        ping, p: ping nodes                                cfiles, cf: create files to add to the repositories
        list, l: list nodes                                arepo, addrepo: add files to the repositories 
        route, r: list routes                              listrepo, lstrepo: dump the repository names   
        tunnel, t: list tunnels                            routeccn, rccn: set ccnx routing 
        ifconf, i: list interfaces                         statccn, ccns: list ccnd forwarding table
        script, s: create scripts                          simulate, sim: simulate test   
        lcreate, cl: execute creation scripts              start: start test  
        lremove, rl: execute removal scripts               reset, rs: reset cache before restarting the test [hardcoded!]                                                                                                                                                 
"""
    
how_to = """
  * Brief guided tour of the functions of Lurch:
        0) fill the configuration file (lurch.conf) and start lurch
        1) verify the connectivity of the nodes --> ping, list, tunnel, ifconf
        2) create and execute tunnel scripts --> script, lcreate
        3) start ccnd and the repositories --> startccn, startrepo
        4) configure ccnx routing --> routeccn
        5) add files to repositories --> addrepo
        6) start download test --> start
"""

batch_usage = """Usage: python lurch.py [-s|-t|-r]
            -r: restart ccnd before a new test
            -s: simulate
            -t: start test"""
            
class ShellCompletion:
    def __init__ (self):
        self.prefix = None
        self.commands = ["help", "howto", "quit", "ping", "list", "route", "tunnel", "ifconf", "script",
                        "lcreate", "lremove", "startccn", "killccn", "startrepo", "killrepo", "cfiles",
                        "arepo", "listrepo", "routeccn", "statccn", "simulate", "start", "reset"]
        
    def complete (self, prefix, index):
        if prefix != self.prefix:
            self.matching = [word for word in self.commands if word.startswith(prefix)]
            self.prefix = prefix
        if index < len(self.matching):
            return self.matching[index]
        else:
            return None
        
def prompt(net, ccn):
    completion = ShellCompletion()
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completion.complete)
    
    print welcome
    while True:
        cmd = raw_input("Lurch > ").lower()
        
        # general functions
        if cmd in ('q', 'quit'):
            print " * Exit Lurch..."
            break
        elif cmd in ('h', 'help'):
            print help
        elif cmd in ('ht', 'howto'):
            print how_to

        # network functions    
        elif cmd in ('p', 'ping'):
            net.pingAll()  
        elif cmd in ('l', 'list'):
            print " * Listing the nodes of the network:"
            print net  
        elif cmd in ('r', 'route'):
            net.lstRoutes()
        elif cmd in ('t', 'tunnel'):
            net.lstTunnels()
        elif cmd in ('i', 'ifconf'):
            net.lstInterfaces()
        elif cmd in ('s', 'script'):
            net.createScripts()
        elif cmd in ('cl', 'lcreate'):
            net.createLinks()
        elif cmd in ('rl', 'lremove'):
            net.removeLinks()
            
        # CCNx functions    
        elif cmd in ('sccn', 'startccn'):
            ccn.startCCND(net.nodes.keys())
        elif cmd in ('kccn', 'killccn'):
            ccn.stopCCND(net.nodes.keys())
        elif cmd in ('rccn', 'routeccn'):
            ccn.createCCNxRoutingScripts(net.nodes)
            ccn.setCCNxRouting()
        elif cmd in ('ccns', 'statccn'):
            ccn.lstCCNdStatus(net.nodes)
        elif cmd in ('cf', 'cfiles'):
            mb = raw_input("\tDimension [MB] > ").lower()
            ccn.createFiles(mb)
        elif cmd in ('arepo', 'addrepo'):
            ccn.addFilesToRepos()
        elif cmd in ('srepo', 'startrepo'):
            ccn.startRepos()
        elif cmd in ('krepo', 'killrepo'):
            ccn.stopRepos()
        elif cmd in ('lstrepo', 'listrepo'):
            ccn.lstRepo()
        elif cmd in ('reset', 'rs'):
            ccn.resetCache()
        elif cmd in ('uccn', 'upccn'):
            res = raw_input("\tAre you sure? [n|y|h = help] > ").lower()
            if res == "y":
                ccn.updateCCNx(net.nodes.keys())
            elif res == "h":
                print ccn.updateCCNx.__doc__
        
        # CCNx test functions 
        elif cmd in ('sim', 'simulate'):
            ccn.simulate()
        elif cmd == 'start':
            ccn.startTest()
        
        elif cmd == '':
            pass
        else:
            print " # Unknown command"
            



if __name__ == '__main__':
    net = NetworkManager.NetworkManager()
    ccn = CCNxManager.CCNxManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "-s":
            ccn.simulate()
        elif sys.argv[1] == "-t":
            ccn.startTest()
        elif sys.argv[1] == "-r":
            ccn.resetCache()
        else:
            print "Error: unknown parameter \"{0}\"".format(sys.argv[1])
            print batch_usage
            sys.exit(1)
        sys.exit(0)
        
    prompt(net, ccn)