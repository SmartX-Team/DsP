#/bin/bash

BOX="<BOX_NAME>"

INSTALLER_PATH="${HOME}/DsP-Installer"
CONF_DIR="${INSTALLER_PATH}/conf"
DSP_INSTALLER_DIR="${INSTALLER_PATH}/dsp_installer"
LOG_PATH="${INSTALLER_PATH}/logs"

START_TIME=$(date +%s)
echo "Enter ubuntu_supervisor.sh for ${BOX}.sh"
source ${CONF_DIR}/${BOX}

python ${DSP_INSTALLER_DIR}/maas_interface.py ${BOX}
while [ 1 ]; do
	nc -z -w 2 ${MGMT_IP_ADDRESS} 22
	if [ $? -eq 0 ]; then
		break;
	fi
	sleep 5 
done
ssh-keygen -f "/root/.ssh/known_hosts" -R ${MGMT_IP_ADDRESS}
scp -oStrictHostKeyChecking=no -oCheckHostIP=no ${DSP_INSTALLER_DIR}/${BOX}_ubuntu_1.sh ubuntu@${MGMT_IP_ADDRESS}:~/${BOX}.sh
if [ $? -ne 0 ]; then
	sleep 10
	scp -oStrictHostKeyChecking=no -oCheckHostIP=no ${DSP_INSTALLER_DIR}/${BOX}_ubuntu_1.sh ubuntu@${MGMT_IP_ADDRESS}:~/${BOX}.sh
fi

ssh -oStrictHostKeyChecking=no -oCheckHostIP=no ubuntu@${MGMT_IP_ADDRESS} "sudo bash ~/${BOX}.sh" > "${LOG_PATH}/${BOX}_ubuntu.log" 2>&1

ssh -oStrictHostKeyChecking=no -oBatchMode=yes -oConnectTimeout=3 -q ${USER_ACCOUNT}@${MGMT_IP_ADDRESS} exit

if [ $? -ne 0 ]; then
echo "ubuntu_supervisor (${BOX})	: copy ssh key"
/usr/bin/expect <<EOD
set timeout 5
spawn ssh-copy-id -oStrictHostKeyChecking=no -i ${HOME}/.ssh/id_rsa ${USER_ACCOUNT}@${MGMT_IP_ADDRESS}
expect "assword: "
send "${PASSWD}\n"
expect eof
EOD
fi

ssh -oStrictHostKeyChecking=no -oCheckHostIP=no ${USER_ACCOUNT}@${MGMT_IP_ADDRESS} "echo Success > ~/.DsP_status"

END_TIME=$(date +%s)
echo "Ubuntu Installation for $BOX Box takes  $(($END_TIME - $START_TIME)) seconds to finish" > "${LOGS_DIR}/${BOX}_ubuntu_elapsed_time"

###################  ubuntu_supervisor.sh  #############################
########################################################################
