#!/bin/sh


deploy_api() (
	ansible-playbook deploy_api.yml -i ~/.ansible/inventories/musical_chairs  --ask-vault-pass -K
)

command="$1"
shift
"$command"
