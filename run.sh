#!/usr/bin/env bash
set -x
DIRNAME=$(dirname "$0")
cd "$DIRNAME"

# determine config_stage and config_name from filename
BASENAME=$(basename "$0")
CONFIG_NAME=$(awk '-F[.-]' '{ print $2}' <<<"$BASENAME")
CONFIG_STAGE=$(awk '-F[.-]' '{ print $3}' <<<"$BASENAME")

# checking
if [ -z "$CONFIG_NAME" ]; then 
  echo "CONFIG_NAME could not be determined."
  exit 1
fi

if [ -z "$CONFIG_STAGE" ]; then 
  echo "CONFIG_STAGE could not be determined."
  exit 1
fi

if [ ! -d "inventory/$CONFIG_STAGE" ]; then
  echo  "inventory/$CONFIG_STAGE is not a directory."
  exit 1  
fi

ansible-playbook playbook.yaml \
	-i inventory/all.yaml \
	-i inventory/cluster.yaml \
	-i inventory/fcos.yaml \
	-i inventory/$CONFIG_STAGE/inventory.yaml \
        -e config_name=$CONFIG_NAME \
	-e config_stage=$CONFIG_STAGE \
	$CONFIG \
	$*
