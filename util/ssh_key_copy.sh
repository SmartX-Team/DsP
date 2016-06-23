#!/bin/bash

BOX=$1

CONF_DIR="${HOME}/dsp_installer/conf"
source "${CONF_DIR}/${BOX}"

KEY_DIR="`eval echo "~$(whoami)"`/.ssh"

BOX_IP_ADDRESS="${MGMT_IP_ADDRESS}"
ACCOUNT="${USER_ACCOUNT}"
PWD="${PASSWD}"

/usr/bin/expect <<EOD
set timeout 5
spawn ssh-copy-id -i ${KEY_DIR}/id_rsa  ${ACCOUNT}@${BOX_IP_ADDRESS}
expect "assword: "
send "${PWD}\n"
expect eof
EOD
