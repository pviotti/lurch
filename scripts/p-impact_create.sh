#!/bin/bash

sysctl -w net.ipv4.ip_forward=1
modprobe ipip

iptunnel add tap2 mode ipip local 10.193.163.176 remote 10.193.163.120
ifconfig tap2 10.0.0.5 netmask 255.255.255.255 up
route add 10.0.0.2 tap2

iptunnel add tap0 mode ipip local 10.193.163.176 remote 10.193.163.130
ifconfig tap0 10.0.0.3 netmask 255.255.255.255 up
route add 10.0.0.1 tap0
tc qdisc add dev tap0 root handle 1: htb default 1
tc class add dev tap0 parent 1: classid 1:1 htb rate 5mbit ceil 5mbit
tc qdisc add dev tap0 parent 1:1 handle 20: ccnsfq limit 20

iptunnel add tap1 mode ipip local 10.193.163.176 remote 10.193.163.128
ifconfig tap1 10.0.0.4 netmask 255.255.255.255 up
route add 10.0.0.6 tap1

