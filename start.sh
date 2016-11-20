#!/bin/bash

# All of install procedures are controlled by this scripts.
# So, if you want to install some nodes, modify and execute this scripts.
#
# Last modified date : 16.03.07
# Made and modified by JSSHIN


## Variable Definition##
INSTALLER_PATH="$HOME/DsP-Installer"
LOG_DIR="$INSTALLER_PATH/logs"
CONF_DIR="$INSTALLER_PATH/conf"
PG_TPL="$CONF_DIR/PLAYGROUND_TEMPLATE"

if [ "$(id -u)" != "0" ]; then
   echo "This script should be run as root" 1>&2
   exit 1
fi

if [ `(pwd)` != ${INSTALLER_PATH} ]; then
	echo "You shouled execute this script in ${INSTALLER_PATH} directory!"
	exit 1
fi


## Box List Extraction
START_TIME=$(date +%s)

TARGET_BOXES=`cat $PG_TPL | grep TARGET_BOXES | sed -e "s/TARGET_BOXES//g" -e "s/://g"`

for BOX in $TARGET_BOXES
do
	echo "####################################################"
	echo "$BOX SITE installation Procedure is being started"
	echo -e "#####################################################\n\n"

        # This Part check whether this site can be install
		# DsP-Installer exclude boxes written in DONT_TOUCH_SITE.
		# This can prevent from doing provisioning over production environment.
        CHECK=$(cat $CONF_DIR/DONT_TOUCH_SITE | grep $BOX)

        if [ "${CHECK:-null}" != null ]; then
		echo "########### ERROR ##########"
                echo "$BOX site can't be installed at this time."
                echo -e "Please check /root/node_installer/conf/DONT_TOUCH_LIST \n\n"
                continue
        fi

	# Prepare DsP-Installer
	# Copy appropriate installers from installer_inventory to dsp_installer,
	# then modify parameters inside copied installers. (picker.sh)
        sudo bash $INSTALLER_PATH/installer_inventory/picker.sh $BOX
done

# Do real provisioning procedures
# By now, all required installers are prepared inside dsp_installer directory.
# Therefore, dsp_installer automates Playground	provisioning by excuting
# prepared installers one by one.
sudo bash $INSTALLER_PATH/dsp_installer/dsp_installer.sh


END_TIME=$(date +%s)

echo ""
echo ""
echo ""
echo "######################################################################################"
echo ""
echo "   OpenStack Cloud Construction takes $(($END_TIME - $START_TIME)) seconds to finish"
echo ""
echo "######################################################################################"


####  Wrap-Up Part ####
#	sudo bash "${INSTALLER_PATH}/dsp_installer/clean.sh"
####

