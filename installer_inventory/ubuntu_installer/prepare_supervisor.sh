#!/bin/bash

BOX=$1

INSTALLER_PATH="${HOME}/dsp_installer"
CONF_DIR="${INSTALLER_PATH}/conf"
SUPERVISOR_DIR="${INSTALLER_PATH}/installer_inventory/ubuntu_installer"
DSP_INSTALLER_PATH="${INSTALLER_PATH}/dsp_installer"

REPO_DIR=/usr/share/maas/web/static/maasrepo
REPO_URL='http://210.114.90.8/MAAS/static/maasrepo'

echo ""
echo ""
echo "Enter Prepare Ubuntu Supervisor Script"

if [ ! -f "${DSP_INSTALLER_PATH}/common_ubuntu.sh" ]; then
	cat "${SUPERVISOR_DIR}/maas_cli_login.sh" > "${DSP_INSTALLER_PATH}/common_ubuntu.sh"
	chmod 755 "${DSP_INSTALLER_PATH}/common_ubuntu.sh"
	echo "common_ubuntu.sh"
fi


cat ${SUPERVISOR_DIR}/maas_start.sh > "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh"
sed -i "s/<BOX_NAME>/${BOX}/g" "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh"

cat ${CONF_DIR}/${BOX} > ${REPO_DIR}/scripts/${BOX}.sh
cat ${SUPERVISOR_DIR}/ubuntu_account_cfg.sh >> ${REPO_DIR}/scripts/${BOX}.sh
cat ${SUPERVISOR_DIR}/ubuntu_net_cfg.sh >> ${REPO_DIR}/scripts/${BOX}.sh
cat ${SUPERVISOR_DIR}/ubuntu_apt_cfg.sh >> ${REPO_DIR}/scripts/${BOX}.sh
cat ${SUPERVISOR_DIR}/ubuntu_add_cfg.sh >> ${REPO_DIR}/scripts/${BOX}.sh



cat "${SUPERVISOR_DIR}/ubuntu_supervisor.sh" > "${DSP_INSTALLER_PATH}/${BOX}_ubuntu.sh"
sed -i "s/<BOX_NAME>/${BOX}/g" "${DSP_INSTALLER_PATH}/${BOX}_ubuntu.sh"


chmod 755 "${DSP_INSTALLER_PATH}/${BOX}_ubuntu.sh" "${DSP_INSTALLER_PATH}/${BOX}_ubuntu_1.sh" "${REPO_DIR}/scripts/${BOX}.sh"
