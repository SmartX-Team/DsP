# Container Box Installer

### Description
LXD Installer automatically creates a LXD machine container, called Container Box or cBox, inside the target box.

The machine container acts as an individual box which contains full operating system environment 
like virtual machine. So we can use cBox in the same way to virtual machine or even bare-metal machine.

LXD Installer operates on **Post Box** which is in charge of managing other boxes in the cluster. 
And the Installer create **LXD cBox** on **target host box** according to the given template.  

### Supporting Software Installation
- LXD Container

### Prerequisite
- Install LXD on Post Box
~~~~
PostBox:~$ sudo apt install lxd
PostBox:~$ sudo lxd init
~~~~

- Install and Configure LXD on Target Tox
~~~~
TargetBox:~$ sudo apt install lxd
TargetBox:~$ sudo lxd init

(Configure below parameter correctly)
Would you like LXD to be available over the network (yes/no) [default=no]? yes
Trust password for new clients: <PASSWORD_FOR_REMOTE_ACCESS>
~~~~

- Copy a public key of Post Box to Target Box
~~~~
PostBox:~$ ssh-keygen -f ~/.ssh/id_rsa -t rsa -N ''
PostBox:~$ ssh-copy-id <TARGET_BOX_ACCOUNT>@<TARGET_BOX_IP>
~~~~

### Required Software
> #### Post Box
> - pylxd (Python Package)
> - ipaddress (Python Package)

> #### for Target Box
> - LXD

### How to write Template
~~~~
- name: <cbox_name>
  software:
    - name: "linux"
      installer: "lxd"
      opt:
        image: <lxd_image>
        trust_password: <password>
~~~~

### References
- https://www.ubuntu.com/containers/lxd
- https://lxd.readthedocs.io/en/latest/
- https://github.com/lxc/pylxd

### Contact
- If you have any questions related with this installer, please send me a e-mail or create an issue.
- jsshin_at_smartx.kr (Jun-Sik Shin)
- Networked Computing Systems Laboratory in GIST, South Korea.