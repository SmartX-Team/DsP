#!/bin/bash

INSTALLER_PATH="${HOME}/DsP-Installer"
CONF_DIR="${INSTALLER_PATH}/conf"
DSP_INSTALLER_DIR="${INSTALLER_PATH}/dsp_installer"
UTIL_DIR="${INSTALLER_PATH}/utils"
LOGS_DIR="${INSTALLER_PATH}/logs"
PG_TPL="${CONF_DIR}/PLAYGROUND_TEMPLATE"

AVAIL_SW_LIST=`cat "${CONF_DIR}/AVAILABLE_SOFTWARE"`
TARGET_BOXES=`cat "${PG_TPL}" | grep TARGET_BOXES | sed -e "s/TARGET_BOXES//g" -e "s/://g"`

INSTALL_TARGET_SW(){
	BOX=$1
	SW=$2
	FNAME="${BOX}_$(echo ${SW} | tr "[:upper:]" "[:lower:]").sh"

	echo "Enter INSTALL_TARGET_SW() for the installation of $FNAME"

	source "${CONF_DIR}/${BOX}"
	ssh-keygen -f "/root/.ssh/known_hosts" -R ${MGMT_IP_ADDRESS}

	while [ 1 ]; do
		
		if [ ${SW} == "Ubuntu" ]; then
			break;
		fi

		##### Get status of the Target Box
		BOX_STATUS=`ssh -o ConnectTimeout=2 ubuntu@${MGMT_IP_ADDRESS} "cat ~/.DsP_status"`
		if [ $? -eq 0 ]; then
			echo "Installed Softwares in Box $BOX: $BOX_STATUS"

			##### Check whether the required software was installed
			CHECK=`echo ${BOX_STATUS} | grep "Success"`
			if [ "${CHECK:-null}" != null ]; then
				break;
			fi
		fi
		sleep 5
	done
	##### Execute the install supervisor
	ssh -oConnectTimeout=2 -oStrictHostKeyChecking=no -oCheckHostIP=no ubuntu@${MGMT_IP_ADDRESS} "echo Installing > ~/.DsP_status"
	sudo bash ${DSP_INSTALLER_DIR}/${FNAME}
	ssh -oConnectTimeout=2 -oStrictHostKeyChecking=no -oCheckHostIP=no ubuntu@${MGMT_IP_ADDRESS} "echo Success > ~/.DsP_status"
}

## Check the current status of the Box, one by one.
## And if the status become what we want, we executes the supervisor scripts.

for SW in $AVAIL_SW_LIST
do
	START_TIME=$(date +%s)

	## Execute common script for the software if it exists ##
	FNAME="common_$(echo ${SW} | tr "[:upper:]" "[:lower:]").sh"
	if [ -f "${DSP_INSTALLER_DIR}/${FNAME}" ]; then
		echo "Start to execute ${FNAME}"
		bash ${DSP_INSTALLER_DIR}/${FNAME}
	fi


	for BOX in $TARGET_BOXES
	do
		FNAME="${BOX}_$(echo ${SW} | tr "[:upper:]" "[:lower:]").sh"
		echo "FNAME is ${DSP_INSTALLER_DIR}/${FNAME}"
		if [ ! -f "${DSP_INSTALLER_DIR}/${FNAME}" ]; then
			echo "Pass"
		else
				echo "Start to execute ${FNAME}"
				INSTALL_TARGET_SW ${BOX} ${SW} &
		fi
	done

	wait

	END_TIME=$(date +%s)

	echo "$SW Installation takes  $(($END_TIME - $START_TIME)) seconds to finish" > "${LOGS_DIR}/${SW}_elapsed_time"
done
