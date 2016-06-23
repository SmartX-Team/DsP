#!/bin/bash
PWD='fn!xo!ska!'

cd ~
git clone https://git.openstack.org/openstack-dev/devstack
cd devstack
git checkout stable/juno
# git checkout grizzly-eol
wget -O ./local.conf http://210.114.90.8/MAAS/static/maasrepo/postscripts/service/local.conf.$(hostname)

while [1]; do
	sleep 10
	
/usr/bin/expect <<EOD
set timeout 20
spawn scp -oStrictHostKeyChecking=no -oCheckHostIP=no stack@210.114.90.99:/home/stack/logs/stack.sh.log.summary ./
expect "password: "
send "$PWD\r"
expect "# "
send "exit\r"
EOD

	CHECK_CONTROLLER=$(cat ./stack.sh.log.summary | grep Starting Nova)
	if [ "${CHECK_CONTROLLER:-null}" != null ]; then
		break;
	fi
done

./stack.sh

sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
