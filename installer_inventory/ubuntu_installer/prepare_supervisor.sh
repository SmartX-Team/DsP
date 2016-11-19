#!/bin/bash

BOX=$1

INSTALLER_PATH="${HOME}/DsP-Installer"
CONF_DIR="${INSTALLER_PATH}/conf"
SUPERVISOR_DIR="${INSTALLER_PATH}/installer_inventory/ubuntu_installer"
DSP_INSTALLER_PATH="${INSTALLER_PATH}/dsp_installer"

REPO_IP="116.89.190.141"
REPO_DIR=/usr/share/maas/web/static/maasrepo
REPO_URL='http://116.89.190.141/MAAS/static/maasrepo'

echo ""
echo ""
echo "Enter Prepare Ubuntu Supervisor Script"

# MAAS Client Login --> common_ubuntu.sh
if [ ! -f "${DSP_INSTALLER_PATH}/common_ubuntu.sh" ]; then
	cat "${SUPERVISOR_DIR}/maas_cli_login.sh" > "${DSP_INSTALLER_PATH}/common_ubuntu.sh"
	chmod 755 "${DSP_INSTALLER_PATH}/common_ubuntu.sh"
	echo "common_ubuntu.sh"
fi

# Trigger MAAS to install Linux into a box --> ${BOX}_ubuntu_1.sh
cat ${SUPERVISOR_DIR}/maas_start.sh > "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh"
sed -i "s/<BOX_NAME>/${BOX}/g" "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh"

# Create Linux Default Account
# Configure Network Interfaces
# Install Ubuntu Packages
# Additional configurations
#				--> ${BOX}.sh
#				--> Copy to Web Server Directory
cat ${CONF_DIR}/${BOX} > ${SUPERVISOR_DIR}/${BOX}.sh
cat ${SUPERVISOR_DIR}/ubuntu_account_cfg.sh >> ${SUPERVISOR_DIR}/${BOX}.sh
cat ${SUPERVISOR_DIR}/ubuntu_net_cfg.sh >> ${SUPERVISOR_DIR}/${BOX}.sh
cat ${SUPERVISOR_DIR}/ubuntu_apt_cfg.sh >> ${SUPERVISOR_DIR}/${BOX}.sh
cat ${SUPERVISOR_DIR}/ubuntu_add_cfg.sh >> ${SUPERVISOR_DIR}/${BOX}.sh

chmod 755 ${SUPERVISOR_DIR}/${BOX}.sh
scp ${SUPERVISOR_DIR}/${BOX}.sh root@${REPO_IP}:${REPO_DIR}/scripts/${BOX}.sh

cat "${SUPERVISOR_DIR}/ubuntu_supervisor.sh" > "${DSP_INSTALLER_PATH}/${BOX}_ubuntu.sh"
sed -i "s/<BOX_NAME>/${BOX}/g" "${DSP_INSTALLER_PATH}/${BOX}_ubuntu.sh"


chmod 755 "${DSP_INSTALLER_PATH}/${BOX}_ubuntu.sh" "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh"
