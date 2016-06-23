#!/bin/bash

# prepare_conf_scripts.sh

# In this script, scripts which cofigure the installed box environments will be copied into the maasrepo directory.
# That script will be download to installed box at the end of the OS installation process, and then downloaded scripts will be executed before showing login prompt when the box is rebooted

# Version 1.0
# Made by SJS ( jsshin@nm.gist.ac.kr)


##
##      Base Configuration Part
##

BOX=$1

INSTALLER_PATH="${HOME}/dsp_installer"
CONF_DIR="$INSTALLER_PATH/conf"
INVENTORY_PATH="$INSTALLER_PATH/installer_inventory"
PG_TPL="$CONF_DIR/PLAYGROUND_TEMPLATE"

REPO_DIR=/usr/share/maas/web/static/maasrepo
REPO_URL='http://210.114.90.8/MAAS/static/maasrepo'

##
##      Specific Service Configuration Part
##

INSTALL_SW_LIST=`cat $PG_TPL | sed -e "/TARGET_BOXES/d" -ne "/$BOX/,/}/p" | grep INSTALL_SOFTWARE | sed -e "s/INSTALL_SOFTWARE//g" -e "s/://g" | sed -e "s/	//g"`
AVAIL_SW_LIST=`cat $CONF_DIR/AVAILABLE_SOFTWARE`

echo "for Box $BOX, Software $INSTALL_SW_LIST will be installed"

for SW in $AVAIL_SW_LIST
do
	INVEN_DIR=

	CHECK=`echo $INSTALL_SW_LIST | grep -i $SW`
	if [ "${CHECK:-null}" != null ]; then
		echo "*** You chose $SW for the $BOX box"	
		INVEN_DIR=`echo $SW | tr '[:upper:]' '[:lower:]'`
	else
			continue;
	fi
	
	CHECK=`cat $PG_TPL | sed -e "/TARGET_NODES/d" -ne "/$BOX/,/}/p" | grep -i $SW | grep -i "INSTALLER" | sed -e "s/	//g"`
	if [ "${CHECK:-null}" != null ]; then
		TMP=`echo $CHECK | sed -e "s/://g" | awk '{print $2}' | tr '[:upper:]' '[:lower:]'`
		INVEN_DIR="${INVEN_DIR}_${TMP}"
	fi
	INVEN_DIR="${INVENTORY_PATH}/${INVEN_DIR}_installer"
	echo "Inventory DIR for Box $BOX: $INVEN_DIR"
	bash $INVEN_DIR/prepare_supervisor.sh $BOX
done
