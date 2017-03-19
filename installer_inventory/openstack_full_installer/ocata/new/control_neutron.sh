#/!bin/bash

if [ ! -f ./admin-openrc ]; then
echo "export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=$ADMIN_PASS
export OS_AUTH_URL=http://$CTRL_IP:35357/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2" > ./admin-openrc
fi


## DB Configuration
mysql -uroot -p${MYSQL_PASS} -e "CREATE DATABASE neutron;"
mysql -uroot -p${MYSQL_PASS} -e "GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY '$NEUTRON_DBPASS';"
mysql -uroot -p${MYSQL_PASS} -e "GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY '$NEUTRON_DBPASS';"

openstack user create --domain default --password $NEUTRON_PASS neutron
openstack role add --project service --user neutron admin
openstack service create --name neutron --description "OpenStack Networking" network

openstack endpoint create --region $REGION_ID network public http://$MGMT_IP:9696
openstack endpoint create --region $REGION_ID network internal http://$CTRL_IP:9696
openstack endpoint create --region $REGION_ID network admin http://$CTRL_IP:9696




if [ "$NEUTRON_MECHANISM_DRIVER" == "linuxdriver" ]; then

apt install -y neutron-server neutron-plugin-ml2 neutron-linuxbridge-agent neutron-l3-agent neutron-dhcp-agent neutron-metadata-agent

## neutron.conf configuration
sed -i "s/^core_plugin.*//" /etc/neutron/neutron.conf
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
service_plugins = router\n\
allow_overlapping_ips = true\n\
core_plugin = ml2\n\
auth_strategy = keystone\n\
rpc_backend = rabbit\n\
notify_nova_on_port_status_changes = true\n\
notify_nova_on_port_data_changes = true/"/etc/neutron/neutron.conf

sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
transport_url = rabbit:\/\/openstack:$RABBIT_PASS@$CTRL_IP/"/etc/neutron/neutron.conf

sed -i "s/^connection =.*/connection = mysql+pymysql:\/\/neutron:$NEUTRON_DBPASS@$CTRL_IP\/neutron/" /etc/neutron/neutron.conf

sed -i "s/^\[keystone_authtoken\]/\[keystone_authtoken\]\n\
auth_uri = http:\/\/$CTRL_IP:5000\n\
auth_url = http:\/\/$CTRL_IP:35357\n\
memcached_servers = $CTRL_IP:11211\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
project_name = service\n\
username = neutron\n\
password = $NEUTRON_PASS/" /etc/neutron/neutron.conf

sed -i "s/^\[oslo_messaging_rabbit\]/\[oslo_messaging_rabbit\]\n\
rabbit_host = $CTRL_IP\n\
rabbit_userid = openstack\n\
rabbit_password = $RABBIT_PASS/" /etc/neutron/neutron.conf

sed -i "s/^\[nova\]/\[nova\]\n\
auth_url = http:\/\/$CTRL_IP:35357\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
region_name = $REGION_ID\n\
project_name = service\n\
username = nova\n\
password = $NOVA_PASS/" /etc/neutron/neutron.conf

## linuxbridge_agent.ini configuration
EXTERNAL_INTERFACE=`ip route | grep $MGMT_IP | awk '{print $3}'`
sed -i "s/^\[linux_bridge\]/\[linux_bridge\]\nphysical_interface_mappings = provider:$EXTERNAL_INTERFACE/" /etc/neutron/plugins/ml2/linuxbridge_agent.ini

sed -i "s/^\[vxlan\]/\[vxlan\]\n\
enable_vxlan = true\n\
local_ip = $DATA_IP\n\
l2_population = true/" /etc/neutron/plugins/ml2/linuxbridge_agent.ini

sed -i "s/^\[securitygroup\]/\[securitygroup\]\n\
enable_security_group = True\n\
firewall_driver = iptables/" /etc/neutron/plugins/ml2/linuxbridge_agent.ini

## ml2_conf.ini configuration	
sed -i "s/^\[ml2\]/\[ml2\]\n\
type_drivers = flat,vlan,vxlan\n\
tenant_network_types = vxlan\n\
mechanism_drivers = linuxbridge,l2population\n\
extension_drivers = port_security/" /etc/neutron/plugins/ml2/ml2_conf.ini
#sed -i "s/^\[ml2_type_flat\]/\[ml2_type_flat\]\nflat_networks = provider/" /etc/neutron/plugins/ml2/ml2_conf.ini
sed -i "s/^\[ml2_type_vxlan\]/\[ml2_type_vxlan\]\nvni_ranges = 1:1000/" /etc/neutron/plugins/ml2/ml2_conf.ini
sed -i "s/^\[securitygroup\]/\[securitygroup\]\nenable_ipset = true/" /etc/neutron/plugins/ml2/ml2_conf.ini

## l3_agent.ini configuration
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
interface_driver = linuxbridge\n\
external_network_bridge = /" /etc/neutron/l3_agent.ini

## dhcp_agent.ini configuration
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
interface_driver = linuxbridge\n\
dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq\n\
enable_isolated_metadata = true/" /etc/neutron/dhcp_agent.ini





elif [ "$NEUTRON_MECHANISM_DRIVER" == "openvswitch" ]; then
apt install -y neutron-server neutron-plugin-ml2 neutron-openvswitch-agent neutron-l3-agent neutron-dhcp-agent neutron-metadata-agent

### Control Node
## neutron.conf configuration
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
service_plugins = router\n\
allow_overlapping_ips = true/" /etc/neutron/neutron.conf

## ml2_conf.ini configuration   
sed -i "s/^\[ml2\]/\[ml2\]\n\
type_drivers = flat,vlan,vxlan\n\
tenant_network_types = vxlan\n\
mechanism_drivers = openvswitch,l2population\n\
extension_drivers = port_security/" /etc/neutron/plugins/ml2/ml2_conf.ini
sed -i "s/^\[ml2_type_flat\]/\[ml2_type_flat\]\nflat_networks = external/" /etc/neutron/plugins/ml2/ml2_conf.ini
sed -i "s/^\[ml2_type_vxlan\]/\[ml2_type_vxlan\]\nvni_ranges = 1:1000/" /etc/neutron/plugins/ml2/ml2_conf.ini
sed -i "s/^\[securitygroup\]/\[securitygroup\]\nfirewall_driver = iptables_hybrid/" /etc/neutron/plugins/ml2/ml2_conf.ini

### Network Node
## neutron.conf configuration
sed -i "s/^core_plugin.*//" /etc/neutron/neutron.conf
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
core_plugin = ml2\n\
auth_strategy = keystone\n\
rpc_backend = rabbit\n\
notify_nova_on_port_status_changes = true\n\
notify_nova_on_port_data_changes = true/" /etc/neutron/neutron.conf

sed -i "s/^connection =.*/connection = mysql+pymysql:\/\/neutron:$NEUTRON_DBPASS@$CTRL_IP\/neutron/" /etc/neutron/neutron.conf

sed -i "s/^\[keystone_authtoken\]/\[keystone_authtoken\]\n\
auth_uri = http:\/\/$CTRL_IP:5000\n\
auth_url = http:\/\/$CTRL_IP:35357\n\
memcached_servers = $CTRL_IP:11211\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
project_name = service\n\
username = neutron\n\
password = $NEUTRON_PASS/" /etc/neutron/neutron.conf

sed -i "s/^\[oslo_messaging_rabbit\]/\[oslo_messaging_rabbit\]\n\
rabbit_host = $CTRL_IP\n\
rabbit_userid = openstack\n\
rabbit_password = $RABBIT_PASS/" /etc/neutron/neutron.conf

sed -i "s/^\[nova\]/\[nova\]\n\
auth_url = http:\/\/$CTRL_IP:35357\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
region_name = $REGION_ID\n\
project_name = service\n\
username = nova\n\
password = $NOVA_PASS/" /etc/neutron/neutron.conf


## openvswitch_agent.ini configuration
ovs-vsctl add-br br-ex

sed -i "s/^\[ovs\]/\[ovs\]\n\
bridge_mappings = external:br-ex\n\
local_ip=$DATA_IP/" /etc/neutron/plugins/ml2/openvswitch_agent.ini

sed -i "s/^\[agent\]/\[agent\]\n\
tunnel_types = vxlan\n\
l2_population = true/" /etc/neutron/plugins/ml2/openvswitch_agent.ini

sed -i "s/^\[securitygroup\]/\[securitygroup\]\nfirewall_driver = iptables_hybrid/" /etc/neutron/plugins/ml2/openvswitch_agent.ini

## l3_agent.ini configuration
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
interface_driver = openvswitch\n\
external_network_bridge =/" /etc/neutron/l3_agent.ini


### DVR configuration
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\nrouter_distributed = true/" /etc/neutron/neutron.conf
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\nenable_distributed_routing = true/" /etc/neutron/plugins/ml2/openvswitch_agent.ini
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\nagent_mode = dvr_snat/" /etc/neutron/l3_agent.ini

ifconfig br-ex up
ifconfig br-int up
ifconfig br-tun up

fi





## metadata_agent.ini configuration
sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
nova_metadata_ip = $CTRL_IP\n\
metadata_proxy_shared_secret = $METADATA_SECRET/" /etc/neutron/metadata_agent.ini

sed -i "s/^\[neutron\]/\[neutron\]\n\
url = http:\/\/$CTRL_IP:9696\n\
auth_url = http:\/\/$CTRL_IP:35357\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
region_name = $REGION_ID\n\
project_name = service\n\
username = neutron\n\
password = $NEUTRON_PASS\n\
service_metadata_proxy = true\n\
metadata_proxy_shared_secret = $METADATA_SECRET/" /etc/nova/nova.conf

su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron

## Restart services
service nova-api restart
service neutron-server restart
service neutron-dhcp-agent restart
service neutron-metadata-agent restart
service neutron-l3-agent restart

if [ "$NEUTRON_MECHANISM_DRIVER" == "linuxbridge" ]; then
service neutron-linuxbridge-agent restart
elif [ "$NEUTRON_MECHANISM_DRIVER" == "openvswitch" ]; then
service openvswitch-switch restart
service neutron-openvswitch-agent restart
fi
