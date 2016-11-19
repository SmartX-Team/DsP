#!/bin/bash

# This scripts check whether a maas cli account already log in or not
# If you need to log in, some process for getting information about the current
# maas environment is executed. And then, "root" account will be log in
#
# Modified Date : 14.07.18
# Made and Modified by JSSHIN (jsshin@nm.gist.ac.kr)

MAAS_ID="root"

CHECK=`maas --help | grep "Interact with"`

if [ "${CHECK:-null}" != null ]; then
	PREV_ID=`echo $CHECK | awk '{print $1}'`
	echo "PREV_ID is $PREV_ID"	
	if [ $PREV_ID != $MAAS_ID ]; then
	        echo "Need to log-in $MAAS_ID"
	        API_KEY=`sudo maas-region-admin apikey --username root`
	        sudo maas login $MAAS_ID http://210.114.90.8/MAAS/api/1.0 $API_KEY
	else
	        echo "$MAAS_ID was already logined"
	fi

else
        echo "Need to log-in $MAAS_ID"
        API_KEY=`sudo maas-region-admin apikey --username root`
        sudo maas login $MAAS_ID http://210.114.90.8/MAAS/api/1.0 $API_KEY
fi

echo "####################################"
echo "Login procedure is completed"
echo "Your CLI ID : $MAAS_ID"
echo -e "####################################\n\n"

######################  maas_cli_login.sh  #############################
########################################################################
