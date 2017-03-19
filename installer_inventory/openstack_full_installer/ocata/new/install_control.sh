#!/bin/bash

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

source openstack_settings.cfg
bash ./update_apt.sh
bash ./control_env_software.sh
bash ./keystone.sh
bash ./glance.sh
bash ./control_nova.sh
bash ./control_neutron.sh
