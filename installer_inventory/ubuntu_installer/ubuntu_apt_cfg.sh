
rm /etc/apt/apt.conf

#sed -i "s/kr.archive.ubuntu.com/172.30.90.9/g" /etc/apt/sources.list
#sed -i "s/security.ubuntu.com/172.30.90.9/g" /etc/apt/sources.list

sed -i "s/172.30.90.9/ftp.daum.net/g" /etc/apt/sources.list

apt-get update
apt-get install -f sshpass

######################  ubuntu_apt_cfg.sh  #############################
########################################################################

