#!/bin/bash

## Keystone DB Configuartion
mysql -uroot -p${MYSQL_PASS} -e "CREATE DATABASE keystone;"
mysql -uroot -p${MYSQL_PASS} -e "GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' IDENTIFIED BY '$KEYSTONE_DBPASS';"
mysql -uroot -p${MYSQL_PASS} -e "GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' IDENTIFIED BY '$KEYSTONE_DBPASS';"


## Keystone Installation
apt install -y keystone
sed -i "s/^#connection = <None>/connection = mysql+pymysql:\/\/keystone:$KEYSTONE_DBPASS@$CTRL_IP\/keystone/" /etc/keystone/keystone.conf
sed -i "s/^\[token\]/\[token\]\nprovider = fernet/" /etc/keystone/keystone.conf

su -s /bin/sh -c "keystone-manage db_sync" keystone
keystone-manage fernet_setup --keystone-user keystone --keystone-group keystone
keystone-manage credential_setup --keystone-user keystone --keystone-group keystone

keystone-manage bootstrap --bootstrap-password $ADMIN_PASS \
  --bootstrap-admin-url http://$CTRL_IP:35357/v3/ \
  --bootstrap-internal-url http://$CTRL_IP:5000/v3/ \
  --bootstrap-public-url http://$MGMT_IP:5000/v3/ \
  --bootstrap-region-id $REGION_ID


## Apache2 Configuration
echo "ServerName $MGMT_IP" >> /etc/apache2/apache2.conf
service apache2 restart
rm -f /var/lib/keystone/keystone.db


## Export Variables for the remaining installation
export OS_USERNAME=admin
export OS_PASSWORD=$ADMIN_PASS
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_AUTH_URL=http://$CTRL_IP:35357/v3
export OS_IDENTITY_API_VERSION=3


## Create a Domain/Projects/Users/Roles
openstack project create --domain default --description "Service Project" service
openstack project create --domain default --description "Demo Project" demo
openstack user create --domain default --password $DEMO_PASS demo
openstack role create user
openstack role add --project demo --user demo user

sed -i "s/ admin_token_auth//" /etc/keystone/keystone-paste.ini

echo "export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=$ADMIN_PASS
export OS_AUTH_URL=http://$CTRL_IP:35357/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2" > ./admin-openrc

echo "export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=demo
export OS_USERNAME=demo
export OS_PASSWORD=$DEMO_PASS
export OS_AUTH_URL=http://$CTRL_IP:5000/v3
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2" > ./demo-openrc
