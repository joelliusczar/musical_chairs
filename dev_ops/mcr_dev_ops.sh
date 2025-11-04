#!/bin/sh


deploy_app() (
	ansible-playbook deploy_api.yml -i ~/.ansible/inventories/musical_chairs  --ask-vault-pass -K
)

deploy_vm_app() (
	ansible-playbook deploy_api.yml -i ~/.ansible/inventories/vms_inv  --ask-vault-pass -K
)

deploy_local_app() (
	ansible-playbook startup_api.yml -i ~/.ansible/inventories/testing  --ask-vault-pass -K
)

# app_name='musical_chairs'
# 	mkdir -p "../test_trash/${app_name}" &&
# 	rsync -avP --del ./files "../test_trash/${app_name}"  &&
# 	mkdir -p "../test_trash/${app_name}/ices_configs" &&
# 	mkdir -p "../test_trash/${app_name}/pyModules" &&
# 	rsync -avP --del ../sql_scripts "../test_trash/${app_name}"  &&

setup_tests() (
	ansible-playbook run_test_setup.yml --skip-tags  entitled
)

setup_schedules() (
	ansible-playbook run_schedule_setup.yml -i ~/.ansible/inventories/musical_chairs  --ask-vault-pass -K
)


command="$1"
shift
"$command"
