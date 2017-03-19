#!/bin/bash

BOX=$1

INSTALLER_PATH="${HOME}/DsP-Installer"
SUPERVISOR_DIR="${INSTALLER_PATH}/installer_inventory/openstack_full_installer"
DSP_INSTALLER_DIR="${INSTALLER_PATH}/dsp_installer"
CONF_DIR=${INSTALLER_PATH}/conf
PG_TPL=${CONF_DIR}/PLAYGROUND_TEMPLATE
#OPENSTACK_PASSWORD='fn!xo!ska!'
OPENSTACK_PASSWORD='test'
VERSION="newton"
source $CONF_DIR/$BOX

echo ""
echo ""
echo "Prepare Supervisor ${BOX}	: Enter Prepare OpenStack Full Installer Script"
echo ""
echo "Prepare Supervisor ${BOX}	: You chose Manual as OpenStack Installer"

OPENSTACK_MODE=`cat $PG_TPL | sed -e "/TARGET_BOXES/d" -ne "/$BOX/,/}/p" | grep OPENSTACK_MODE | sed -e "s/OPENSTACK_MODE://g" | awk '{print $1}'`
echo "Prepare Supervisor ${BOX}	: OpenStack Mode --> $OPENSTACK_MODE"

if [ ${OPENSTACK_MODE} == Compute ]; then

        echo "Prepare OpenStack ${BOX}	: Prepare Compute Node"


        CONTROLLER_NODE=`cat $PG_TPL | sed -e "/TARGET_BOXES/d" -ne "/$BOX/,/}/p" | grep OPENSTACK_CONTROLLER |sed -e "s/OPENSTACK_CONTROLLER://g" | awk '{print $1}'`
	CONTROLLER_MGMT_IP=$(cat ${CONF_DIR}/$CONTROLLER_NODE | grep MGMT_IP_ADDRESS | sed "s/MGMT_IP_ADDRESS=//g")
        CONTROLLER_CTRL_IP=$(cat ${CONF_DIR}/$CONTROLLER_NODE | grep CTRL_IP_ADDRESS | sed "s/CTRL_IP_ADDRESS=//g")

        cat $SUPERVISOR_DIR/${VERSION}/compute.sh > $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
	sed -i "s/<M_IP>/${MGMT_IP_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<C_IP>/${CTRL_IP_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<D_IP>/${DATA_IP_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<CTR_M_IP>/${CONTROLLER_MGMT_IP}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<CTR_C_IP>/${CONTROLLER_CTRL_IP}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
	sed -i "s/<PASSWORD>/\'${OPENSTACK_PASSWORD}\'/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh

else  # if the Box is OpenStack Controller

        echo "Prepare Supervisor ${BOX}	: Prepare Controller Node"

        cat $SUPERVISOR_DIR/${VERSION}/controller.sh > $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
	sed -i "s/<M_IP>/${MGMT_IP_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<D_IP>/${DATA_IP_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<C_IP>/${CTRL_IP_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
	sed -i "s/<PASSWORD>/\'${OPENSTACK_PASSWORD}\'/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
fi

## Copy & Modify full_supervisor.sh file ##

cat "${SUPERVISOR_DIR}/openstack_supervisor.sh" > "${DSP_INSTALLER_DIR}/${BOX}_openstack.sh"
sed -i "s/<BOX_NAME>/${BOX}/g" "${DSP_INSTALLER_DIR}/${BOX}_openstack.sh"
chmod 755 "${DSP_INSTALLER_DIR}/${BOX}_openstack.sh" "${DSP_INSTALLER_DIR}/${BOX}_openstack_1.sh"
