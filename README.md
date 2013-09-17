**Lurch** is a tool I wrote for simplifying and automating the testing of 
[CCNx][1] performance over a small park of machines.  
It was developed in _2010_, 
as a collateral effort for my M.Sc. thesis in computers and 
communication networks at [PoliTo][2] and [Telecom ParisTech][3], during 
a six months intership at [Orange Labs][4].  

An improved version of this tool has been used for large scale experimental deployments
as explained in [this][5] CCNxCon presentation.

For results obtained using Lurch, please refer to [my M.Sc. thesis][6].


[1]: http://www.ccnx.org/
[2]: http://www.polito.it/
[3]: http://www.telecom-paristech.fr
[4]: http://www.orange.com/en/innovation/research
[5]: http://www.ccnx.org/wp-content/uploads/2013/07/CCNDeployment_6_Carofiglio.ppt
[6]: http://perso.rd.francetelecom.fr/muscariello/MS-thesis-viotti.pdf


### Features

 * monitor connectivity (issuing commands like ping, ifconfig, route)
 * setup routing using IP tunnels
 * manage `ccnd` and `ccn_repo`
 * update the CCNx distribution from the Git repository
 * generate and add file to the repository
 * simulate a download test, i.e. generate popularity and inter-request time samples
 * start download tests using `ccncatchunks2` ~~and the CCNx VLC plugin~~
 * collect tests' results

 
Lurch's help command:

```
Lurch > help

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
```

How-to help message:

```
Lurch > howto

  * Brief guided tour of the functions of Lurch:
        0) fill the configuration file (lurch.conf) and start lurch
        1) verify nodes connectivity --> ping, list, tunnel, ifconf
        2) create and execute tunnel scripts --> script, lcreate
        3) start ccnd and the repositories --> startccn, startrepo
        4) configure ccnx routing --> routeccn
        5) add files to repositories --> addrepo
        6) start download test --> start
```

Batch usage help:

```
Usage: python lurch.py [-s|-t|-r]
        -r: restart ccnd before a new test
        -s: simulate
        -t: start test
```

To change the parameters regarding popularity and inter-arrival times 
`r-scripts/inter.R` and `r-scripts/pop.R` should be edited.
In particular *n_req* in `pop.R` must be equal to *num_intervals*  in `inter.R`.  

To change the network topology edit `lurch.conf` and apply the setting using *script* and *lcreate* Lurch commands.
Few other parameters are hardcoded in the first lines of file `lurch/CCNxManager.py` and `lurch/NetworkManager.py`.  

Results of tests consist in these files:

 * `lurch.log` - main application log
 * `logs.tar.gz` - archive containing single download log files
 * `pop_prob.in` - a posteriori statistics about popularity
 * `results.in` - statistics about throughput

Process these files using `graphs.sh` and `convert_time.py` scripts located in `_processing/`.
Then use `pop_gp.dat` obtained in the previous step to plot graphs about throughput vs popularity.


### Requirements

 * Python 2.6+
 * CCNx 0.2.0
 * R (in Ubuntu: `sudo apt-get install r-base r-vgam`)
 * `rpy2` and `numpy` Python libraries (in Ubuntu: `sudo apt-get install python-rpy2 python-numpy`)
 * some basic Linux network utilities such as `ping`, `ifconfig`, `route` and `iptunnel`
 
 
### Distribution

 * `files/` - contains dummy files generated by Lurch to be added to the repository
 * `video/` - contains the video files to be added to the repository
 * `scripts/` - contains the bash scripts created by Lurch to set the network topology and the CCNx routing
 * `r-scripts/` - R language scripts executed to sample inter-request and popularity values
 * `log/` - contains the log files collected during the test
 * `lurch/` - contains the two modules of Lurch: NetworkManager and CCNxManager
 * `lurch.conf` - configuration file, to be edited by hand before starting Lurch
 * `lurch.py` - Lurch main script file
 
 
### Known bugs

There may be quite a few bugs or, most likely, hardcoded settings, 
as this was a personal tool I coded just for speeding up my tests setups.  


### License

Copyright 2010 Paolo Viotti.  (name.surname at gmail)
Licensed under the **Apache License**, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at  http://www.apache.org/licenses/LICENSE-2.0.  
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
