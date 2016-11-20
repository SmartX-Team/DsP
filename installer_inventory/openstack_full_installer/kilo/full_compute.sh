#!/bin/bash

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi


COMPUTE_M_IP='<COMPUTE_MGMT_IP>'
COMPUTE_M_MAC='<COMPUTE_MGMT_MAC>'
COMPUTE_D_IP='<COMPUTE_DATA_IP>'
CONTROLLER_EXT_IP='<CONTROLLER_MGMT_IP>'
CONTROLLER_M_IP='<CONTROLLER_CTRL_IP>'
PASSWORD='<ADMIN_PASSWORD>'

MGMT_INTERFACE=$(ifconfig -a | grep $COMPUTE_M_MAC | awk '{print $1}')


######################### Update Packages ####################

apt-get install ubuntu-cloud-keyring
echo "deb http://ubuntu-cloud.archive.canonical.com/ubuntu trusty-updates/kilo main" > /etc/apt/sources.list.d/cloudarchive-kilo.list

apt-get update && apt-get -y dist-upgrade


####################### Install Nova Part ########################

sudo apt-get install -y nova-compute sysfsutils


Nova=`dpkg -l | grep nova-api`

if [ "$Nova" == "" ]; then

sed -i "/enabled_apis=ec2,osapi_compute,metadata/a\rpc_backend = rabbit\n\
auth_strategy = keystone\n\
my_ip = $COMPUTE_M_IP\n\
vnc_enabled = True\n\
vncserver_listen = 0.0.0.0\n\
vncserver_proxyclient_address = $COMPUTE_M_IP\n\
novncproxy_base_url = http://$CONTROLLER_EXT_IP:6080/vnc_auto.html\n\n\
[oslo_messaging_rabbit]\n\
rabbit_host = $CONTROLLER_M_IP\n\
rabbit_userid = openstack\n\
rabbit_password = $PASSWORD\n\n\
[keystone_authtoken]\n\
auth_uri = http:\/\/$CONTROLLER_M_IP:5000\n\
auth_url = http:\/\/$CONTROLLER_M_IP:35357\n\
auth_plugin = password\n\
project_domain_id = default\n\
user_domain_id = default\n\
project_name = service\n\
username = nova\n\
password = $PASSWORD\n\n\
[glance]\n\
host = $CONTROLLER_M_IP\n\n\
[oslo_concurrency]\n\
lock_path = \/var\/lib\/nova\/tmp" /etc/nova/nova.conf
fi

service nova-compute restart


rm -f /var/lib/nova/nova.sqlite


######################### Installl Neutron Part ########################

sed -i "/#kernel.domainname = example.com/a\
net.ipv4.ip_forward=1\n\
net.ipv4.conf.all.rp_filter=0\n\
net.ipv4.conf.default.rp_filter=0" /etc/sysctl.conf





Neutron=`dpkg -l | grep neutron-server`

if [ "$Neutron" == "" ]; then

  apt-get install -y neutron-plugin-ml2 neutron-plugin-openvswitch-agent neutron-l3-agent

  ################### neutron.conf

  sed -i "s/# router_distributed = False/router_distributed = True/g" /etc/neutron/neutron.conf
  sed -i "s/# rpc_backend=rabbit/rpc_backend = rabbit/g" /etc/neutron/neutron.conf
  sed -i "s/# rabbit_host = localhost/rabbit_host = $CONTROLLER_M_IP/g" /etc/neutron/neutron.conf
  sed -i "s/# rabbit_userid = guest/rabbit_userid = openstack/g" /etc/neutron/neutron.conf
  sed -i "s/# rabbit_password = guest/rabbit_password = $PASSWORD/g" /etc/neutron/neutron.conf
  sed -i "s/# auth_strategy = keystone/auth_strategy = keystone/g" /etc/neutron/neutron.conf
  sed -i "s/auth_uri = http:\/\/127.0.0.1:35357\/v2.0\//auth_uri = http:\/\/$CONTROLLER_M_IP:5000/g" /etc/neutron/neutron.conf
  sed -i "s/identity_uri = http:\/\/127.0.0.1:5000/auth_url = http:\/\/$CONTROLLER_M_IP:35357\n\
auth_plugin = password\n\
project_domain_id = default\n\
user_domain_id = default/g" /etc/neutron/neutron.conf
  sed -i "s/admin_tenant_name = %SERVICE_TENANT_NAME%/project_name = service/g" /etc/neutron/neutron.conf
  sed -i "s/admin_user = %SERVICE_USER%/username = neutron/g" /etc/neutron/neutron.conf
  sed -i "s/admin_password = %SERVICE_PASSWORD%/password = $PASSWORD/g" /etc/neutron/neutron.conf
  sed -i "s/# service_plugins =/service_plugins = router/g" /etc/neutron/neutron.conf
  sed -i "s/# allow_overlapping_ips = False/allow_overlapping_ips = True/g" /etc/neutron/neutron.conf
  sed -i "s/# verbose = False/verbose = True/g" /etc/neutron/neutron.conf
  sed -i "s/connection = sqlite:\/\/\/\/var\/lib\/neutron\/neutron.sqlite/# connection =/g" /etc/neutron/neutron.conf

  ################### l3_agent.ini


  sed -i "s/# interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver/interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver\n\
external_network_bridge = br-ex \n\
use_namespaces = True\n\
verbose = True\n\
agent_mode = dvr/g" /etc/neutron/l3_agent.ini


  ########### metadata_agent.ini


  sed -i "s/admin_password = %SERVICE_PASSWORD%/nova_metadata_ip = $CONTROLLER_M_IP\n\
metadata_proxy_shared_secret = METADATA_SECRET\n\
verbose = True/g" /etc/neutron/metadata_agent.ini

  sed -i "s/auth_url = http:\/\/localhost:5000\/v2.0/#/g" /etc/neutron/metadata_agent.ini
  sed -i "s/admin_tenant_name = %SERVICE_TENANT_NAME%/#project_name = service/g" /etc/neutron/metadata_agent.ini
  sed -i "s/admin_user = %SERVICE_USER%/#username = neutron/g" /etc/neutron/metadata_agent.ini
  sed -i "s/auth_region = RegionOne/#/g" /etc/neutron/metadata_agent.ini


  #################### ml2_conf.ini

  sed -i "s/# type_drivers = local,flat,vlan,gre,vxlan/type_drivers = vxlan\n\
tenant_network_types = vxlan\n\
mechanism_drivers = openvswitch,l2population/g" /etc/neutron/plugins/ml2/ml2_conf.ini

  sed -i "s/# vni_ranges =/vni_ranges = 1001:2000/g" /etc/neutron/plugins/ml2/ml2_conf.ini


  sed -i "s/# enable_ipset = True/enable_security_group = True\n\
enable_ipset = True\n\
firewall_driver = neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver\n\n\
[ovs]\n\
local_ip = $COMPUTE_D_IP\n\n\
[agent]\n\
tunnel_types = vxlan\n\
l2_population = True\n\
enable_distributed_routing = True/g" /etc/neutron/plugins/ml2/ml2_conf.ini


  ######## We need to reconfigure nova.conf bacause of using networking
  ######## nova.conf

  sed -i "/DEFAULT/a\network_api_class = nova.network.neutronv2.api.API\n\
security_group_api = neutron\n\
linuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver\n\
firewall_driver = nova.virt.firewall.NoopFirewallDriver" /etc/nova/nova.conf
  sed -i "/rabbit_password/a\[neutron]\n\
url = http:\/\/$CONTROLLER_M_IP:9696\n\
auth_strategy = keystone\n\
admin_auth_url = http:\/\/$CONTROLLER_M_IP:35357\/v2.0\n\
admin_tenant_name = service\n\
admin_username = neutron\n\
admin_password = $PASSWORD" /etc/nova/nova.conf


  service nova-compute restart
  service neutron-plugin-openvswitch-agent restart
  service neutron-l3-agent restart
  service neutron-metadata-agent restart

fi


#################### Installl Ceilometer Part ################




sudo apt-get install -y ceilometer-agent-compute


Ceilometer=`dpkg -l | grep ceilometer-api`

if [ "$Ceilometer" == "" ]; then


  ######## configure ceilometer.conf


  #TELEMETRY_SECRET=`openssl rand -hex 10`

  sed -i "s/#rpc_backend = rabbit/rpc_backend = rabbit\n\
verbose = True/g" /etc/ceilometer/ceilometer.conf
  sed -i "s/#rabbit_host = localhost/rabbit_host = $CONTROLLER_M_IP/g" /etc/ceilometer/ceilometer.conf
  sed -i "s/#rabbit_userid = guest/rabbit_userid = openstack/g" /etc/ceilometer/ceilometer.conf
  sed -i "s/#rabbit_password = guest/rabbit_password = $PASSWORD/g" /etc/ceilometer/ceilometer.conf
  sed -i "s/#auth_uri = <None>/auth_uri = http:\/\/$CONTROLLER_M_IP:5000\/v2.0\n\
identity_uri = http:\/\/$CONTROLLER_M_IP:35357\n\
admin_tenant_name = service\n\
admin_user = ceilometer\n\
admin_password = $PASSWORD\n\n\
[service_credentials]\n\
os_auth_url = http:\/\/$CONTROLLER_M_IP:5000\/v2.0\n\
os_username = ceilometer\n\
os_tenant_name = service\n\
os_password = $PASSWORD\n\
os_endpoint_type = internalURL\n\
os_region_name = RegionOne\n\n\
[publisher]\n\
telemetry_secret = $PASSWORD/g" /etc/ceilometer/ceilometer.conf

  ################# configure nova.conf

  sed -i "/DEFAULT/a\instance_usage_audit = True\n\
instance_usage_audit_period = hour\n\
notify_on_state_change = vm_and_task_state\n\
notification_driver = messagingv2" /etc/nova/nova.conf

fi


service ceilometer-agent-compute restart
service nova-compute restart


ovs-vsctl add-br br-ex
ifconfig ${MGMT_INTERFACE} 0
ovs-vsctl add-port br-ex ${MGMT_INTERFACE}

sed -i "s/${MGMT_INTERFACE}/br-ex/g" /etc/network/interfaces
sed -i "s/loopback/loopback\n\n\
auto ${MGMT_INTERFACE}/g" /etc/network/interfaces

echo "this is end for ethernet setting"

ifdown br-ex
ifup br-ex
ifconfig ${MGMT_INTERFACE} up

service nova-compute restart
