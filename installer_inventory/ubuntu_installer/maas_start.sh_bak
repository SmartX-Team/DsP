#!/bin/bash

MAAS_ID="root"
BOX="<BOX_NAME>"
#INSTALLER_TYPE=$3

INSTALLER_PATH="${HOME}/dsp_installer"
CONF_DIR="${INSTALLER_PATH}/conf"
source "${CONF_DIR}/${BOX}"

#FIND TARGET NODE SYSTEM ID
TARGET_SYSTEM_ID=$( sudo maas $MAAS_ID nodes list hostname=$BOX | grep system_id | awk '{print $2}')
TARGET_SYSTEM_ID=$( echo $TARGET_SYSTEM_ID | sed "s/\"//g" | sed "s/,//g" )
echo -e "$BOX Node System ID : $TARGET_SYSTEM_ID \n"


# GET THE STATUS OF TARGET NODE
# POSSIBLE NODE STATUS
# DECLARED = 0, COMMISSIONING = 1, FAILED_TESTS = 2,
# MISSING = 3, READY = 4, RESERVED = 5,
# ALLOCATED = 6, RETIRED = 7
# 
# REFER : http://maas.ubuntu.com/docs/enum.html#maasserver.models.NODE_STATUS

BOX_STATUS=$( sudo maas $MAAS_ID nodes list hostname=$BOX | grep \"status\"| awk '{print $2}' | sed "s/,//g" )

echo "BOX_STATUS $BOX_STATUS haha"
# IF THE NODE IS ALREADY ALLOCATED, NEED TO CHANGE THE STATUS TO READY
if [ $BOX_STATUS == 6 ]; then
	echo "in the poweroff"
	TARGET_IP=$(cat ${INSTALLER_PATH}/conf/${BOX}  | grep DATA_IP_ADDRESS | sed "s/DATA_IP_ADDRESS=//g")
	CHECK=$(ping -c 1 ${TARGET_IP} | grep Unreachable)

	if [ "${CHECK:-null}" == null ]; then
		echo "ssh to $TARGET_IP"
		sudo ssh -oStrictHostKeyChecking=no -oCheckHostIP=no ubuntu@$TARGET_IP sudo shutdown -h now
		sleep 15
	fi

	sudo maas $MAAS_ID node stop $TARGET_SYSTEM_ID
	sleep 3
	sudo maas $MAAS_ID node release $TARGET_SYSTEM_ID
	
	while [ 1 ]; do
		sleep 2
		BOX_STATUS=$(sudo maas $MAAS_ID nodes list hostname=$BOX | grep \"status\" | awk '{print $2}' | sed "s/,//g")

		if [ $BOX_STATUS == 4 ]; then
			break
		fi
	done

# IF THE TARGET NODE IS EVEN NOT COMMISSIONED, NEED TO COMMISSION
elif [ $BOX_STATUS == 0 ]; then
	echo "$BOX : In DECLARED status"
	echo "$BOX : Needed to commission"
	
	sudo maas $MAAS_ID node commission $TARGET_SYSTEM_ID
	echo "$BOX : Start to commission"
	

# IF THE NODE STATUS ISN'T IN DECLARED, READY OR ALLOCATED, WE CAN'T MANAGE IT
elif [ $BOX_STATUS != 4 ]; then
	echo "$BOX : Current Node status can't be treated. STATUS $BOX_STATUS"
	exit
fi



if [ $BOX_STATUS == 1 ]; then
	while [ 1 ]; do
        
	        sleep 10

                BOX_STATUS= $( sudo maas $MAAS_ID nodes list hostname=$BOX | grep status| awk '{print $2}' | sed "s/,//g" )

                if [ $BOX_STATUS == 4]; then
                        break
                fi
        done

fi

# WHEN UPPER CONDITION STATEMENTS WERE PASSED SUCCESSFULLY, IT IS READY TO INSTALL OS
if [ $BOX_STATUS == 4 ]; then
	echo "$BOX is started to install OS"
	sudo maas $MAAS_ID nodes acquire system_id=$TARGET_SYSTEM_ID > /dev/null
	sudo maas $MAAS_ID node start $TARGET_SYSTEM_ID > /dev/null

	# WAIT UNTIL FINISHING INSTALL PROCESS
#	while [ 1 ]; do
#		sleep 10
#		RES_PING=$(ping $DATA_IP_ADDRESS -c 1 -W 1 | grep "time=")
#		echo "ADDR = $DATA_IP_ADDRESS"
#		if [ "${RES_PING-:null}" != null ]; then
#			break
#		fi
#	done
	echo "###########################################################"
	echo "Provisioning Procedure for the $BOX Box is started."
	echo -e "###########################################################\n\n"
fi
