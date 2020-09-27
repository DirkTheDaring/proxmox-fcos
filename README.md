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

