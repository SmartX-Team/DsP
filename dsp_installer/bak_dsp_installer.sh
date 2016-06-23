#!/bin/bash

TARGET=$1
SW_LIST=$2

if [ -z $TARGET or ! -f "./${TARGET}.sh" ]; then
	exit
fi

source `pwd`/../../../conf/${TARGET}

sleep 450

while true; do
	TARGET_IP=

	sleep 30
	if [ -z $TARGET_IP ]; then
		ping $MGMT_IP_ADDRESS -w 1 > /dev/null

		if [ $? -eq 0 ]; then
			TARGET_IP=$MGMT_IP_ADDRESS
		else
			ping $DATA_IP_ADDRESS -w 1 > /dev/null

			if [ $? -eq 0 ]; then
				TARGET_IP=$DATA_IP_ADDRESS
			else
				ping $CTRL_IP_ADDRESS -w 1 > /dev/null

				if [ $? -eq 0]; then
					TARGET_IP=$CTRL_IP_ADDRESS
				else
					continue
				fi
			fi
		fi
	fi

	scp ubuntu@${TARGET_IP}:~/.box_status ./.${TARGET}_box_status

	if [ -n ./.${TARGET}_box_status and `echo ./.inst_status` == "configuration done" ]; then
		break
	fi
done

ssh-copy-id -i ~/.ssh/id_rsa.pub ${DEFAULT_ACCOUNT}@${MGMT_IP_ADDRESS} <<EOF
	$PASSWD
EOF

if [ -n $SW_LIST ]; then

	CHECK=`echo $SW_LIST | awk '{print tolower($0)' |  grep openstack`
	if [ -n $CHECK ]; then
		scp -oStrictHostKeyChecking=no -oCheckHostIP=no `pwd`/${TARGET}_openstack.sh  tein@$MGMT_IP_ADDRESS:~/${TARGET}_openstack.sh
		ssh tein@$MGMT_IP_ADDRESS "sudo bash ~/${TARGET}_openstack.sh"
	fi

#	for SW in $SW_LIST; do
#		echo "** Install software $SW into $TARGET SmartX Box"
#		SW_LOW=`echo $SW | awk '{print tolower($0)}'`
#		scp 
#		bash `pwd`/${TARGET}_${SW_LOW}.sh
#	done

fi
