#!/bin/bash

## Download and set Devstack to install OpenStack ##
cd ~
git clone https://git.openstack.org/openstack-dev/devstack
cd devstack
git checkout stable/juno
wget -O ./local.conf http://210.114.90.8/MAAS/static/maasrepo/postscripts/service/local.conf.$(hostname)

## To configure a created VMs MTU ##
echo "dhcp-option-force=26,1440" > dnsmasq-neutron.conf

## For access from external network to a VM ##
sudo bash -c 'echo "net.ipv4.conf.eth0.proxy_arp = 1" >> /etc/sysctl.conf'
sudo bash -c 'echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf'
sudo sysctl -p

## Make a script for easy reinstallation
echo "./stack.sh" > one_touch_stack.sh

HOST_MGMT_IP=`cat local.conf | grep HOST_IP= | sed "s/HOST_IP=//g"`
#echo "sudo ifdown eth0" >> one_touch_stack.sh
#echo 'sudo sed -i "s/eth0/br-ex/g" /etc/network/interfaces'  >> one_touch_stack.sh
#echo 'sudo ifconfig br-ex 0.0.0.0 down'  >> one_touch_stack.sh
#echo 'sudo ifup br-ex'  >> one_touch_stack.sh
#echo 'sudo ifconfig eth0 up'  >> one_touch_stack.sh
#echo 'sudo ovs-vsctl add-port br-ex eth0'  >> one_touch_stack.sh

#echo 'source openrc demo demo' >> one_touch_stack.sh
#echo 'neutron router-interface-delete router1 private-subnet'  >> one_touch_stack.sh
#echo 'neutron router-delete router1'  >> one_touch_stack.sh
#echo 'neutron router-create router1'  >> one_touch_stack.sh
echo 'source openrc admin demo' >> one_touch_stack.sh
#echo "neutron subnet-update --gateway `echo $HOST_MGMT_IP` public-subnet" >> one_touch_stack.sh
#echo 'neutron router-gateway-set router1 public' >> one_touch_stack.sh
#echo 'neutron router-interface-add router1 private-subnet' >> one_touch_stack.sh

echo "sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE" >> one_touch_stack.sh
echo "source /home/stack/devstack/openrc demo demo" >> one_touch_stack.sh
echo "neutron subnet-update --dns-nameserver 8.8.8.8 private-subnet" >> one_touch_stack.sh
echo 'neutron security-group-rule-create --direction ingress --protocol tcp --port_range_min 1 --port_range_max 65535 default' >> one_touch_stack.sh
echo 'neutron security-group-rule-create --direction egress --protocol tcp --port_range_min 1 --port_range_max 65535 default' >> one_touch_stack.sh
echo 'neutron security-group-rule-create --direction egress --protocol udp --port_range_min 1 --port_range_max 65535 default' >> one_touch_stack.sh
echo 'neutron security-group-rule-create --direction ingress --protocol udp --port_range_min 1 --port_range_max 65535 default' >> one_touch_stack.sh
echo 'neutron security-group-rule-create --direction ingress --protocol icmp default' >> one_touch_stack.sh
echo 'neutron security-group-rule-create --direction egress --protocol icmp default' >> one_touch_stack.sh


echo 'source /home/stack/devstack/openrc admin demo' >> one_touch_stack.sh
echo 'keystone user-role-add --user demo --tenant-id demo --role-id admin' >> one_touch_stack.sh
echo 'nova quota-class-update --instance 1000 --cores 10000 --ram 5120000 default' >> one_touch_stack.sh

bash one_touch_stack.sh
chmod 744 one_touch_stack.sh
