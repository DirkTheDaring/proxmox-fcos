#!/usr/bin/env bash
set -x
DIRNAME=$(dirname "$0")
cd "$DIRNAME"

# determine config_stage and config_name from filename
BASENAME=$(basename -s .sh "$0")

# sequence matters, config_name and config_stage need to be set first!
ansible-playbook playbook-hosts.yaml \
	-i inventory/all.yaml \
	-i inventory/cluster.yaml \
	$*
