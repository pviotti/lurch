#!/bin/bash

modprobe ipip

iptunnel add tap0 mode ipip local 10.193.163.120 remote 10.193.163.176
ifconfig tap0 10.0.0.2 netmask 255.255.255.255 up
route add -net 10.0.0.0/24 tap0

