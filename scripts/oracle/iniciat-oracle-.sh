#!/bin/sh

sudo su -
apt update -y &&  apt upgrade -y 
apt install nginx -y 
iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
iptables -I INPUT 6 -m state --state NEW -p tcp --dport 3000 -j ACCEPT
netfilter-persistent save
cd /usr/local/src/ && wget https://www.noip.com/client/linux/noip-duc-linux.tar.gz && tar xzf noip-duc-linux.tar.gz