#!/bin/bash

BOX=$1

INSTALLER_PATH="${HOME}/DsP-Installer"
CONF_DIR="${INSTALLER_PATH}/conf"
SUPERVISOR_DIR="${INSTALLER_PATH}/installer_inventory/ubuntu_installer"
DSP_INSTALLER_PATH="${INSTALLER_PATH}/dsp_installer"

echo ""
echo ""
echo "Enter Prepare Ubuntu Supervisor Script"

# MAAS Client Login --> common_ubuntu.sh
#if [ ! -f "${DSP_INSTALLER_PATH}/common_ubuntu.sh" ]; then
#	cat "${SUPERVISOR_DIR}/maas_cli_login.sh" > "${DSP_INSTALLER_PATH}/common_ubuntu.sh"
#	chmod 755 "${DSP_INSTALLER_PATH}/common_ubuntu.sh"
#	echo "common_ubuntu.sh"
#fi

if [ ! -f "${DSP_INSTALLER_PATH}/maas_interface.py" ]; then
	cp ${SUPERVISOR_DIR}/maas_interface.py ${DSP_INSTALLER_PATH}/maas_interface.py
	chmod 755 ${DSP_INSTALLER_PATH}/maas_interface.py
fi

# Trigger MAAS to install Linux into a box --> ${BOX}_ubuntu_1.sh
cat "${SUPERVISOR_DIR}/ubuntu_supervisor.sh" > "${DSP_INSTALLER_PATH}/${BOX}_ubuntu.sh"
sed -i "s/<BOX_NAME>/${BOX}/g" "${DSP_INSTALLER_PATH}/${BOX}_ubuntu.sh"

# Create Linux Default Account
# Configure Network Interfaces
# Install Ubuntu Packages
# Additional configurations
#				--> ${BOX}.sh
#				--> Copy to Web Server Directory
cat ${CONF_DIR}/${BOX} > "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh"
cat ${SUPERVISOR_DIR}/ubuntu_account_cfg.sh >> "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh"
cat ${SUPERVISOR_DIR}/ubuntu_net_cfg.sh >> "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh"
cat ${SUPERVISOR_DIR}/ubuntu_apt_cfg.sh >> "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh"
cat ${SUPERVISOR_DIR}/ubuntu_add_cfg.sh >> "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh"

chmod 755 "${DSP_INSTALLER_PATH}/${BOX}_ubuntu.sh" "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh"
