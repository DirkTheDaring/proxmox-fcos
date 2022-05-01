#!/usr/bin/bash
set -eux
BASENAME=$(basename -s .sh "$0")
ARRAY=(${BASENAME//-/ })

ACTION=${ARRAY[0]}
CONFIG_NAME=${ARRAY[1]}
CONFIG_STAGE=${ARRAY[2]}

[[ "${ARRAY[0]}" == run  ]] && ACTION=ansible-playbook  TARGET=playbook.yaml
[[ "${ARRAY[0]}" == test ]] && ACTION=ansible-inventory TARGET=--list

LIST=($(cat<<EOF
inventory/all.yaml
inventory/groups-kubespray.yaml
inventory/groups-proxmox.yaml
inventory/groups-available.config
inventory/proxmox_hosts.yaml
inventory/proxmox_guests.yaml
inventory/groups-assembler.config
EOF
))

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

