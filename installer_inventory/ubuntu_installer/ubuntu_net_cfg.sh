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

