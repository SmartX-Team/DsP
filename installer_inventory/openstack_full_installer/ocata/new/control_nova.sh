#!/bin/bash

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

## Configure Database
source admin-openrc
mysql -uroot -p${MYSQL_PASS} -e "CREATE DATABASE nova;"
mysql -uroot -p${MYSQL_PASS} -e "GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'localhost' IDENTIFIED BY '$NOVA_DBPASS';"
mysql -uroot -p${MYSQL_PASS} -e "GRANT ALL PRIVILEGES ON nova.* TO 'nova'@'%' IDENTIFIED BY '$NOVA_DBPASS';"

mysql -uroot -p${MYSQL_PASS} -e "CREATE DATABASE nova_api;"
mysql -uroot -p${MYSQL_PASS} -e "GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'localhost' IDENTIFIED BY '$NOVA_DBPASS';"
mysql -uroot -p${MYSQL_PASS} -e "GRANT ALL PRIVILEGES ON nova_api.* TO 'nova'@'%' IDENTIFIED BY '$NOVA_DBPASS';"


## Create user, role, endpoints
openstack user create --domain default --password $NOVA_PASS nova
openstack role add --project service --user nova admin
openstack service create --name nova --description "OpenStack Compute" compute
openstack endpoint create --region $REGION_ID compute public http://$MGMT_IP:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region $REGION_ID compute internal http://$CTRL_IP:8774/v2.1/%\(tenant_id\)s
openstack endpoint create --region $REGION_ID compute admin http://$CTRL_IP:8774/v2.1/%\(tenant_id\)s


## Install Nova
apt install -y nova-api nova-conductor nova-consoleauth nova-novncproxy nova-scheduler

sed -i "s/^connection=/#connection=/" /etc/nova/nova.conf
sed -i "s/^connection =/#connection =/" /etc/nova/nova.conf
sed -i "s/^\[api_database\]/\[api_database\]\n\
connection = mysql+pymysql:\/\/nova:$NOVA_DBPASS@$CTRL_IP\/nova_api/" /etc/nova/nova.conf
sed -i "s/^\[database\]/\[database\]\n\
connection = mysql+pymysql:\/\/nova:$NOVA_DBPASS@$CTRL_IP\/nova/" /etc/nova/nova.conf

sed -i "s/^\[DEFAULT\]/\[DEFAULT\]\n\
transport_url = rabbit:\/\/openstack:$RABBIT_PASS@$CTRL_IP/" /etc/nova/nova.conf

sed -i "s/^#auth_strategy.*/auth_strategy = keystone/" /etc/nova/nova.conf
sed -i "s/^\[keystone_authtoken\]/\[keystone_authtoken\]\n\
auth_uri = http:\/\/$CTRL_IP:5000\n\
auth_url = http:\/\/$CTRL_IP:35357\n\
memcached_servers = $CTRL_IP:11211\n\
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
vncserver_listen = \$my_ip\n\
vncserver_proxyclient_address = \$my_ip/" /etc/nova/nova.conf

sed -i "s/^\[glance\]/\[glance\]\n\
api_servers = http:\/\/$CTRL_IP:9292/" /etc/nova/nova.conf

sed -i "s/^lock_path=.*/lock_path = \/var\/lib\/nova\/tmp\//" /etc/nova/nova.conf

su -s /bin/sh -c "nova-manage api_db sync" nova
su -s /bin/sh -c "nova-manage db sync" nova


## Restart Nova Services
service nova-api restart
service nova-consoleauth restart
service nova-scheduler restart
service nova-conductor restart
service nova-novncproxy restart
