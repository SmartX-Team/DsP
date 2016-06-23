USERACCOUNT=stack
PASSWD='fn!xo!ska!'

cat "start to install devstack" >> /root/test_time
cat "========================================" >> /root/test_time
date >> /root/test_time

useradd -m -s /bin/bash $USERACCOUNT

/usr/bin/expect <<EOD
set timeout 20
spawn bash
expect "# "
send "passwd $USERACCOUNT \r"
expect "password: "
send "$PASSWD\r"
expect "password: "
send "$PASSWD\r"
expect"# "
send "exit\r"
EOD

echo "stack ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
apt-get install git -y

wget -O /home/stack/devstack_install.sh http://210.114.90.8/MAAS/static/maasrepo/postscripts/service/$(hostname)_devstack_install.sh 
chown stack:stack /home/stack/devstack_install.sh
su stack -c 'bash /home/stack/devstack_install.sh'

date >> /root/test_time
