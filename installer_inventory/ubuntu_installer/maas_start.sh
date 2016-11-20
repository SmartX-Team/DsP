#!/bin/bash

BOX="<BOX_NAME>"
INSTALLER_PATH="${HOME}/DsP-Installer"
DSP_INSTALLER_PATH="${INSTALLER_PATH}/dsp_installer"
# readlink -f `dirname ${BASH_SOURCE[0]}`

echo "Enter ${BOX}_ubuntu_1.sh"
python ${DSP_INSTALLER_PATH}/maas_interface.py ${BOX}
