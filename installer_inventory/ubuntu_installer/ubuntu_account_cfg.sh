
passwd root << EOF
$PASSWD
$PASSWD
EOF

adduser $USER_ACCOUNT <<EOF
$PASSWD
$PASSWD
EOF

echo "${USER_ACCOUNT}	ALL=(ALL)	NOPASSWD:ALL" >> /etc/sudoers

##################  ubuntu_account_cfg.sh  #############################
########################################################################
