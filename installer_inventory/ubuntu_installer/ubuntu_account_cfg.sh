passwd root << EOF
$PASSWD
$PASSWD
EOF

adduser $USER_ACCOUNT <<EOF
$PASSWD
$PASSWD
EOF

echo "${USER_ACCOUNT}	ALL=(ALL)	NOPASSWD:ALL" >> /etc/sudoers
sed -i "s/PasswordAuthentication/#PasswordAuthentication/g" /etc/ssh/sshd_config
service ssh restart

echo "127.0.1.1 `hostname`" >> /etc/hosts
##################  ubuntu_account_cfg.sh  #############################
########################################################################
