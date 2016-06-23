#!/bin/bash
TARGET_PATH="${HOME}/dsp_installer/dsp_installer"

cd ${TARGET_PATH}
rm -f *_ubuntu*.sh *_openstack*.sh local.conf* *wsgi-keystone* *client.py
sudo rm -f /home/tein/dsp_installer/maasrepo/scripts/* 
