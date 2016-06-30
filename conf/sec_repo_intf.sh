#!/bin/bash 

if [ $# -ne 2 ]; then
	echo "Usage sec_repo_intf.sh <encrypt|decrypt> <file_name>"
	exit -1
fi

if [ $1 == "encrypt" ]; then
	if [ ! -f $2 ]; then
		echo "File $2 for Encryption is not exists"
		exit -1
	fi
	USR=`gpg --list-keys | grep uid | awk '{print $NF}'`

	if [ -n $USR ]; then
		echo "You should generate your key before using Secured Repository"
		echo "Command: gpg --gen-key"
		exit -1
	fi

	gpg --output $2.gpg --encrypt --recipient $USR  $2

elif [ $1 == "decrypt" ]; then
	if [ ! -f $2 ]; then
		echo "File $2 for Decryption is not exists"
		exit -1
	fi
	DEC_FILE=`echo $2 | sed "s/.gpg//g"`
	gpg --output $DEC_FILE --decrypt $2

else
	echo "Usage sec_repo_intf.sh <encrypt|decrypt> <file_name>"
	exit -1
fi
