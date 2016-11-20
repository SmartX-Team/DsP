#/bin/bash

BOX="<BOX_NAME>"

INSTALLER_PATH="${HOME}/DsP-Installer"
CONF_DIR="${INSTALLER_PATH}/conf"
DSP_INSTALLER_DIR="${INSTALLER_PATH}/dsp_installer"
MAAS_REPO_DIR="/usr/share/maas/web/static/maasrepo"

echo "Enter ubuntu_supervisor.sh for ${BOX}.sh"
source ${CONF_DIR}/${BOX}

#python ${DSP_INSTALLER_PATH}/maas_interface.py ${BOX}
while [ 1 ]; do
	nc -z -w 2 ${MGMT_IP_ADDRESS} 22
	if [ $? -eq 0 ]; then
		break;
	fi 
done

scp -oStrictHostKeyChecking=no -oCheckHostIP=no ubuntu@${MGMT_IP_ADDRESS} ${DSP_INSTALLER_DIR}/${BOX}_ubuntu_1.sh ubuntu@${MGMT_IP_ADDRESS}:~/${BOX}.sh
#ssh -oStrictHostKeyChecking=no -oCheckHostIP=no ubuntu@${MGMT_IP_ADDRESS} "sudo bash ~/${BOX}.sh"

###################  ubuntu_supervisor.sh  #############################
########################################################################
