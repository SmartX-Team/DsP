#!/bin/bash

# Version 0.1
# Made by SJS ( jsshin@nm.gist.ac.kr)

# "start.sh" file calls this "picker.sh" file for each box listed in PLAYGROUND_TEMPLATE
# And "Box Hostname"(e.g., GJ-C1, JJ-C1, etc) is passed as a parameter. 

##
##  Variable Definition & Initialization
##

BOX=$1

INSTALLER_PATH="${HOME}/DsP-Installer"
CONF_DIR="$INSTALLER_PATH/conf"
INVENTORY_PATH="$INSTALLER_PATH/installer_inventory"
PG_TPL="$CONF_DIR/PLAYGROUND_TEMPLATE"

##
##  Service Preparation
##

# Extract Box configuration definition from Template, and parse software lists for the box
INSTALL_SW_LIST=`cat $PG_TPL | sed -e "/TARGET_BOXES/d" -ne "/$BOX/,/}/p" | grep INSTALL_SOFTWARE | sed -e "s/INSTALL_SOFTWARE//g" -e "s/://g" | sed -e "s/	//g"`

AVAIL_SW_LIST=`cat $CONF_DIR/AVAILABLE_SOFTWARE`

echo "for Box $BOX, Software $INSTALL_SW_LIST will be installed"

# AVAILABLE_SOFTWARE file defines supported software list and its priority
# So all software should be installed in the correct order defined in the file.
for SW in $AVAIL_SW_LIST
do
	INVEN_DIR=

	CHECK=`echo $INSTALL_SW_LIST | grep -i $SW`
	if [ "${CHECK:-null}" != null ]; then
		echo "*** You chose $SW for the $BOX box"
		# Convert Capital letters to small letters	
		INVEN_DIR=`echo $SW | tr '[:upper:]' '[:lower:]'`
	else
			continue;
	fi
	
	# Some software can have multiple installer. For example, we implemented two installers,
	# one is DevStack-based installer, and another one is script-based full-version installer.
	# So, the operator can choose an installer among a couple of installers.
	CHECK=`cat $PG_TPL | sed -e "/TARGET_NODES/d" -ne "/$BOX/,/}/p" | grep -i $SW | grep -i "INSTALLER" | sed -e "s/	//g"`
	if [ "${CHECK:-null}" != null ]; then
		TMP=`echo $CHECK | sed -e "s/://g" | awk '{print $2}' | tr '[:upper:]' '[:lower:]'`
		INVEN_DIR="${INVEN_DIR}_${TMP}"
	fi

	# Each installer locates a directory named "<SOFTWARE_NAME>_<INSTALLER_TYPE>_installer"
	# For example, if you choose a software OpenStack and Full-Version installer
	# then the installer is placed in "openStack_full_installer"
	INVEN_DIR="${INVENTORY_PATH}/${INVEN_DIR}_installer"
	echo "Inventory DIR for Box $BOX: $INVEN_DIR"

	# In each installer directory, "prepare_supervisor.sh" file should be there.
	# This file does actual copy & parameter modification.
	bash $INVEN_DIR/prepare_supervisor.sh $BOX
done
