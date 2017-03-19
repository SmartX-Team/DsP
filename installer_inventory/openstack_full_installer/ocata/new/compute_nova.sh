#!/bin/bash

apt install -y nova-compute

sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
transport_url = rabbit:\/\/openstack:$RABBIT_PASS@$CONTROL_CTRL_IP/" /etc/nova/nova.conf

sed -i "s/^#auth_strategy.*/auth_strategy = keystone/" /etc/nova/nova.conf
sed -i "s/^\[keystone_authtoken\]/\[keystone_authtoken\]\n\
auth_uri = http:\/\/$CONTROL_CTRL_IP:5000\n\
auth_url = http:\/\/$CONTROL_CTRL_IP:35357\n\
memcached_servers = $CONTROL_CTRL_IP:11211\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
project_name = service\n\
username = nova\n\
password = $NOVA_PASS/" /etc/nova/nova.conf

sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
my_ip = $CTRL_IP\n\
use_neutron = True\n\
firewall_driver = nova.virt.firewall.NoopFirewallDriver/" /etc/nova/nova.conf

sed -i "s/^\[vnc\]/\[vnc\]\n\
enable = true\n\
vncserver_listen = 0.0.0.0\n\
vncserver_proxyclient_address = \$my_ip/" /etc/nova/nova.conf

#sed -i "s/^\[vnc\]/\[vnc\]\n\
#vncserver_listen = \$my_ip/" /etc/nova/nova.conf

#The below is only an additional part in Compute Node
sed -i "s/^\[vnc\]/\[vnc\]\n\
novncproxy_base_url = http:\/\/$CONTROL_MGMT_IP:6080\/vnc_auto.html/" /etc/nova/nova.conf

sed -i "s/^\[glance\]/\[glance\]\n\
api_servers = http:\/\/$CONTROL_CTRL_IP:9292/" /etc/nova/nova.conf

sed -i "s/^lock_path=.*/lock_path = \/var\/lib\/nova\/tmp\//" /etc/nova/nova.conf

NUM=`egrep -c '(vmx|svm)' /proc/cpuinfo`
if [ $NUM = 0 ]
then
 echo "here"
 sed -i "s/virt_type=kvm/virt_type=qemu/g" /etc/nova/nova-compute.conf
fi

service nova-compute restart
