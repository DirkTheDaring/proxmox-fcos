# proxmox-fcos
proxmox fedora coreos installer

# flash all images
run-name-stage.sh  -e 'flash=*'  

# flash only nodes
run-name-stage.sh  -e 'flash=*node*'  

# flash specific nodes
run-name-stage.sh  -e 'flash=node1,node2,master1'  

# ADD the destroy flag to destroy the virtual machine and re-create it 
run-name-stage.sh  -e 'flash=*' -e destroy=true

# Install fcos from channel testing
run-name-stage     -e 'flash=*' -e 'destroy=true' -e 'fcos_channel=testing'

# use tagging to just starte one module
run-name-stage --tags=packages
run-name-stage --tags=quirks



### pve-edge-kernel
The repository for latest kernel builds is integrated, but an edge kernel is NOT automatically installed

VERSION=5.12
apt update
apt install pve-kernel-${VERSION}-edge

