#!/bin/sh
DIRNAME="$(dirname $0)"
cd "$DIRNAME"

CONFIG_NAME=fritz.box
CONFIG_STAGE=prod
CONFIG="-e config_name=$CONFIG_NAME -e config_stage=$CONFIG_STAGE"
ansible-playbook playbook.yaml -i inventory.yaml $CONFIG "${@}"
