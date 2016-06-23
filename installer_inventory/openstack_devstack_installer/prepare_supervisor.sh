BOX=$1

INSTALLER_PATH=${HOME}/dsp_installer
SUPERVISOR_DIR=$INSTALLER_PATH/installer_inventory/openstack_devstack_installer
DSP_INSTALLER_DIR=$INSTALLER_PATH/dsp_installer
CONF_DIR=${INSTALLER_PATH}/conf
PG_TPL=${CONF_DIR}/PLAYGROUND_TEMPLATE

echo "*** You chose Devstack as OpenStack Installer"

cat $SUPERVISOR_DIR/devstack_common.sh > $DSP_INSTALLER_DIR/${BOX}_openstack_1.sh


OPENSTACK_MODE=`cat $PG_TPL | sed -e "/TARGET_BOXES/d" -ne "/$BOX/,/}/p" | grep OPENSTACK_MODE | sed -e "s/OPENSTACK_MODE://g" | awk '{print $1}'`
echo "OpenStack Mode: $OPENSTACK_MODE"

if [ ${OPENSTACK_MODE} == "Compute" ]; then
        echo "Prepare Compute Node"
        CONTROLLER_NODE=`cat $PG_TPL | sed -e "/TARGET_BOXES/d" -ne "/$BOX/,/}/p" | grep OPENSTACK_CONTROLLER |sed -e "s/OPENSTACK_CONTROLLER://g"`
        cat $SUPERVISOR_DIR/devstack_compute.sh >> $DSP_INSTALLER_DIR/${BOX}_openstack_2.sh
        bash $SUPERVISOR_DIR/make_local_conf.sh $BOX "COMPUTE"  $CONTROLLER_NODE

else
        echo "Prepare Controller Node"

        cat $SUPERVISOR_DIR/devstack_controller.sh >> $DSP_INSTALLER_DIR/${BOX}_openstack_2.sh
        bash $SUPERVISOR_DIR/make_local_conf.sh $BOX "CONTROLLER"
fi

chmod 755 ${DSP_INSTALLER_DIR}/${BOX}_openstack_1.sh ${DSP_INSTALLER_DIR}/${BOX}_openstack_2.sh
