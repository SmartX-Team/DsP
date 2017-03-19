#!/bin/bash

apt install -y chrony
sed -i "s/^server/#server/g" /etc/chrony/chrony.conf
sed -i "s/^pool/#pool/g" /etc/chrony/chrony.conf
echo "server ${CONTROL_CTRL_IP} iburst" >> /etc/chrony/chrony.conf
service chrony restart
