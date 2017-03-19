#!/bin/bash

if [ "$NEUTRON_MECHANISM_DRIVER" == "linuxbridge" ]; then
## linuxbridge_agent.ini configuration
apt install -y neutron-liinuxbridge-agent

## neutron.conf configuration
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
rpc_backend = rabbit\n\
auth_strategy = keystone/" /etc/neutron/neutron.conf

sed -i "s/^\[oslo_messaging_rabbit\]/\[oslo_messaging_rabbit\]\n\
rabbit_host = $CONTROL_CTRL_IP\n\
rabbit_userid = openstack\n\
rabbit_password = $RABBIT_PASS/" /etc/neutron/neutron.conf

sed -i "s/^\[keystone_authtoken\]/\[keystone_authtoken\]\n\
auth_uri = http:\/\/$CONTROL_CTRL_IP:5000\n\
auth_url = http:\/\/$CONTROL_CTRL_IP:35357\n\
memcached_servers = $CONTROL_CTRL_IP:11211\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
project_name = service\n\
username = neutron\n\
password = $NEUTRON_PASS/" /etc/neutron/neutron.conf

PROVIDER_INTERFACE_NAME=`ip route | grep $MGMT_IP | awk '{print $3}'`
sed -i "s/^\[linux_bridge\]/\[linux_bridge\]\nphysical_interface_mappings = provider:$PROVIDER_INTERFACE_NAME/" /etc/neutron/plugins/ml2/linuxbridge_agent.ini

sed -i "s/^\[vxlan\]/\[vxlan\]\n\
enable_vxlan = True\n\
local_ip = $DATA_IP\n\
l2_population = True/" /etc/neutron/plugins/ml2/linuxbridge_agent.ini

sed -i "s/^\[securitygroup\]/\[securitygroup\]\n\
enable_security_group = True
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver/" /etc/neutron/plugins/ml2/linuxbridge_agent.ini





elif [ "$NEUTRON_MECHANISM_DRIVER" == "openvswitch" ]; then
sudo apt-get install -y neutron-plugin-ml2 neutron-plugin-openvswitch-agent neutron-l3-agent

## neutron.conf configuration
sed -i "s/^core_plugin.*//" /etc/neutron/neutron.conf
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
core_plugin = ml2\n\
auth_strategy = keystone/" /etc/neutron/neutron.conf

sed -i "s/^connection =.*/connection = mysql+pymysql:\/\/neutron:$NEUTRON_DBPASS@$CONTROL_CTRL_IP\/neutron/" /etc/neutron/neutron.conf

sed -i "s/^\[keystone_authtoken\]/\[keystone_authtoken\]\n\
auth_uri = http:\/\/$CONTROL_CTRL_IP:5000\n\
auth_url = http:\/\/$CONTROL_CTRL_IP:35357\n\
memcached_servers = $CONTROL_CTRL_IP:11211\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
project_name = service\n\
username = neutron\n\
password = $NEUTRON_PASS/" /etc/neutron/neutron.conf

sed -i "s/^\[oslo_messaging_rabbit\]/\[oslo_messaging_rabbit\]\n\
rabbit_host = $CONTROL_CTRL_IP\n\
rabbit_userid = openstack\n\
rabbit_password = $RABBIT_PASS/" /etc/neutron/neutron.conf

sed -i "s/^\[nova\]/\[nova\]\n\
auth_url = http:\/\/$CONTROL_CTRL_IP:35357\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
region_name = $REGION_ID\n\
project_name = service\n\
username = nova\n\
password = $NOVA_PASS/" /etc/neutron/neutron.conf

## openvswitch_agent.ini configuration
sed -i "s/^\[ovs\]/\[ovs\]\n\
bridge_mappings = external:br-ex\n\
local_ip=$DATA_IP/" /etc/neutron/plugins/ml2/openvswitch_agent.ini

sed -i "s/^\[securitygroup\]/\[securitygroup\]\nfirewall_driver = iptables_hybrid/" /etc/neutron/plugins/ml2/openvswitch_agent.ini
sed -i "s/^\[agent\]/\[agent\]\n\
tunnel_types = vxlan\n\
l2_population = true/" /etc/neutron/plugins/ml2/openvswitch_agent.ini

## dhcp_agent.ini configuration
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
interface_driver = openvswitch\n\
enable_isolated_metadata = true/" /etc/neutron/dhcp_agent.ini

## metadata_agent.ini configuration
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
nova_metadata_ip = $CONTROL_CTRL_IP\n\
metadata_proxy_shared_secret = $METADATA_SECRET/" /etc/neutron/metadata_agent.ini

## DVR configuration
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\nenable_distributed_routing = True/" /etc/neutron/plugins/ml2/openvswitch_agent.ini

sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
interface_driver = openvswitch\n\
external_network_bridge =\n\
agent_mode = dvr/" /etc/neutron/l3_agent.ini


EXTERNAL_INTERFACE=`ip route | grep $MGMT_IP | awk '{print $3}'`
ovs-vsctl add-br br-ex
#ovs-vsctl add-port br-ex $EXTERNAL_INTERFACE
fi

## nova.conf configuration
sed -i "s/^\[neutron\]/\[neutron\]\n\
url = http:\/\/$CONTROL_CTRL_IP:9696\n\
auth_url = http:\/\/$CONTROL_CTRL_IP:35357\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
region_name = $REGION_ID\n\
project_name = service\n\
username = neutron\n\
password = $NEUTRON_PASS/" /etc/nova/nova.conf

service nova-compute restart
service neutron-metadata-agent restart

if [ "$NEUTRON_MECHANISM_DRIVER" == "linuxdriver" ]; then
service neutron-linuxbridge-agent restart
elif [ "$NEUTRON_MECHANISM_DRIVER" == "openvswitch" ]; then
service neutron-l3-agent restart
service neutron-openvswitch-agent restart

ifconfig br-ex up
ifconfig br-int up
ifconfig br-tun up
fi
