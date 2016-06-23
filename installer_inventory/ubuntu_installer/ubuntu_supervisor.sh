#!/bin/bash

BOX="<BOX_NAME>"

INSTALLER_PATH="${HOME}/dsp_installer"
CONF_DIR="${INSTALLER_PATH}/conf"
DSP_INSTALLER_DIR="${INSTALLER_PATH}/dsp_installer"
MAAS_REPO_DIR="/usr/share/maas/web/static/maasrepo"

bash "${DSP_INSTALLER_DIR}/${BOX}_ubuntu_1.sh"

source ${CONF_DIR}/${BOX}

while [ 1 ]; do
	nc -z -w 2 ${MGMT_IP_ADDRESS} 22
	if [ $? -eq 0 ]; then
		break;
	fi 
done

	bash $INSTALLER_PATH/util/ssh_key_clean.sh $BOX > /dev/null
	bash ${INSTALLER_PATH}/util/ssh_key_copy.sh $BOX
#sudo bash ${INSTALLER_PATH}/util/ssh_key_copy.sh $BOX
###################  ubuntu_supervisor.sh  #############################
########################################################################
