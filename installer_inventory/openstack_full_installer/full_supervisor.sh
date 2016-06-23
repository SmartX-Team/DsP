#!/bin/bash

BOX="<BOX_NAME>"
BOX_IP_ADDRESS="<BOX_IP_ADDRESS>"
INSTALLER_PATH="${HOME}/dsp_installer"
DSP_INSTALLER_DIR="${INSTALLER_PATH}/dsp_installer"

USER_ACCOUNT='<USER_ACCOUNT>'
PASSWD='<PASSWD>'
OPENSTACK_MODE='<OPENSTACK_MODE>'

echo "Enter ${BOX} OpenStack Full Supervisor"

START_TIME=$(date +%s)
#bash "${INSTALLER_PATH}/util/ssh_key_clean.sh" ${BOX}
#bash "${INSTALLER_PATH}/util/ssh_key_copy.sh" ${BOX}

#### Copy openstack_1.sh file to Target box through "scp" command ####
scp -oStrictHostKeyChecking=no -oCheckHostIP=no "${DSP_INSTALLER_DIR}/${BOX}_openstack_1.sh" ${USER_ACCOUNT}@$BOX_IP_ADDRESS:~/openstack.sh

if [ -f ${DSP_INSTALLER_DIR}/${BOX}_openstack_wsgi-keystone.conf ]; then
	scp -oStrictHostKeyChecking=no -oCheckHostIP=no "${DSP_INSTALLER_DIR}/${BOX}_openstack_wsgi-keystone.conf" ${USER_ACCOUNT}@$BOX_IP_ADDRESS:~/wsgi-keystone.conf
	scp -oStrictHostKeyChecking=no -oCheckHostIP=no "${DSP_INSTALLER_DIR}/${BOX}_openstack_client.py" ${USER_ACCOUNT}@$BOX_IP_ADDRESS:~/client.py
fi

if [ "${OPENSTACK_MODE}" == "Compute" ]; then
	while [ 1 ]; do
		sleep 10

		BOX_STATUS=`ssh -o ConnectTimeout=2 ${USER_ACCOUNT}@${MGMT_IP_ADDRESS} "dpkg -l | grep nova"`
		if [ "${BOX_STATUS:-null}" != null ]; then
			break;
		fi
	done
fi

#### Execute openstack_1.sh file through ssh ####
sudo ssh -oStrictHostKeyChecking=no -oCheckHostIP=no ${USER_ACCOUNT}@${BOX_IP_ADDRESS} "sudo bash ~/openstack.sh" 1>openstack.log 2>&1

END_TIME=$(date +%s)
echo "$OpenStack Installation for $BOX Box takes  $(($END_TIME - $START_TIME)) seconds to finish" >> "${LOGS_DIR}/${SW}_elapsed_time"

