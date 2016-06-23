#!/bin/bash

###################################
### It should be run as root ######
###################################

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi


################## This is Variable Part ##############


IP='<CONTROLLER_CTRL_IP>'
PASSWORD='<ADMIN_PASSWORD>'
M_IP='<CONTROLLER_MGMT_IP>'
D_IP='<CONTROLLER_DATA_IP>'
M_MAC='<CONTROLLER_MGMT_MAC>'
INTERFACE=$(ifconfig -a | grep $M_MAC | awk '{print $1}')




################# Update Package ##########

apt-get install ubuntu-cloud-keyring -y

echo "deb http://ubuntu-cloud.archive.canonical.com/ubuntu trusty-updates/kilo main" > /etc/apt/sources.list.d/cloudarchive-kilo.list

apt-get update && apt-get -y upgrade

########### Install Other packages

sudo apt-get install -y curl
sudo apt-get install -y ntp vlan bridge-utils

sed -i "/#kernel.domainname = example.com/a\
net.ipv4.ip_forward=1\n\
net.ipv4.conf.all.rp_filter=0\n\
net.ipv4.conf.default.rp_filter=0" /etc/sysctl.conf


sed -i "s/server ntp.ubuntu.com/server ntp.ubuntu.com\nserver 127.127.1.0\nfudge 127.127.1.0 stratum 10/g" /etc/ntp.conf
service ntp restart



######################## Install & Configure MYSQL



sudo debconf-set-selections <<< "mariadb-server mysql-server/root_password password $PASSWORD"
sudo debconf-set-selections <<< "mariadb-server mysql-server/root_password_again password $PASSWORD"
sudo apt-get -y install mariadb-server python-mysqldb


sudo touch /etc/mysql/conf.d/mysqld_openstack.cnf

echo "[mysqld]" >> /etc/mysql/conf.d/mysqld_openstack.cnf
echo "bind-address = $IP" >> /etc/mysql/conf.d/mysqld_openstack.cnf
echo "default-storage-engine = innodb" >> /etc/mysql/conf.d/mysqld_openstack.cnf
echo "innodb_file_per_table" >> /etc/mysql/conf.d/mysqld_openstack.cnf
echo "collation-server = utf8_general_ci" >> /etc/mysql/conf.d/mysqld_openstack.cnf
echo "init-connect = 'SET NAMES utf8'" >> /etc/mysql/conf.d/mysqld_openstack.cnf
echo "character-set-server = utf8" >> /etc/mysql/conf.d/mysqld_openstack.cnf

service mysql restart

echo -e "$PASSWORD\nn\ny\ny\ny\ny" | mysql_secure_installation

#################### RabbitMQ


apt-get install -y rabbitmq-server


rabbitmqctl add_user openstack $PASSWORD
rabbitmqctl set_permissions openstack ".*" ".*" ".*"




#################### Install Keystone


cat << EOF | mysql -uroot -p$PASSWORD
CREATE DATABASE keystone;
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '$PASSWORD';
GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY '$PASSWORD';
quit;
EOF

TOKEN=`openssl rand -hex 10`

echo "manual" > /etc/init/keystone.override

sudo apt-get -y install keystone python-openstackclient apache2 libapache2-mod-wsgi memcached python-memcache



# configure /etc/keystone/keystone.conf


sed -i "s/connection = sqlite:\/\/\/\/var\/lib\/keystone\/keystone.db/connection = mysql:\/\/keystone:$PASSWORD@$IP\/keystone/g" /etc/keystone/keystone.conf

sed -i "s/#admin_token = ADMIN/admin_token=$TOKEN/g" /etc/keystone/keystone.conf
#sed -i "/admin_token/a\rpc_backend = rabbit" /etc/keystone/keystone.conf
sed -i "s/#servers = localhost:11211/servers = localhost:11211/g" /etc/keystone/keystone.conf

sed -i "s/#provider = keystone.token.providers.uuid.Provider/provider = keystone.token.providers.uuid.Provider/g" /etc/keystone/keystone.conf
sed -i "s/#driver = keystone.token.persistence.backends.sql.Token/driver = keystone.token.persistence.backends.memcache.Token/g" /etc/keystone/keystone.conf
sed -i "s/#driver = keystone.contrib.revoke.backends.sql.Revoke/driver = keystone.contrib.revoke.backends.sql.Revoke/g" /etc/keystone/keystone.conf
sed -i "s/#verbose = false/verbose = True/g" /etc/keystone/keystone.conf



su -s /bin/sh -c "keystone-manage db_sync" keystone




############# wsgi???

cp wsgi-keystone.conf /etc/apache2/sites-available/wsgi-keystone.conf

ln -s /etc/apache2/sites-available/wsgi-keystone.conf /etc/apache2/sites-enabled


mkdir -p /var/www/cgi-bin/keystone

curl http://git.openstack.org/cgit/openstack/keystone/plain/httpd/keystone.py?h=stable/kilo | tee /var/www/cgi-bin/keystone/main /var/www/cgi-bin/keystone/admin


chown -R keystone:keystone /var/www/cgi-bin/keystone
chmod 755 /var/www/cgi-bin/keystone/*


service apache2 restart

rm -f /var/lib/keystone/keystone.db


export OS_TOKEN=$TOKEN
export OS_URL=http://$IP:35357/v2.0




openstack service create --name keystone --description "OpenStack Identity" identity
openstack endpoint create --publicurl http://$IP:5000/v2.0 --internalurl http://$IP:5000/v2.0 --adminurl http://$IP:35357/v2.0 --region RegionOne identity




######### Admin and demo create


openstack project create --description "Admin Project" admin
openstack user create --password $PASSWORD admin
openstack role create admin
openstack role add --project admin --user admin admin


########### service project

openstack project create --description "Service Project" service
openstack project create --description "Demo Project" demo
openstack user create --password $PASSWORD demo
openstack role create user
openstack role add --project demo --user demo user




unset OS_TOKEN OS_URL

touch admin-openrc.sh
echo "export OS_PROJECT_DOMAIN_ID=default" >> admin-openrc.sh
echo "export OS_USER_DOMAIN_ID=default" >> admin-openrc.sh
echo "export OS_PROJECT_NAME=admin" >> admin-openrc.sh
echo "export OS_TENANT_NAME=admin" >> admin-openrc.sh
echo "export OS_USERNAME=admin" >> admin-openrc.sh
echo "export OS_PASSWORD=$PASSWORD" >> admin-openrc.sh
echo "export OS_AUTH_URL=http://$IP:35357/v3" >> admin-openrc.sh


touch demo-openrc.sh
echo "export OS_PROJECT_DOMAIN_ID=default" >> demo-openrc.sh
echo "export OS_USER_DOMAIN_ID=default" >> demo-openrc.sh
echo "export OS_PROJECT_NAME=demo" >> demo-openrc.sh
echo "export OS_TENANT_NAME=demo" >> demo-openrc.sh
echo "export OS_USERNAME=demo" >> demo-openrc.sh
echo "export OS_PASSWORD=$PASSWORD" >> demo-openrc.sh
echo "export OS_AUTH_URL=http://$IP:5000/v3" >> demo-openrc.sh


########################### Glance Part

cat << EOF | mysql -uroot -p$PASSWORD
CREATE DATABASE glance;
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' IDENTIFIED BY '$PASSWORD';
GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' IDENTIFIED BY '$PASSWORD';
quit;
EOF


source admin-openrc.sh


openstack user create --password $PASSWORD glance
openstack role add --project service --user glance admin
openstack service create --name glance --description "OpenStack Image service" image
openstack endpoint create --publicurl http://$IP:9292 --internalurl http://$IP:9292 --adminurl http://$IP:9292 --region RegionOne image


sudo apt-get install -y glance python-glanceclient



################### glance-api.conf


#sed -i "s/# rpc_backend = 'rabbit'/rpc_packend = rabbit/g" /etc/glance/glance-api.conf
sed -i "s/rabbit_host = localhost/rabbit_host = $IP/g" /etc/glance/glance-api.conf
sed -i "s/rabbit_password = guest/rabbit_password = $PASSWORD/g" /etc/glance/glance-api.conf
sed -i "s/rabbit_userid = guest/rabbit_userid = openstack/g" /etc/glance/glance-api.conf
sed -i "s/sqlite_db = \/var\/lib\/glance\/glance.sqlite/connection = mysql:\/\/glance:$PASSWORD@$IP\/glance/g" /etc/glance/glance-api.conf

#sed -i "s/backend = sqlalchemy/backend = mysql/g" /etc/glance/glance-api.conf
sed -i "s/identity_uri = http:\/\/127.0.0.1:35357/auth_uri = http:\/\/$IP:5000\n\
auth_url = http:\/\/$IP:35357\n\
auth_plugin = password\n\
project_domain_id = default\n\
user_domain_id = default/g" /etc/glance/glance-api.conf

#sed -i "/identity_uri/a\auth_host = $IP\n\
#auth_port = 35357\n\
#auth_protocol = http" /etc/glance/glance-api.conf

sed -i "s/admin_tenant_name = %SERVICE_TENANT_NAME%/project_name = service/g" /etc/glance/glance-api.conf
sed -i "s/admin_user = %SERVICE_USER%/username = glance/g" /etc/glance/glance-api.conf
sed -i "s/admin_password = %SERVICE_PASSWORD%/password = $PASSWORD/g" /etc/glance/glance-api.conf
sed -i "s/#flavor=/flavor = keystone/g" /etc/glance/glance-api.conf
sed -i "s/# Default: 'file'/default_store = file\n\
filesystem_store_datadir = \/var\/lib\/glance\/images\//g" /etc/glance/glance-api.conf
sed -i "s/#verbose = False/verbose = True/g" /etc/glance/glance-api.conf


################### glance-registry.conf

sed -i "s/# rpc_backend = 'rabbit'/rpc_packend = rabbit/g" /etc/glance/glance-registry.conf
sed -i "s/rabbit_host = localhost/rabbit_host = $IP/g" /etc/glance/glance-registry.conf
sed -i "s/rabbit_password = guest/rabbit_password = $PASSWORD/g" /etc/glance/glance-registry.conf
sed -i "s/rabbit_userid = guest/rabbit_userid = openstack/g" /etc/glance/glance-registry.conf
sed -i "s/sqlite_db = \/var\/lib\/glance\/glance.sqlite/connection = mysql:\/\/glance:$PASSWORD@$IP\/glance/g" /etc/glance/glance-registry.conf

#sed -i "s/backend = sqlalchemy/backend = mysql/g" /etc/glance/glance-api.conf
sed -i "s/identity_uri = http:\/\/127.0.0.1:35357/auth_uri = http:\/\/$IP:5000\n\
auth_url = http:\/\/$IP:35357\n\
auth_plugin = password\n\
project_domain_id = default\n\
user_domain_id = default/g" /etc/glance/glance-registry.conf

#sed -i "/identity_uri/a\auth_host = $IP\n\
#auth_port = 35357\n\
#auth_protocol = http" /etc/glance/glance-api.conf

sed -i "s/admin_tenant_name = %SERVICE_TENANT_NAME%/project_name = service/g" /etc/glance/glance-registry.conf
sed -i "s/admin_user = %SERVICE_USER%/username = glance/g" /etc/glance/glance-registry.conf
sed -i "s/admin_password = %SERVICE_PASSWORD%/password = $PASSWORD/g" /etc/glance/glance-registry.conf
sed -i "s/#flavor=/flavor = keystone/g" /etc/glance/glance-registry.conf
sed -i "s/#verbose = False/verbose = True/g" /etc/glance/glance-registry.conf


##################### service restart & db sync

su -s /bin/sh -c "glance-manage db_sync" glance

service glance-registry restart
service glance-api restart

rm -f /var/lib/glance/glance.sqlite

echo "export OS_IMAGE_API_VERSION=2" | tee -a admin-openrc.sh demo-openrc.sh
source admin-openrc.sh
mkdir /tmp/images
wget -P /tmp/images http://download.cirros-cloud.net/0.3.4/cirros-0.3.4-x86_64-disk.img
glance image-create --name "cirros-0.3.4-x86_64" --file /tmp/images/cirros-0.3.4-x86_64-disk.img --disk-format qcow2 --container-format bare --visibility public --progress


rm -r /tmp/images


################# nova part



cat << EOF | mysql -uroot -p$PASSWORD
CREATE DATABASE nova;
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' IDENTIFIED BY '$PASSWORD';
GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY '$PASSWORD';
quit;
EOF


source admin-openrc.sh

openstack user create --password $PASSWORD nova
openstack role add --project service --user nova admin
openstack service create --name nova --description "OpenStack Compute" compute
openstack endpoint create --publicurl http://$IP:8774/v2/%\(tenant_id\)s --internalurl http://$IP:8774/v2/%\(tenant_id\)s --adminurl http://$IP:8774/v2/%\(tenant_id\)s --region RegionOne compute



apt-get install -y nova-api nova-cert nova-conductor nova-consoleauth nova-novncproxy nova-scheduler python-novaclient


################# nova.conf

sed -i "s/logdir=\/var\/log\/nova/log_dir=\/var\/log\/nova/g" /etc/nova/nova.conf
sed -i "/enabled_apis=ec2,osapi_compute,metadata/a\rpc_backend = rabbit\n\
auth_strategy = keystone\n\
my_ip = $IP\n\
vncserver_listen = $IP\n\
vncserver_proxyclient_address = $IP\n\
novncproxy_base_url = http://$M_IP:6080/vnc_auto.html\n\
[database]\n\
connection = mysql:\/\/nova:$PASSWORD@$IP\/nova\n\n\
[keystone_authtoken]\n\
auth_uri = http:\/\/$IP:5000\n\
auth_url = http:\/\/$IP:35357\n\
auth_plugin = password\n\
project_domain_id = default\n\
user_domain_id = default\n\
project_name = service\n\
username = nova\n\
password = $PASSWORD\n\n\
[glance]\n\
host = $IP\n\n\
[oslo_concurrency]\n\
lock_path = \/var\/lib\/nova\/tmp\n\n\
[oslo_messaging_rabbit]\n\
rabbit_host = $IP\n\
rabbit_userid = openstack\n\
rabbit_password = $PASSWORD" /etc/nova/nova.conf


su -s /bin/sh -c "nova-manage db sync" nova

service nova-api restart
service nova-cert restart
service nova-consoleauth restart
service nova-scheduler restart
service nova-conductor restart
service nova-novncproxy restart

rm -f /var/lib/nova/nova.sqlite
                                                           

########################## neutron part



cat << EOF | mysql -uroot -p$PASSWORD
CREATE DATABASE neutron;
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY '$PASSWORD';
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY '$PASSWORD';
quit;
EOF


source admin-openrc.sh

openstack user create --password $PASSWORD neutron
openstack role add --project service --user neutron admin
openstack service create --name neutron --description "OpenStack Networking" network
openstack endpoint create --publicurl http://$IP:9696 --adminurl http://$IP:9696 --internalurl http://$IP:9696 --region RegionOne network

apt-get install -y neutron-server neutron-plugin-ml2 python-neutronclient neutron-plugin-openvswitch-agent neutron-l3-agent neutron-dhcp-agent neutron-metadata-agent

############################# neutron.conf

sed -i "s/connection = sqlite:\/\/\/\/var\/lib\/neutron\/neutron.sqlite/connection = mysql:\/\/neutron:$PASSWORD@$IP\/neutron/g" /etc/neutron/neutron.conf

sed -i "s/# router_distributed = False/router_distributed = True/g" /etc/neutron/neutron.conf
sed -i "s/# rabbit_host = localhost/rabbit_host = $IP/g" /etc/neutron/neutron.conf
sed -i "s/# rabbit_userid = guest/rabbit_userid = openstack/g" /etc/neutron/neutron.conf
sed -i "s/# rabbit_password = guest/rabbit_password = $PASSWORD/g" /etc/neutron/neutron.conf
sed -i "s/# rpc_backend=rabbit/rpc_backend = rabbit/g" /etc/neutron/neutron.conf
sed -i "s/# auth_strategy = keystone/auth_strategy = keystone/g" /etc/neutron/neutron.conf
sed -i "s/auth_uri = http:\/\/127.0.0.1:35357\/v2.0\//auth_uri = http:\/\/$IP:5000/g" /etc/neutron/neutron.conf
sed -i "s/identity_uri = http:\/\/127.0.0.1:5000/auth_url = http:\/\/$IP:35357\n\
auth_plugin = password\n\
project_domain_id = default\n\
user_domain_id = default/g" /etc/neutron/neutron.conf
sed -i "s/admin_tenant_name = %SERVICE_TENANT_NAME%/project_name = service/g" /etc/neutron/neutron.conf
sed -i "s/admin_user = %SERVICE_USER%/username = neutron/g" /etc/neutron/neutron.conf
sed -i "s/admin_password = %SERVICE_PASSWORD%/password = $PASSWORD/g" /etc/neutron/neutron.conf
sed -i "s/# service_plugins =/service_plugins = router/g" /etc/neutron/neutron.conf
sed -i "s/# allow_overlapping_ips = False/allow_overlapping_ips = True/g" /etc/neutron/neutron.conf
sed -i "s/# notify_nova_on_port_status_changes = True/notify_nova_on_port_status_changes = True/g" /etc/neutron/neutron.conf
sed -i "s/# notify_nova_on_port_data_changes = True/notify_nova_on_port_data_changes = True/g" /etc/neutron/neutron.conf
sed -i "s/# nova_url = http:\/\/127.0.0.1:8774\/v2/nova_url = http:\/\/$IP:8774\/v2/g" /etc/neutron/neutron.conf
sed -i "s/# auth_plugin =/auth_url = http:\/\/$IP:35357\n\
auth_plugin = password\n\
project_domain_id = default\n\
user_domain_id = default\n\
region_name = RegionOne\n\
project_name = service\n\
username = nova\n\
password = $PASSWORD/g" /etc/neutron/neutron.conf

sed -i "s/# verbose = False/verbose = True/g" /etc/neutron/neutron.conf


######## We need to reconfigure nova.conf bacause of using networking
######## nova.conf

sed -i "/DEFAULT/a\network_api_class = nova.network.neutronv2.api.API\n\
security_group_api = neutron\n\
linuxnet_interface_driver = nova.network.linux_net.LinuxOVSInterfaceDriver\n\
firewall_driver = nova.virt.firewall.NoopFirewallDriver" /etc/nova/nova.conf
sed -i "/rabbit_password/a\[neutron]\n\
url = http:\/\/$IP:9696\n\
auth_strategy = keystone\n\
admin_auth_url = http:\/\/$IP:35357\/v2.0\n\
admin_tenant_name = service\n\
admin_username = neutron\n\
admin_password = $PASSWORD" /etc/nova/nova.conf



########### ml2_conf.ini

sed -i "s/# type_drivers = local,flat,vlan,gre,vxlan/type_drivers = vxlan\n\
tenant_network_types = vxlan\n\
mechanism_drivers = openvswitch,l2population/g" /etc/neutron/plugins/ml2/ml2_conf.ini

sed -i "s/# vni_ranges =/vni_ranges = 1001:2000/g" /etc/neutron/plugins/ml2/ml2_conf.ini


sed -i "s/# enable_ipset = True/enable_security_group = True\n\
enable_ipset = True\n\
firewall_driver = neutron.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver\n\n\
[ovs]\n\
local_ip = $D_IP\n\n\
[agent]\n\
tunnel_types = vxlan\n\
l2_population = True\n\
enable_distributed_routing = True/g" /etc/neutron/plugins/ml2/ml2_conf.ini



################# l3_agent.ini


sed -i "s/# interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver/interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver\n\
external_network_bridge = br-ex \n\
use_namespaces = True\n\
verbose = True\n\
agent_mode = dvr_snat/g" /etc/neutron/l3_agent.ini


############### dhcp_agent.ini

touch /etc/neutron/dnsmasq-neutron.conf

echo "dhcp-option-force=26,1400" >> /etc/neutron/dnsmasq-neutron.conf

sed -i "s/# debug = False/dnsmasq_config_file = \/etc\/neutron\/dnsmasq-neutron.conf\n\
verbose = True\n\
interface_driver = neutron.agent.linux.interface.OVSInterfaceDriver/g" /etc/neutron/dhcp_agent.ini

pkill dnsmasq




########### metadata_agent.ini


sed -i "s/auth_url = http:\/\/localhost:5000\/v2.0/auth_uri = http:\/\/$IP:5000\n\
auth_url = http:\/\/$IP:35357\n\
auth_plugin = password\n\
project_domain_id = default\n\
user_domain_id = default/g" /etc/neutron/metadata_agent.ini
sed -i "s/admin_tenant_name = %SERVICE_TENANT_NAME%/project_name = service/g" /etc/neutron/metadata_agent.ini
sed -i "s/admin_user = %SERVICE_USER%/username = neutron/g" /etc/neutron/metadata_agent.ini
sed -i "s/admin_password = %SERVICE_PASSWORD%/password = $PASSWORD\n\
nova_metadata_ip = $IP\n\
metadata_proxy_shared_secret = METADATA_SECRET\n\
verbose = True/g" /etc/neutron/metadata_agent.ini


sed -i "/admin_password/a\service_metadata_proxy = True\n\
metadata_proxy_shared_secret = METADATA_SECRET" /etc/nova/nova.conf

#service nova-api restart



su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron


service nova-api restart

service neutron-server restart

service openvswitch-switch restart
service neutron-plugin-openvswitch-agent restart
service neutron-l3-agent restart
service neutron-dhcp-agent restart
service neutron-metadata-agent restart


################################### heat Part




cat << EOF | mysql -uroot -p$PASSWORD
CREATE DATABASE heat;
GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'localhost' IDENTIFIED BY '$PASSWORD';
GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'%' IDENTIFIED BY '$PASSWORD';
quit;
EOF


source admin-openrc.sh

openstack user create --password $PASSWORD heat
openstack role add --project service --user heat admin
openstack role create heat_stack_owner


openstack role add --project demo --user demo heat_stack_owner
#You must add the heat_stack_owner role to users that manage stacks.

openstack role create heat_stack_user
#The Orchestration service automatically assigns the
#heat_stack_user role to users that it creates during stack deployment.
#By default, this role restricts API operations. To avoid conflicts,
#do not add this role to users with the heat_stack_owner role.

openstack service create --name heat --description "Orchestration" orchestration
openstack service create --name heat-cfn --description "Orchestration" cloudformation


openstack endpoint create --publicurl http://$IP:8004/v1/%\(tenant_id\)s --internalurl http://$IP:8004/v1/%\(tenant_id\)s --adminurl http://$IP:8004/v1/%\(tenant_id\)s --region RegionOne orchestration

openstack endpoint create --publicurl http://$IP:8000/v1 --internalurl http://$IP:8000/v1 --adminurl http://$IP:8000/v1 --region RegionOne cloudformation



sudo apt-get install -y heat-api heat-api-cfn heat-engine python-heatclient



########################### heat.conf

sed -i "s/#connection = <None>/connection = mysql:\/\/heat:$PASSWORD@$IP\/heat/g" /etc/heat/heat.conf
sed -i "s/#rpc_backend = rabbit/rpc_backend = rabbit/g" /etc/heat/heat.conf
sed -i "s/#rabbit_host = localhost/rabbit_host = $IP/g" /etc/heat/heat.conf
sed -i "s/#rabbit_userid = guest/rabbit_userid = openstack/g" /etc/heat/heat.conf
sed -i "s/#rabbit_password = guest/rabbit_password = $PASSWORD/g" /etc/heat/heat.conf
sed -i "s/#auth_uri = <None>/auth_uri = http:\/\/$IP:5000\/v2.0\n\
identity_uri = http:\/\/$IP:35357\n\
admin_tenant_name = service\n\
admin_user = heat\n\
admin_password = $PASSWORD\n\n\
[ec2authtoken]\n\
auth_uri = http:\/\/$IP:5000\/v2.0/g" /etc/heat/heat.conf
sed -i "s/#verbose = false/verbose = True\n\
heat_metadata_server_url = http:\/\/$IP:8000\n\
heat_waitcondition_server_url = http:\/\/$IP:8000\/v1\/waitcondition\n\
stack_domain_admin = heat_domain_admin\n\
stack_domain_admin_password = $PASSWORD\n\
stack_user_domain_name = heat_user_domain/g" /etc/heat/heat.conf





heat-keystone-setup-domain --stack-user-domain-name heat_user_domain --stack-domain-admin heat_domain_admin --stack-domain-admin-password $PASSWORD


su -s /bin/sh -c "heat-manage db_sync" heat

service heat-api restart
service heat-api-cfn restart
service heat-engine restart

rm -f /var/lib/heat/heat.sqlite



############################ Ceilometer part

#install mongodb
apt-get install -y mongodb-server mongodb-clients python-pymongo

sed -i "s/bind_ip = 127.0.0.1/bind_ip = $IP/g" /etc/mongodb.conf

service mongodb restart


sleep 3
mongo --host $IP --eval 'db = db.getSiblingDB("ceilometer"); db.addUser({user: "ceilometer", pwd: "'$PASSWORD'", roles: [ "readWrite", "dbAdmin" ]})'


##### configure Keystone
source admin-openrc.sh

openstack user create --password $PASSWORD ceilometer
openstack role add --project service --user ceilometer admin
openstack service create --name ceilometer --description "Telemetry" metering
openstack endpoint create --publicurl http://$IP:8777 --internalurl http://$IP:8777 --adminurl http://$IP:8777 --region RegionOne metering

sudo apt-get install -y ceilometer-api ceilometer-collector ceilometer-agent-central ceilometer-agent-notification ceilometer-alarm-evaluator ceilometer-alarm-notifier python-ceilometerclient




######## configure ceilometer.conf


#TELEMETRY_SECRET=`openssl rand -hex 10`

sed -i "s/#connection = <None>/connection = mongodb:\/\/ceilometer:$PASSWORD@$IP:27017\/ceilometer/g" /etc/ceilometer/ceilometer.conf
sed -i "s/#rpc_backend = rabbit/rpc_backend = rabbit\n\
verbose = True\n\
auth_strategy = keystone/g" /etc/ceilometer/ceilometer.conf
sed -i "s/#rabbit_host = localhost/rabbit_host = $IP/g" /etc/ceilometer/ceilometer.conf
sed -i "s/#rabbit_userid = guest/rabbit_userid = openstack/g" /etc/ceilometer/ceilometer.conf
sed -i "s/#rabbit_password = guest/rabbit_password = $PASSWORD/g" /etc/ceilometer/ceilometer.conf
sed -i "s/#auth_uri = <None>/auth_uri = http:\/\/$IP:5000\/v2.0\n\
identity_uri = http:\/\/$IP:35357\n\
admin_tenant_name = service\n\
admin_user = ceilometer\n\
admin_password = $PASSWORD\n\n\
[service_credentials]\n\
os_auth_url = http:\/\/$IP:5000\/v2.0\n\
os_username = ceilometer\n\
os_tenant_name = service\n\
os_password = $PASSWORD\n\
os_endpoint_type = internalURL\n\
os_region_name = RegionOne\n\n\
[publisher]\n\
telemetry_secret = $PASSWORD/g" /etc/ceilometer/ceilometer.conf

##################### It maybe causes some dependency issues
#sudo apt-get install -y python-pip
#sudo pip install --upgrade python-ceilometerclient
#sudo pip install --upgrade python-openstackclient


cp client.py /usr/lib/python2.7/dist-packages/ceilometerclient/client.py



service ceilometer-agent-central restart
service ceilometer-agent-notification restart
service ceilometer-api restart
service ceilometer-collector restart
service ceilometer-alarm-evaluator restart
service ceilometer-alarm-notifier restart

sed -i "/DEFAULT/a\notification_driver = messagingv2" /etc/glance/glance-api.conf

sed -i "/DEFAULT/a\notification_driver = messagingv2" /etc/glance/glance-registry.conf

service glance-registry restart
service glance-api restart


##################### dashboard part

sudo apt-get install -y openstack-dashboard

sed -i 's/OPENSTACK_HOST = "127.0.0.1"/OPENSTACK_HOST = "'$IP'"/g' /etc/openstack-dashboard/local_settings.py

sed -i 's/OPENSTACK_KEYSTONE_DEFAULT_ROLE = "_member_"/OPENSTACK_KEYSTONE_DEFAULT_ROLE = "user"/g' /etc/openstack-dashboard/local_settings.py

service apache2 reload


############# This is OVS Configuration Part ################

ovs-vsctl add-br br-ex
ifconfig $INTERFACE 0
ovs-vsctl add-port br-ex $INTERFACE

sed -i "s/$INTERFACE/br-ex/g" /etc/network/interfaces
sed -i "s/loopback/loopback\n\n\
auto $INTERFACE/g" /etc/network/interfaces

echo "this is end for ethernet setting"

ifdown br-ex
ifup br-ex
ifconfig $INTERFACE up



