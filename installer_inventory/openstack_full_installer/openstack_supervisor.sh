#!/bin/bash

BOX="<BOX_NAME>"
INSTALLER_PATH="${HOME}/DsP-Installer"
CONF_DIR="${INSTALLER_PATH}/conf"
DSP_INSTALLER_DIR="${INSTALLER_PATH}/dsp_installer"
source ${CONF_DIR}/${BOX}

START_TIME=$(date +%s)

ssh -oStrictHostKeyChecking=no -oBatchMode=yes -oConnectTimeout=3 -q ${USER_ACCOUNT}@${MGMT_IP_ADDRESS} exit
if [ $? -ne 0 ]; then
echo "${BOX}_openstack	: copy ssh key"
/usr/bin/expect <<EOD
set timeout 5
spawn ssh-copy-id -i ${HOME}/.ssh/id_rsa ${USER_ACCOUNT}@${MGMT_IP_ADDRESS}
expect "assword: "
send "${PASSWD}\n"
expect eof
EOD
fi

echo "${BOX}_openstack	: Copy Installation Script"
scp -oStrictHostKeyChecking=no -oCheckHostIP=no "${DSP_INSTALLER_DIR}/${BOX}_openstack_1.sh" ${USER_ACCOUNT}@${MGMT_IP_ADDRESS}:~/openstack.sh

echo "${BOX}_openstack	: Execute the Installation Script"
sudo ssh -oStrictHostKeyChecking=no -oCheckHostIP=no ${USER_ACCOUNT}@${MGMT_IP_ADDRESS} "sudo bash ~/openstack.sh" 1>${INSTALLER_PATH}/logs/${BOX}_openstack.log 2>&1

END_TIME=$(date +%s)
echo "OpenStack Installation for $BOX Box takes  $(($END_TIME - $START_TIME)) seconds to finish" > "${LOGS_DIR}/${BOX}_OpenStack_elapsed_time"
