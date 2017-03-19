#!/bin/bash

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

source openstack_settings.cfg

bash update_apt.sh
bash compute_env_software.sh
bash compute_nova.sh
bash compute_neutron.sh
