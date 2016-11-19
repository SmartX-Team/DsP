HOSTNAME=K1-GJ1-Small1
USER_ACCOUNT=netcs
PASSWD='netcs007bang'

MGMT_GATEWAY=116.89.190.1
MGMT_DNS_NAMESERVER=8.8.8.8

MGMT_IP_ADDRESS=116.89.190.113
MGMT_IP_SUBNET=255.255.255.0
MGMT_MAC_ADDRESS=0c:c4:7a:ca:3b:f2

DATA_IP_ADDRESS=172.30.190.113
DATA_IP_SUBNET=255.255.0.0
DATA_MAC_ADDRESS=0c:c4:7a:ca:58:8b

CTRL_IP_ADDRESS=172.20.190.113
CTRL_IP_SUBNET=255.255.0.0
CTRL_MAC_ADDRESS=0c:c4:7a:ca:3b:f3

passwd root << EOF
$PASSWD
$PASSWD
EOF

adduser $USER_ACCOUNT <<EOF
$PASSWD
$PASSWD
EOF

echo "${USER_ACCOUNT}	ALL=(ALL)	NOPASSWD:ALL" >> /etc/sudoers

##################  ubuntu_account_cfg.sh  #############################
########################################################################

source /root/conf	
NET_CONF_FILE="/etc/network/interfaces"

DATA_INTERFACE=$(ifconfig -a | grep $DATA_MAC_ADDRESS | awk '{print $1}')
MGMT_INTERFACE=$(ifconfig -a | grep $MGMT_MAC_ADDRESS | awk '{print $1}')
CTRL_INTERFACE=$(ifconfig -a | grep $CTRL_MAC_ADDRESS | awk '{print $1}')

echo -e "auto lo" > $NET_CONF_FILE
echo -e "iface lo inet loopback" >> $NET_CONF_FILE               
echo -e "\n"                                                            

echo -e "auto $MGMT_INTERFACE" >> $NET_CONF_FILE                 
echo -e "iface $MGMT_INTERFACE inet static" >> $NET_CONF_FILE    
echo -e "\\taddress $MGMT_IP_ADDRESS" >> $NET_CONF_FILE          
echo -e "\\tnetmask $MGMT_IP_SUBNET" >> $NET_CONF_FILE           
echo -e "\\tgateway $MGMT_GATEWAY" >> $NET_CONF_FILE             
echo -e "\\tdns-nameservers $MGMT_DNS_NAMESERVER" >> $NET_CONF_FILE      
echo -e "\n"                                                            

echo -e "auto $DATA_INTERFACE" >> $NET_CONF_FILE                 
echo -e "iface $DATA_INTERFACE inet static" >> $NET_CONF_FILE    
echo -e "\\taddress $DATA_IP_ADDRESS" >> $NET_CONF_FILE          
echo -e "\\tnetmask $DATA_IP_SUBNET\\n" >> $NET_CONF_FILE        
echo -e "\n"                                                            

echo -e "auto $CTRL_INTERFACE" >> $NET_CONF_FILE                 
echo -e "iface $CTRL_INTERFACE inet static" >> $NET_CONF_FILE    
echo -e "\\taddress $CTRL_IP_ADDRESS" >> $NET_CONF_FILE          
echo -e "\\tnetmask $CTRL_IP_SUBNET\\n" >> $NET_CONF_FILE        
echo -e "\n"                                                            

route del default 
ifup $MGMT_INTERFACE
ifup $CTRL_INTERFACE
ifup $DATA_INTERFACE

######################  ubuntu_net_cfg.sh  #############################
########################################################################


rm /etc/apt/apt.conf

#sed -i "s/kr.archive.ubuntu.com/172.30.90.9/g" /etc/apt/sources.list
#sed -i "s/security.ubuntu.com/172.30.90.9/g" /etc/apt/sources.list

sed -i "s/172.30.90.9/ftp.daum.net/g" /etc/apt/sources.list

apt-get update
apt-get install -f sshpass

######################  ubuntu_apt_cfg.sh  #############################
########################################################################


echo "#!/bin/bash -e" > /etc/rc.local
echo "exit 0" >> /etc/rc.local
date >> /root/test_time
##################  ubuntu_add_cfg.sh  #############################
####################################################################

