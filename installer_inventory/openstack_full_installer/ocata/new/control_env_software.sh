#!/bin/bash


## NTP Installation
apt install -y chrony
echo "allow 172.20.0.0/16" >> /etc/chrony/chrony.conf
service chrony restart


## DB Installation
apt install -y mariadb-server python-pymysql
echo "[mysqld]
bind-address = $CTRL_IP

default-storage-engine = innodb
innodb_file_per_table = on
max_connections = 4096
collation-server = utf8_general_ci
character-set-server = utf8" > /etc/mysql/mariadb.conf.d/99-openstack.cnf

service mysql restart
echo -e "$PASSWORD\nn\ny\ny\ny\ny" | mysql_secure_installation


## Message Queue Installation
apt install -y rabbitmq-server
rabbitmqctl add_user openstack $RABBIT_PASS
rabbitmqctl set_permissions openstack ".*" ".*" ".*"


## Memcached Installation
apt install -y memcached python-memcache
sed -i "s/^-l.*/-l ${CTRL_IP}/" /etc/memcached.conf
service memcached restart
