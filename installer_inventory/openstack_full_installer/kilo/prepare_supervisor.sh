#!/bin/bash

BOX=$1

INSTALLER_PATH="${HOME}/dsp_installer"
SUPERVISOR_DIR="${INSTALLER_PATH}/installer_inventory/openstack_full_installer"
DSP_INSTALLER_DIR="${INSTALLER_PATH}/dsp_installer"
CONF_DIR=${INSTALLER_PATH}/conf
PG_TPL=${CONF_DIR}/PLAYGROUND_TEMPLATE
OPENSTACK_PASSWORD='fn!xo!ska!'
source $CONF_DIR/$BOX

echo ""
echo ""
echo "Enter Prepare OpenStack Full Installer Script"
echo ""
echo "*** You chose Manual as OpenStack Installer"

OPENSTACK_MODE=`cat $PG_TPL | sed -e "/TARGET_BOXES/d" -ne "/$BOX/,/}/p" | grep OPENSTACK_MODE | sed -e "s/OPENSTACK_MODE://g" | awk '{print $1}'`
echo "OPENSTACK_MODE: $OPENSTACK_MODE"

if [ ${OPENSTACK_MODE} == Compute ]; then

        echo "Prepare Compute Node"


        CONTROLLER_NODE=`cat $PG_TPL | sed -e "/TARGET_BOXES/d" -ne "/$BOX/,/}/p" | grep OPENSTACK_CONTROLLER |sed -e "s/OPENSTACK_CONTROLLER://g" | awk '{print $1}'`
	CONTROLLER_MGMT_IP=$(cat ${CONF_DIR}/$CONTROLLER_NODE | grep MGMT_IP_ADDRESS | sed "s/MGMT_IP_ADDRESS=//g")
        CONTROLLER_CTRL_IP=$(cat ${CONF_DIR}/$CONTROLLER_NODE | grep CTRL_IP_ADDRESS | sed "s/CTRL_IP_ADDRESS=//g")


        cat $SUPERVISOR_DIR/full_compute.sh > $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
	sed -i "s/<COMPUTE_MGMT_IP>/${MGMT_IP_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<COMPUTE_MGMT_MAC>/${MGMT_MAC_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<COMPUTE_DATA_IP>/${DATA_IP_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<CONTROLLER_MGMT_IP>/${CONTROLLER_MGMT_IP}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<CONTROLLER_CTRL_IP>/${CONTROLLER_CTRL_IP}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
	sed -i "s/<ADMIN_PASSWORD>/${OPENSTACK_PASSWORD}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh

else  # if the Box is OpenStack Controller

        echo "Prepare Controller Node"


        cat $SUPERVISOR_DIR/full_controller.sh > $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
	sed -i "s/<CONTROLLER_MGMT_IP>/${MGMT_IP_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<CONTROLLER_DATA_IP>/${DATA_IP_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
        sed -i "s/<CONTROLLER_CTRL_IP>/${CTRL_IP_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
	sed -i "s/<CONTROLLER_MGMT_MAC>/${MGMT_MAC_ADDRESS}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh
	sed -i "s/<ADMIN_PASSWORD>/${OPENSTACK_PASSWORD}/g" $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh

	cat $SUPERVISOR_DIR/wsgi-keystone.conf > "${DSP_INSTALLER_DIR}/${BOX}_openstack_wsgi-keystone.conf"
	cat $SUPERVISOR_DIR/client.py > "${DSP_INSTALLER_DIR}/${BOX}_openstack_client.py"
fi

## Copy & Modify full_supervisor.sh file ##

cat "${SUPERVISOR_DIR}/full_supervisor.sh" > "${DSP_INSTALLER_DIR}/${BOX}_openstack.sh"
sed -i "s/<BOX_NAME>/${BOX}/g" "${DSP_INSTALLER_DIR}/${BOX}_openstack.sh"
#sed -i "s/<BOX_IP_ADDRESS>/${MGMT_IP_ADDRESS}/g" "${DSP_INSTALLER_DIR}/${BOX}_openstack.sh"
sed -i "s/<BOX_IP_ADDRESS>/${DATA_IP_ADDRESS}/g" "${DSP_INSTALLER_DIR}/${BOX}_openstack.sh"
sed -i "s/<USER_ACCOUNT>/${USER_ACCOUNT}/g" "${DSP_INSTALLER_DIR}/${BOX}_openstack.sh"
sed -i "s/<PASSWD>/${PASSWD}/g" "${DSP_INSTALLER_DIR}/${BOX}_openstack.sh"


chmod 755 "${DSP_INSTALLER_DIR}/${BOX}_openstack.sh" "${DSP_INSTALLER_DIR}/${BOX}_openstack_1.sh"
