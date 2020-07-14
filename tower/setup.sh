#!/bin/bash

apt-get update -y
apt-get install pip -y
pip install -e requirement.txt
pip install ./post_interface/
