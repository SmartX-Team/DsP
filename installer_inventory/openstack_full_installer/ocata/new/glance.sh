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

## DB Configuration
mysql -uroot -p${MYSQL_PASS} -e "CREATE DATABASE glance;"
mysql -uroot -p${MYSQL_PASS} -e "GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' IDENTIFIED BY '$GLANCE_DBPASS';"
mysql -uroot -p${MYSQL_PASS} -e "GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' IDENTIFIED BY '$GLANCE_DBPASS';"


## Create OpenStack user/role/service/endpoints
source admin-openrc
openstack user create --domain default --password $GLANCE_PASS glance
openstack role add --project service --user glance admin
openstack service create --name glance --description "OpenStack Image" image

openstack endpoint create --region RegionOne image public http://$MGMT_IP:9292
openstack endpoint create --region RegionOne image internal http://$CTRL_IP:9292
openstack endpoint create --region RegionOne image admin http://$CTRL_IP:9292


## Glance Installation
apt install -y glance
sed -i "s/^#connection = <None>/connection = mysql+pymysql:\/\/glance:$GLANCE_DBPASS@$CTRL_IP\/glance/g" /etc/glance/glance-api.conf
sed -i "s/#auth_uri = <None>/auth_uri = http:\/\/$CTRL_IP:5000\n\
auth_url = http:\/\/$CTRL_IP:35357\n\
memcached_servers = $CTRL_IP:11211\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
project_name = service\n\
username = glance\n\
password = $GLANCE_PASS\n/g" /etc/glance/glance-api.conf
sed -i "s/^#flavor.*/flavor = keystone/" /etc/glance/glance-api.conf
sed -i "s/^\[glance_store\]/\[glance_store\]\n\
stores = file,http\n\
default_store = file\n\
filesystem_store_datadir = \/var\/lib\/glance\/images\//" /etc/glance/glance-api.conf

sed -i "s/^#connection = <None>/connection = mysql+pymysql:\/\/glance:$GLANCE_DBPASS@$CTRL_IP\/glance/g" /etc/glance/glance-registry.conf
sed -i "s/#auth_uri = <None>/auth_uri = http:\/\/$CTRL_IP:5000\n\
auth_url = http:\/\/$CTRL_IP:35357\n\
memcached_servers = $CTRL_IP:11211\n\
auth_type = password\n\
project_domain_name = default\n\
user_domain_name = default\n\
project_name = service\n\
username = glance\n\
password = $GLANCE_PASS\n/g" /etc/glance/glance-registry.conf
sed -i "s/^#flavor.*/flavor = keystone/" /etc/glance/glance-registry.conf


su -s /bin/sh -c "glance-manage db_sync" glance
service glance-registry restart
service glance-api restart


## Upload Cirros Image
source ./admin-openrc
wget http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img
openstack image create "cirros" --file cirros-0.3.5-x86_64-disk.img --disk-format qcow2 --container-format bare --public
