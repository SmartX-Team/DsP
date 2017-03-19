#!/bin/bash
apt install -y software-properties-common
add-apt-repository -y cloud-archive:ocata
apt update && apt -y dist-upgrade
apt -y install python-openstackclient
