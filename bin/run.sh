#!/usr/bin/bash
set -eux
BASENAME=$(basename -s .sh "$0")
ARRAY=(${BASENAME//-/ })
echo "# = ${#ARRAY[@]}"

if [ ${#ARRAY[@]} == 2 ];
then
  echo "hosts!!!"
  CONFIG_NAME="fritz.box"
  CONFIG_STAGE=""
  ACTION=ansible-playbook
  TARGET=playbook-hosts.yaml
  LIST=($(cat<<EOF|grep -v ^#
inventory/${CONFIG_NAME}/all-hosts-ip.yaml
inventory/${CONFIG_NAME}/all-hosts.yaml
inventory/${CONFIG_NAME}/all-guests.yaml
inventory/${CONFIG_NAME}/groups-kubespray.yaml
inventory/${CONFIG_NAME}/groups-proxmox.yaml
inventory/${CONFIG_NAME}/groups-available.config
inventory/${CONFIG_NAME}/proxmox-hosts.yaml
inventory/${CONFIG_NAME}/proxmox-guests.yaml
inventory/${CONFIG_NAME}/groups-assembler.config
EOF
))

elif  [ ${#ARRAY[@]} -gt 2 ]; then
  CONFIG_NAME=${ARRAY[1]}
  CONFIG_STAGE=${ARRAY[2]}
  ACTION=ansible-playbook
LIST=($(cat<<EOF|grep -v ^#
inventory/${CONFIG_NAME}/all-hosts-ip.yaml
inventory/${CONFIG_NAME}/all-hosts.yaml
inventory/${CONFIG_NAME}/all-guests.yaml
inventory/${CONFIG_NAME}/groups-kubespray.yaml
inventory/${CONFIG_NAME}/groups-proxmox.yaml
inventory/${CONFIG_NAME}/groups-available.config
inventory/${CONFIG_NAME}/proxmox-hosts.yaml
inventory/${CONFIG_NAME}/proxmox-guests.yaml
inventory/${CONFIG_NAME}/groups-assembler.config
inventory/${CONFIG_NAME}/${CONFIG_STAGE}/keepalived.yaml
EOF
))
ACTION=${ARRAY[0]}

[[ "${ARRAY[0]}" == run  ]] && ACTION=ansible-playbook  TARGET=playbook.yaml
[[ "${ARRAY[0]}" == test ]] && ACTION=ansible-inventory TARGET=--list


fi


ITEMS=()
for FILEPATH in "${LIST[@]}"; do
        if [ ! -e "${FILEPATH}" ]; then
                echo "$FILEPATH not found." >&2
                exit 1
        else
                ITEMS+=(-i)
                ITEMS+=(${FILEPATH})
        fi
done

$ACTION \
        "${ITEMS[@]}"\
        -e config_name=$CONFIG_NAME \
        -e config_stage=$CONFIG_STAGE \
        "${TARGET}" \
        "$@"
