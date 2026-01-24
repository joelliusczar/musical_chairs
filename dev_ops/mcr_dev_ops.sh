#!/bin/sh


deploy_app() (
	ansible-playbook deploy_api.yml -i ~/.ansible/inventories/musical_chairs  --ask-vault-pass -K
)


setup_new_box_vm() (
	ansible-playbook new_box.yml -i ~/.ansible/inventories/vms_inv  --ask-vault-pass -K
)


setup_new_box() (
	ansible-playbook new_box.yml -i ~/.ansible/inventories/musical_chairs  --ask-vault-pass -K
)


deploy_app_vm() (
	ansible-playbook deploy_api.yml -i ~/.ansible/inventories/vms_inv  --ask-vault-pass -K
)


setup_schedules_vm() (
	ansible-playbook setup_schedules.yml -i ~/.ansible/inventories/vms_inv  --ask-vault-pass
)


deploy_local_app() (
	ansible-playbook startup_api.yml -i ~/.ansible/inventories/testing  --ask-vault-pass -K
)


deploy_local_radio() (
	ansible-playbook setup_radio.yml -i ~/.ansible/inventories/testing  --ask-vault-pass -K
)


setup_tests() (
	ansible-playbook setup_tests.yml --skip-tags  entitled
)


setup_schedules() (
	ansible-playbook run_schedule_setup.yml -i ~/.ansible/inventories/musical_chairs  --ask-vault-pass -K
)


print_db_hash() (
	cd ../src/musical_chairs_libs/one_offs
	python_exe='../../../test_trash/musical_chairs/mcr_env/bin/python'
	"$python_exe" -m db_print --hash
)


regen_reference_file() (
	cd ../src/musical_chairs_libs/one_offs
	python_exe='../../../test_trash/musical_chairs/mcr_env/bin/python'
	"$python_exe" -m regen_file_reference_file
)


replace_local_db() (
	ansible-playbook replace_local_db.yml -i ~/.ansible/inventories/testing --ask-vault-pass -K
)


command="$1"
shift
"$command"
