#!/bin/bash

SITES=$@

UACCOUNT=`whoami`
HOMEDIR=`eval echo "~$UACCOUNT"`

GJ_CHECK=FALSE
JJ_CHECK=FALSE
PO_CHECK=FALSE
KU_CHECK=FALSE
KN_CHECK=FALSE

CHECK=`echo $SITES | grep -i all`

if [ "${CHECK:-null}" != null ]; then
	GJ_CHECK=TRUE
	JJ_CHECK=TRUE
	PO_CHECK=TRUE
	KU_CHECK=TRUE
	KN_CHECK=TRUE
else
	CHECK=`echo $SITES | grep -i gj`
	if [ "${CHECK:-null}" != null ]; then
	GJ_CHECK=TRUE	
	fi
	
	CHECK=`echo $SITES | grep -i jj`
        if [ "${CHECK:-null}" != null ]; then   
	JJ_CHECK=TRUE   
	fi
	
	CHECK=`echo $SITES | grep -i po`
        if [ "${CHECK:-null}" != null ]; then   
	PO_CHECK=TRUE   
	fi
	
	CHECK=`echo $SITES | grep -i ku`
        if [ "${CHECK:-null}" != null ]; then   
	KU_CHECK=TRUE   
	fi
	
	CHECK=`echo $SITES | grep -i kn`
        if [ "${CHECK:-null}" != null ]; then   
	KN_CHECK=TRUE   
	fi
fi

if [ $GJ_CHECK == TRUE ]; then
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 210.114.90.3
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 172.20.90.3
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 172.30.90.3
fi

if [ $JJ_CHECK == TRUE ]; then
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 210.114.90.35
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 172.20.90.35
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 172.30.90.35
fi

if [ $PO_CHECK == TRUE ]; then
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 210.114.90.67
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 172.20.90.67
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 172.30.90.67
fi

if [ $KU_CHECK == TRUE ]; then
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 210.114.90.99
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 172.20.90.99
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 172.30.90.99
fi

if [ $KN_CHECK == TRUE ]; then
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 210.114.90.131
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 172.20.90.131
	ssh-keygen -f "${HOMEDIR}/.ssh/known_hosts" -R 172.30.90.131
fi
