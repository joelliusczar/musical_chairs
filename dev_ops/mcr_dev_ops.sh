#!/bin/sh


deploy_api() (
	ansible-playbook deploy_api.yml -i ~/.ansible/inventories/musical_chairs  --ask-vault-pass -K
)

deploy_local_api() (
	ansible-playbook startup_api.yml -i ~/.ansible/inventories/testing  --ask-vault-pass -K
)

# app_name='musical_chairs'
# 	mkdir -p "../test_trash/${app_name}" &&
# 	rsync -avP --del ./files "../test_trash/${app_name}"  &&
# 	mkdir -p "../test_trash/${app_name}/ices_configs" &&
# 	mkdir -p "../test_trash/${app_name}/pyModules" &&
# 	rsync -avP --del ../sql_scripts "../test_trash/${app_name}"  &&

setup_tests() (
	ansible-playbook test_setup.yml --skip-tags  entitled
)

command="$1"
shift
"$command"
