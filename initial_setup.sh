#!/bin/bash
apt-get update
sudo apt-get install -y can-utils
sudo apt install -y net-tools
sudo apt-get install -y gawk
cd container
docker build -t geargoat .
 
 
 