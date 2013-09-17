'''
Created on May 14, 2010
@author: Paolo VIOTTI
'''

import subprocess
import os
import ConfigParser
import copy
import logging
import threading
import time

conf_file = "lurch.conf"
results_file = "results.in"
pop_prob_file = "pop_prob.in"
log_tarfile = "logs.tar.gz"

scripts_dir = "./scripts/"
files_dir = "./files/"
video_dir = "./video/"
log_dir = "./log/"

num_files = 50
file_size = 5242880.0 #10485760.0 # bytes
#num_requests = 7000 # read from R scripts

r_scripts_dir = "./r-scripts/"
ccnx_dir = "/home/viotti/ccnx"
ccnx_git_url = "git://github.com/ProjectCCNx/ccnx.git"
routing_suffix = "_ccnrouting.sh"
reset_script = "reset.sh"

parallelism = "4"

class CCNxManager():
    
    def __init__(self):
        if not os.path.isdir(files_dir):
            os.mkdir(files_dir)
            
        self.videos = [] 
        self.files = []
        self.file_nodes = {}  # self.file_nodes[node_name] = [file_name1, file_name2..]
        self.video_nodes = {}
        self.routing_rules = {}
            
        config = ConfigParser.ConfigParser()
        config.read(conf_file)
        
        # Parse the CCNxRouting section of the configuration file
        for node in config.options("CCNxRouting"):
            self.routing_rules[node] = config.get("CCNxRouting", node).split() 
        
        # Parse the CCNxRoles section of the configuration file
        for n in config.get("CCNxRoles", "file").split():
            self.file_nodes[n] = []
        for n in config.get("CCNxRoles", "video").split():
            self.video_nodes[n] = []
        
        #print "file nodes: "
        #for i in self.file_nodes.keys(): print i
        #print "video nodes: "
        #for i in self.video_nodes.keys(): print i
        #print "routing rules: "
        #for i in self.routing_rules.keys(): print i, self.routing_rules[i]

    def startCCND(self, nodes):
        print " * Starting ccnd on the nodes..."
        for node in nodes:
            # with redirection of stdout and stderr 'cause otherwise it would block the ssh client
            params = ["ssh", "viotti@" + node, "ccndstart", ">", "/dev/null", "2>&1", "&"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() != 0:
                print "\t# Error while starting ccnd on", node
                return  
            print "\t* ccnd started on", node
    
    def stopCCND(self, nodes):
        print " * Stopping ccnd on the nodes..."
        for node in nodes:
            params = ["ssh", "viotti@" + node, "ccndstop"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() != 0:
                print "\t# Error while stopping ccnd on", node
            else:   
                print "\t* ccnd stopped on", node
    
    def createFiles(self, MB = 10):
        print " * Creating", num_files, "files of", MB, "MB..."
        for i in range (1, num_files+1):
            if len(str(i)) == 1:    str_num = '0' + str(i)
            else:   str_num = str(i)
            file_name = str_num + "_ABCDE.bin"
            # dd if=/dev/zero of=./files/x_ABCD.bin bs=$(( 1024 * 1024 )) count=y
            params = ["dd", "if=/dev/zero", "of=" + files_dir + file_name, 
                      "bs=1048576", "count=" + MB]
            p = subprocess.Popen(params, stderr=subprocess.PIPE)
            if p.wait() != 0:
                print "\t# Error while creating file", i
                return
            
    def startRepos(self):
        print " * Starting ccn_repo on the nodes..." 
        import thread
        
        cv = threading.Condition()
        tmp = copy.deepcopy(self.file_nodes.keys())
        tmp.extend(self.video_nodes)
        all_repo_nodes = set(tmp)
        
        def startRepo(node):
            params = ["ssh",  "viotti@" + node, "ccn_repo", "/home/viotti/repo"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() == 0:
                print "\t* Repo started on", node
            else:
                print "\t# Error while starting repo on", node
            cv.acquire()
            cv.notify()
            cv.release()
                
        for node in all_repo_nodes:
            thread.start_new_thread(startRepo, (node, ))
        
        cv.acquire()
        for node in all_repo_nodes:
            cv.wait()
        cv.release()
                
    
    def stopRepos(self):
        print " * Stopping ccn_repo on the nodes..." 
        tmp = copy.deepcopy(self.file_nodes.keys())
        tmp.extend(self.video_nodes)
        all_repo_nodes = set(tmp)
                
        for node in all_repo_nodes:
            params = ["ssh",  "viotti@" + node, "ccn_repo", "stopall"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() == 0:
                print "\t* Repo stopped on", node
            else:
                print "\t# Error while stopping repo on", node
                
            params = ["ssh",  "viotti@" + node, "rm", "-rf", "repo/"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() != 0:
                print "\t# Error while removing repo directory on", node    
    
         
    def addFilesToRepos(self):
        self._populateFilesAndVideos()
        self._assignFilesToNodes()
        
        # copy videos to the corresponding nodes
        for node in self.video_nodes.keys():
            print " * Copying the videos to {0}...".format(node)
            for f in self.video_nodes[node]: 
                params = ["scp", video_dir + f, "viotti@" + node + ":~"]
                p = subprocess.Popen(params, stdout=subprocess.PIPE)
                if p.wait() != 0:
                    print "\t# Error while copying the video", f, "to", node
                    return    
       
        # add videos to the repositories        
        for node in self.video_nodes.keys():
            print " * Adding videos to the repo of {0}...".format(node)
            for f in self.video_nodes[node]: 
                # ccnputfile [-unversioned] ccnx://path/file.bin /path/to/file.bin
                params = ["ssh",  "viotti@" + node, "ccnputfile", "-unversioned", 
                          "ccnx://" + node + "/" + f, f]
                p = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if p.wait() != 0:
                    print "\t# Error while adding the video", f, "to", node
                    #return
                else:
                    print "\t* {0} added to the repository of {1}".format(f, node)
        
        # copy files to the corresponding nodes
        for node in self.file_nodes.keys():
            print " * Copying the files to {0}...".format(node)
            for f in self.file_nodes[node]: 
                params = ["ssh", node, "ls", f]
                p = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if p.wait() != 0: # if the file does not exist, copy it
                    params = ["scp", files_dir + f, "viotti@" + node + ":~"]
                    p = subprocess.Popen(params, stdout=subprocess.PIPE)
                    if p.wait() != 0:
                        print "\t# Error while copying the file", f, "to", node
                        return    
                
        # add files to the repositories        
        for node in self.file_nodes.keys():
            print " * Adding files to the repo of {0}...".format(node)
            for f in self.file_nodes[node]: 
                # ccnputfile -unversioned ccnx://path/file.bin /path/to/file.bin
                params = ["ssh",  "viotti@" + node, "ccnputfile", "-unversioned", 
                          "ccnx://" + node + "/" + f, f]
                p = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if p.wait() != 0:
                    print "\t# Error while adding the file", f, "to", node
                    return
                else: print "\t* {0} added to the repository of {1}".format(f, node)
                
    def _populateFilesAndVideos(self):
        self.videos = os.listdir(video_dir)
        self.files = os.listdir(files_dir)
        self.files.sort()
        self.videos.sort()
        
        # remove files and videos whose name starts with "." (e.g. ".svn")
        for f in self.files: 
            if f.startswith("."): self.files.remove(f)
        for v in self.videos: 
            if v.startswith("."): self.videos.remove(v)
            
    def _assignFilesToNodes(self):                      
        file_nodes_vec = self.file_nodes.keys()
        file_nodes_vec.sort()
        num_file_nodes = len(file_nodes_vec)
        for i in range(0, len(self.files)):
            self.file_nodes[ file_nodes_vec[i % num_file_nodes] ].append( self.files[i] )
                
        video_nodes_vec = self.video_nodes.keys()
        video_nodes_vec.sort()
        num_video_nodes = len(video_nodes_vec)
        for i in range(0, len(self.videos)):
            self.video_nodes[ video_nodes_vec[i % num_video_nodes] ].append( self.videos[i] )
            
#        print "Files:"
#        for fn in self.file_nodes.keys():
#            print "Node:",fn
#            for f in self.file_nodes[fn]: print f,
#            print 
#        print "\nVideos:"
#        for vn in self.video_nodes.keys():
#            print "Node:",vn
#            for v in self.video_nodes[vn]: print v,
#            print
        
        
    def lstRepo(self):
        print " * Listing the files stored in the repositories..."
        tmp = copy.deepcopy(self.file_nodes.keys())
        tmp.extend(self.video_nodes)
        all_repo_nodes = set(tmp)
                
        for node in all_repo_nodes:
            params = ["ssh",  "viotti@" + node, "ccnlsrepo", "ccnx://" + node]
            p = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.wait() == 0:
                print "\t*", node
                lines = p.stdout.readlines()
                for l in lines:
                    print "\t", l.strip()
                print
            else:
                print "\t# ccnlsrepo returned an error on", node 

            
    def createCCNxRoutingScripts(self, nodes):
        route_template = "ccndc add ccnx:/{0} udp 10.0.0.{1}\n"
        route_template_1 = "ccndc add ccnx:/ udp 10.0.0.{0}\n"
        route_template_keys = "ccndc add ccnx:/ccnx.org udp 10.0.0.{0}\n"
        
        print " * Creating the CCNx routing scripts..."
        for node in self.routing_rules.keys():
            f = open(scripts_dir + node + routing_suffix, 'w')
            f.write("#!/bin/bash\n\n")
            
            if len(self.routing_rules[node]) == 1 and \
                self.routing_rules[node][0].startswith("*root*"):
                temp = self.routing_rules[node][0].split("--")[1]
                f.write(route_template_1.format(nodes[temp].links[node][1]))
            else:
                for line in self.routing_rules[node]:
                    f.write(route_template.format(line, nodes[line].links[node][1]))
                    f.write(route_template_keys.format(nodes[line].links[node][1]))
            f.close()      
            
    def setCCNxRouting(self):
        print " * Setting CCNx routing..."
        for node in self.routing_rules.keys():
            params = ["scp",scripts_dir + node + routing_suffix, "viotti@" + node + ":~"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() != 0:
                print "\t# Error while copying the CCNx routing script to", node
                return
            
            params = ["ssh",  "viotti@" + node, "/bin/bash", node + routing_suffix]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() == 0:
                print "\t* CCNx routing set on", node
            else:
                print "\t# Error while executing the CCNx routing script on", node  
                
    def lstCCNdStatus(self, nodes):
        print " * Listing ccnd status..."
        for node in nodes.keys():          
            params = ["ssh",  "viotti@" + node, "ccndstatus"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() == 0:
                print "\t*", node
                lines = p.stdout.readlines()
                for l in lines:
                    print "\t", l.strip()
                print
            else:
                print "\t# ccndstatus returned an error on", node                
             
    
    def updateCCNx(self, nodes):
        """
        The updateCCNx function perform the following operation:
        
        1. on azteca:
            uninstall CCNx
            remove /home/viotti/ccnx
            git clone repo ccnx on /home/viotti/ccnx
            
        2. on the others:
            uninstall CCNx
            remove /home/viotti/ccnx
            copy ccnx distribution from azteca [because there's no tsocks etc...]
            
        3. on all:
            configure, make, make install
            
        NB: patch about fragmentation or other things should be supplied by hand.         
        """
        
        print " * Updating CCNx on the nodes..."
        
        def clean(node):
            if os.path.isdir(ccnx_dir):
                # make uninstall
                params = ["ssh", "root@"+node, "cd", ccnx_dir, ";make", "uninstall"]
                p = subprocess.Popen(params, stdout=subprocess.PIPE)
                if p.wait() != 0:
                    print "\t# Error while uninstalling CCNx on", node
                    return
                else:
                    #for l in p.stdout.readlines():
                    #    if l != '\n': print "\t\t" + l[:-1]     
                    print "\t* CCNx uninstalled on", node
                    
                # rm -rf /home/viotti/ccnx
                params = ["ssh", "root@"+node, "rm", "-rf", ccnx_dir]
                p = subprocess.Popen(params, stdout=subprocess.PIPE)
                if p.wait() != 0:
                    print "\t# Error while removing CCNx directory on", node
                    return
                else:
                    print "\t* CCNx directory removed on", node
            else:
                print "\t* CCNx directory doesn't exist on", node
  
        clean("azteca")
        
        # git clone on azteca
        params = ["ssh", "viotti@azteca", "tsocks", "git", "clone", ccnx_git_url]
        p = subprocess.Popen(params, stdout=subprocess.PIPE)
        if p.wait() != 0:
            print "\t# Error while cloning CCNx on azteca from the Git repository"
            return
        else:
            for l in p.stdout.readlines():
                if l != '\n': print "\t\t" + l[:-1]     
            print "\t* CCNx cloned on azteca from the Git repository"
        
        # clean (uninstall and remove ccn directory)
        # copy updated version of CCNx from azteca to the other nodes 
        for node in nodes:
            if node != "azteca":
                clean(node)
            
                params = ["scp","-r", ccnx_dir, "viotti@" + node + ":~/ccnx"]
                p = subprocess.Popen(params, stdout=subprocess.PIPE)
                if p.wait() != 0:
                    print "\t# Error while copying CCNx to", node
                    return
                else:
                    print "\t* CCNx copied on", node
                
        # configure, make, make install on all the nodes
        for node in nodes:
            params = ["ssh", "viotti@" + node, "cd", ccnx_dir, ";./configure"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.wait() != 0:
                print "\t# Error while configuring CCNx on", node
                return
            else:  
                print "\t* CCNx configured on", node
                
            params = ["ssh", "viotti@" + node, "cd", ccnx_dir, ";make", "CFLAGS=-O2"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() != 0:
                print "\t# Error while building CCNx on", node
                return
            else:  
                print "\t* CCNx built on", node
                
            params = ["ssh", "root@" + node, "cd", ccnx_dir, ";make", "install"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE)
            if p.wait() != 0:
                print "\t# Error while installing CCNx on", node
                return
            else: 
                print "\t* CCNx installed on", node
                
    # TODO: names of nodes to be resetted are hardcoded
    # the reset script does: stop ccnd, rm cache_log, start ccnd, set CCN routing
    def resetCache(self):
        cache_nodes = ["bird", "p-impact"]
        print " * Restarting CCNx..."
        for node in cache_nodes:
            params = ["scp", scripts_dir + reset_script, "viotti@" + node + ":~"]
            p = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.wait() != 0:
                print "\t# Error while copying the CCNx reset script to", node
                return
            
            params = ["ssh", "viotti@" + node, "/bin/bash", reset_script, ">/dev/null", "2>&1", "&"]
            p = subprocess.Popen(params)
            if p.wait() == 0:
                print "\t* CCNx restarted on", node
            else:
                print "\t# Error while executing the CCNx reset script on", node
                

    def simulate(self):
        import rpy2.robjects as robjects
        
        # generate samples for inter-request times
        inter_script = open(r_scripts_dir + "inter.R",'r').read()
        robjects.r(inter_script)
        print "\tInter-request intervals (mean: {0}):\n\t".format( sum(robjects.r('intervals'))/len(robjects.r('intervals')) ),
        for i in robjects.r('intervals'): print i,
        print
        
        # generate samples for file popularity
        pop_script = open(r_scripts_dir + "pop.R",'r').read()
        robjects.r(pop_script)
        res = [0] * num_files
        #unif_rand = np.random.random_integers(0, tot-1, num_requests)
        tot = 0
        for i in robjects.r('req'):
            #print "\tRequesting object {0}".format(i)
            #print "\tWaiting {0} seconds".format(robjects.r('intervals')[i])
            res[i-1] += 1
            tot += 1
                    
        print "\tRequest frequency of each file (tot: {0}):\t".format(tot)
        for i in res: print i,
        print

    def startTest(self):
        logging.basicConfig(
                filename = "lurch.log",
                filemode = 'w',
                format   = "%(created)f, %(message)s",
                level    = logging.INFO)
            
        print " * Computing the parameters..."       
        #############################################################
        # STEP 1: create parameters of the test
        import rpy2.robjects as robjects
        # generate samples for inter-request times
        inter_script = open(r_scripts_dir + "inter.R",'r').read()
        robjects.r(inter_script)        
        # generate samples for file popularity
        pop_script = open(r_scripts_dir + "pop.R",'r').read()
        robjects.r(pop_script)
        
        num_requests = len(robjects.r('req'))
        
        # If not already done, populate self.files and 
        # assign files to nodes in self.file_node
        if len(self.files) == 0: 
            self._populateFilesAndVideos()
        tot_len = 0
        for n in self.file_nodes.keys(): tot_len += len(self.file_nodes[n])
        if tot_len == 0:
            self._assignFilesToNodes()
            
        toAskFor = []
        # toAskFor: array of (filename, host) to request for download
        #
        # [ [ filename, host ], ... ]
        for i in range(0, num_requests):
            toAskFor.append([ self.files[ robjects.r('req')[i] -1 ], None] )
            for host in self.file_nodes.keys():
                if toAskFor[i][0] in self.file_nodes[host]: 
                    toAskFor[i][1] = host

        testdb = {}
        # testdb: dictionary, used to store test results and statistics
        #
        # { filename: { "host": hostname, "num_dw": num_dw, 
        #               "stat": [ [time, goodput, rtt /*,holes, rtt, rte*/] ],
        #               "stat_avg": [time, goodput, rtt /*,holes, rtt, rte*/] } }
        dws = []    # array of DownloadManager objects
        for i in range(0, num_requests):
            if testdb.has_key(toAskFor[i][0]):
                old_num_dw = testdb[toAskFor[i][0]]["num_dw"]
                testdb.update( {toAskFor[i][0]: {"host": toAskFor[i][1], 
                                                 "num_dw": old_num_dw + 1, 
                                                 "stat": [], "stat_avg": [] } } )
            else:
                testdb.update( {toAskFor[i][0]: {"host": toAskFor[i][1], 
                                                 "num_dw": 1, 
                                                 "stat": [], "stat_avg": [] } } )
            dws.append(DownloadManager(toAskFor[i][0], toAskFor[i][1]))
            
        #import sys
        #sys.setcheckinterval(90)   # set Python thread scheduling granularity every X (Python) instructions
                                    # tradeoff responsiveness vs overhead 
                                    # http://docs.python.org/library/sys.html#sys.setcheckinterval
     
        #############################################################
        # STEP 2: launch the test
        msg = "Starting, {0}, {1}"
        print " * Starting the test..."
        for i in range(0, num_requests):           
            print "\t* [{0}] Starting download of {1} from {2}".format(i+1, toAskFor[i][0], toAskFor[i][1])
            logging.info( msg.format( toAskFor[i][0], int(self.getDownloadCount()) + 1 ) )
            dws[i].start()
            if i != num_requests-1:
                print "\t- Waiting {0} s".format( robjects.r('intervals')[i] )
                #sys.stdout.flush()  # TEMP, to solve sleep issues
                #sys.stdin.flush()   # "
                time.sleep( float(robjects.r('intervals')[i]) )
        print
        
        #############################################################
        # STEP 3: wait for all the downloads to complete
        for dw in dws: 
            dw.join()
            print "\t* {0} joined".format(dw.name)
        
        #############################################################
        # STEP 4: collect and show results
        # fill stats for every download
        print "\t* Filling stats for every download..."
        for i in range(0, num_requests):
            if dws[i].success:
                testdb[dws[i].filename]["stat"].append( [dws[i].download_time, dws[i].goodput, dws[i].rtt] ) 
        
        # compute average values
        print "\t* Computing average values..."
        for file in testdb.keys():
            sum_dt = 0; sum_gp = 0; sum_rtt = 0
            for d in testdb[file]["stat"]:
                sum_dt += d[0]; sum_gp += d[1]; sum_rtt += d[2]
            if len(testdb[file]["stat"]) != 0: # some files are never requested --> not cause "ZeroDivisionError"
                testdb[file]["stat_avg"].append( sum_dt / len(testdb[file]["stat"]) )
                testdb[file]["stat_avg"].append( sum_gp / len(testdb[file]["stat"]) )
                testdb[file]["stat_avg"].append( sum_rtt / len(testdb[file]["stat"]) )
                  
        # save results
        print "\t* Saving results..."
        f = open( results_file, 'w' )
        for filename in self.files:
            if (filename in testdb): 
                if (len( testdb[filename]["stat_avg"] ) != 0):
                    msg = "{0:12} {1:3} {2:10} {3:10} {4}\n".format(filename, 
                                                                    testdb[filename]["num_dw"],
                                                                    testdb[filename]["stat_avg"][0], # time
                                                                    testdb[filename]["stat_avg"][1], # goodput
                                                                    testdb[filename]["stat_avg"][2]) # rtte
                else:
                    msg = "{0:12} NP_err\n".format(filename)
            else:
                msg = "{0:12} NP\n".format(filename)
            f.write(msg)
        f.close()
        
        # dump Python object dataset
        import cPickle as pickle
        outpk = open('data.pkl', 'wb')
        pickle.dump(testdb, outpk, -1) # -1 == pickle.HIGHEST_PROTOCOL
        outpk.close()      
        
        # move cachelogs to local directory
        print "\t* Moving cachelogs to local directory..."
        params = ["bash", "scripts/mv_cachelogs.sh"]
        subprocess.Popen(params)
        
        # dump probability density function of file popularity to file
        f = open( pop_prob_file, 'w' )
        j = 1
        for i in robjects.r('ps'):
            f.write(str(j) + " " + str(i) + "\n")
            j += 1
        f.close()
        
        # compress to a tar.gz file all the log files
        import tarfile
        out = tarfile.open(log_tarfile, mode='w:gz')
        for file in os.listdir(log_dir):
            if file.endswith(".log"):
                out.add(log_dir + file)
                os.remove(log_dir + file)
        out.close()        

        
    def getDownloadCount(self):
        p1 = subprocess.Popen( ["pgrep",  "ccncatchunks2"] , stdout=subprocess.PIPE)
        p2 = subprocess.Popen( ["wc", "-l"] , stdin=p1.stdout, stdout=subprocess.PIPE)
        return p2.communicate()[0].strip()


class DownloadManager(threading.Thread):
            
    def __init__(self, filename, host):
        threading.Thread.__init__(self)
        self.filename = filename
        self.host = host
        self.params = ["ccncatchunks2",  "-s", "-p", parallelism,
                  "ccnx:/" + self.host + "/" + self.filename, ">", "/dev/null"]
        #gnome-terminal -x ccncatchunks2 -s -p 10 ccnx:/path/file > /dev/null
        #params = ["gnome-terminal", "-x", "ccncatchunks2",  "-s", "-p", str(parallelism),
        #      "ccnx:/" + self.host + "/" + self.filename, ">","/dev/null"]
        
    def getDownloadCount(self):
        p1 = subprocess.Popen( ["pgrep",  "ccncatchunks2"] , stdout=subprocess.PIPE)
        p2 = subprocess.Popen( ["wc", "-l"] , stdin=p1.stdout, stdout=subprocess.PIPE)
        return p2.communicate()[0].strip()
    
    def dumpLogToFile(self, lines):
        # decide log file name
        i = 0
        logfilename =  log_dir + self.filename + "_" + str(i) + "_.log"
        while os.path.isfile(logfilename):
            i += 1
            logfilename =  log_dir + self.filename + "_" + str(i) + "_.log"
            
        # dump stderr of the download to file
        f = open(logfilename, "w")
        for l in lines: f.write(l)
        f.close()
        
    def run(self):
        p = subprocess.Popen(self.params, stderr=subprocess.PIPE) # shell=True requires escaping backslash and spaces
        start = time.time()   
        #while p.poll() == None:      # if the process is not terminated - TEMP
        #    time.sleep(0.0001)       # yield to other threads
        #if p.returncode == 0:   # instead of "if p.wait() == 0", for sleep issues
        if p.wait() == 0:      
            self.download_time = time.time() - start                # s
            self.goodput = ( file_size / self.download_time ) * 8   # bps
            self.success = True 
            lines = p.stderr.readlines()
            
            if "transferred" in lines[-2]:  # if ccncatchunks2 produced the final report line, use it (often it doesn't)
                self.download_time = float( lines[-2].split()[6] )
                self.goodput = float( lines[-2].split()[8][1:] ) * 8
            elif "transferred" in lines[-1]:
                self.download_time = float( lines[-1].split()[6] )
                self.goodput = float( lines[-1].split()[8][1:] ) * 8
                
            i = -1
            while "rtte" not in lines[i]: i -= 1    # seeks the last rtte measurement in the log
            self.rtt = int( lines[i].split()[-2] )
            
            # goodput: bps, time: s, rtte: us
            ok_msg = "Completed, {0}, {1}, {2}, {3}, {4}".format(self.filename,
                                                                self.goodput,
                                                                self.download_time,
                                                                self.rtt,
                                                                self.getDownloadCount())
            logging.info(ok_msg)
            self.dumpLogToFile(lines)
            
        else:
            self.download_time = time.time() - start 
            self.success = False
            lines = p.stderr.readlines()
            
            ko_msg = "Failed, {0}, '{1}', {2}, {3}".format(self.filename, 
                                                             lines[-1].strip(),
                                                             self.download_time,
                                                             self.getDownloadCount())
            logging.error(ko_msg)
            self.dumpLogToFile(lines)       
            print "\t#", ko_msg
