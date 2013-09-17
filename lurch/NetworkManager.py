'''
Created on May 14, 2010
@author: Paolo VIOTTI
'''

import socket
import os, sys
import stat
import ConfigParser
import subprocess

conf_file = "lurch.conf"
scripts_dir = "./scripts/"
create_suffix = "_create.sh"
remove_suffix = "_remove.sh"
shaping_bw = "5mbit"

class Node(): 
    def __init__(self, name):
        self.name = name
        try:
            self.address = socket.gethostbyname(name) # slows down!
        except Exception:
            print " # Error: cannot translate name to IP address."
            sys.exit(1)
        self.links = {}
        
    def __str__(self):
        str = "\t{0} - {1} - links:\n".format(self.name, self.address)
        for l in self.links.keys():
            str += "\t\t{0}, tap{1}, 10.0.0.{2}, is shaped: {3}\n".format(l, self.links[l][0], 
                                                                          self.links[l][1], self.links[l][2])
        return str

    
class NetworkManager():
    def __init__(self):
        self.nodes = {}
        config = ConfigParser.ConfigParser()
        config.read(conf_file)
        
        subnet_index = 1    # last number of the overlay IP addresses, e.g. 10.0.0.X
        sorted_links_options = config.options("Links")  # to get the option sorted 
        sorted_links_options.sort()                     # from the config file
        for option in sorted_links_options:
            node_name = option.strip()
            self.nodes[node_name] = Node(node_name)
            linked_nodes = config.get("Links", option).split()
            for n in linked_nodes:
                n_name = n.strip()
                if n_name.startswith("*"): 
                    is_shaped = True
                    n_name = n_name[1:]
                else: 
                    is_shaped = False
                self.nodes[node_name].links[n_name] = [linked_nodes.index(n),   # local interface number 
                                                       subnet_index,            # overlay IP address - last number
                                                       is_shaped]               # whether should be shaped or not
                subnet_index += 1
                
        if not os.path.isdir(scripts_dir):
            os.mkdir(scripts_dir)

    def __str__(self):
        str = ""
        for node in self.nodes.keys():
            str += self.nodes[node].__str__()
        return str
            
    def pingAll(self):
        print " * Pinging all the nodes of the network:"
        for n in self.nodes.keys():
            p = subprocess.Popen(['ping', '-c','1', n], stdout=subprocess.PIPE)
            if p.wait() == 0:
                stats = p.stdout.readlines()[-1]              
                print "\t* {0} is alive, rtt: {1} ms".format(n, stats.split('/')[-3])
            else:
                print "\t# {0} did not respond".format(n)  
                
    def lstRoutes(self):
        print " * Showing current routing tables:"
        for n in self.nodes.keys():
            params = ["ssh", "root@" + n, "route", "-n"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() == 0:
                print "\t*", n
                for l in p.stdout.readlines()[1:]:
                    print "\t"+l.strip()              
            else:
                print "\t# {0} gave an error".format(n)
                for l in p.stdout.readlines(): print "\t" + l.strip() 
            print 
            
    def lstTunnels(self):
        print " * Showing current tunnels:"
        for n in self.nodes.keys():
            params = ["ssh", "root@" + n, "iptunnel", "show"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() == 0:
                lines = p.stdout.readlines()
                if len(lines) < 2:
                    print "\t*", n, "has got no IP tunnels"
                else:
                    print "\t*", n
                    for l in lines[1:]:
                        print "\t"+l.strip()  
                    print            
            else:
                print "\t# {0} gave an error".format(n)
                for l in p.stdout.readlines(): print "\t" + l.strip()
                
    def lstInterfaces(self):
        print " * Showing interfaces:"
        for n in self.nodes.keys():
            params = ["ssh", "root@" + n, "ifconfig"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() == 0:
                print "\t*", n
                for l in p.stdout.readlines():
                    if l != '\n': print "\t" + l[:-1]  
                print            
            else:
                print "\t# {0} gave an error".format(n)
                for l in p.stdout.readlines(): print "\t" + l.strip()
                
    def createScripts(self):
        tunnel_template = "iptunnel add tap{0} mode ipip local {1} remote {2}\n"
        if_template = "ifconfig tap{0} 10.0.0.{1} netmask 255.255.255.255 up\n"
        route_template_1 = "route add -net 10.0.0.0/24 tap{0}\n"
        route_template_2 = "route add 10.0.0.{0} tap{1}\n"
        # with HTB:
        shaping_template = ("tc qdisc add dev tap{0} root handle 1: htb default 1\n" 
                            "tc class add dev tap{0} parent 1: classid 1:1 htb rate {1} ceil {1}\n")
        scheduler_template = "tc qdisc add dev tap{0} parent 1:1 handle 20: ccnsfq limit 20\n"
        # with TBF:
        #shaping_template = ("tc qdisc add dev tap{0} root handle 1: tbf rate {1} burst 100kb " 
        #                    "latency 30ms peakrate 12mbit minburst 1540\n")
        #scheduler_template = "tc qdisc add dev tap{0} parent 1:0 handle 2:10 ccnsfq limit 20\n"
        # with PSPacer: ==> does not work on virtual interfaces (tapX)
        #shaping_template = ("tc qdisc add dev tap{0} root handle 1: psp default 1\n"
        #                    "tc class add dev tap{0} parent 1: classid 1:1 psp rate {1}\n")
        #scheduler_template = "tc qdisc add dev tap{0} parent 1:1 handle 10: ccnsfq limit 20\n"
        remove_template = "iptunnel del tap{0}\n"
        
        print " * Creating scripts to set links..."
        for node in self.nodes.keys():
            if len(self.nodes[node].links)>0:
                f = open(scripts_dir + self.nodes[node].name + create_suffix, 'w')
                f.write("#!/bin/bash\n\n")
                if len(self.nodes[node].links)>1:    
                    f.write("sysctl -w net.ipv4.ip_forward=1\n")
                f.write("modprobe ipip\n\n")
                
                for n in self.nodes[node].links.keys():
                    f.write(tunnel_template.format(self.nodes[node].links[n][0], self.nodes[node].address,
                                                   self.nodes[n].address))
                    f.write(if_template.format(self.nodes[node].links[n][0], self.nodes[node].links[n][1]))
                    if len(self.nodes[node].links) == 1:
                        f.write(route_template_1.format(self.nodes[node].links[n][0]))
                    else:
                        f.write(route_template_2.format(self.nodes[n].links[node][1], 
                                                        self.nodes[node].links[n][0]))
                    if self.nodes[node].links[n][2]:
                        # RULE: the interface that is shaped has the ccnsfq scheduler
                        f.write(shaping_template.format(self.nodes[node].links[n][0], shaping_bw))
                        f.write(scheduler_template.format(self.nodes[node].links[n][0]))
                    f.write("\n")
                f.close()
                os.chmod(scripts_dir + self.nodes[node].name + create_suffix, stat.S_IXUSR | stat.S_IRUSR |
                                                                                 stat.S_IWUSR | stat.S_IRWXU)
                
        print " * Creating scripts to tear down links..."
        for node in self.nodes.keys():
            if len(self.nodes[node].links)>0:
                f = open(scripts_dir + self.nodes[node].name + remove_suffix, 'w')
                f.write("#!/bin/bash\n\n")
                
                for n in self.nodes[node].links.keys():
                    f.write(remove_template.format(self.nodes[node].links[n][0]))
                f.close()                
                os.chmod(scripts_dir + self.nodes[node].name + remove_suffix, stat.S_IXUSR | stat.S_IRUSR | 
                                                                                stat.S_IWUSR | stat.S_IRWXU)
                
    def createLinks(self):
        print " * Creating the links..."
        for node in self.nodes.keys():
            params = ["scp",scripts_dir + node + create_suffix, "root@" + node + ":~"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() != 0:
                print "\t# Error while copying the creation script to", node
                return
            
            params = ["ssh",  "root@" + node, "./" + node + create_suffix]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() == 0:
                print "\t* Links created on", node
            else:
                print "\t# Error while executing the creation script on", node
                
    def removeLinks(self):
        print " * Removing the links..."
        for node in self.nodes.keys():
            params = ["scp", scripts_dir + node + remove_suffix, "root@" + node + ":~"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() != 0:
                print "\t# Error while copying the removal script to", node
                return
            
            params = ["ssh",  "root@" + node, "./" + node + remove_suffix]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() == 0:
                print "\t* Links removed on", node
            else:
                print "\t# Error while executing the removal script on", node
                
