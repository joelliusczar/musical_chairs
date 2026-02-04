#!/bin/sh


meName="mcr_dev_ops.sh"
isSourced=0
[ "${0##*/}" != "${meName}" ] && isSourced=1

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


replace_local_db() (
	ansible-playbook replace_local_db.yml -i ~/.ansible/inventories/testing --ask-vault-pass -K
)


print_db_schema() (
	cd ../src/musical_chairs_libs/one_offs
	python_exe='../../../test_trash/musical_chairs/mcr_env/bin/python'
	"$python_exe" -m db_print
)


pyenv() {
	cd ..
	export PATH="$(pwd)/test_trash/musical_chairs/mcr_env/bin/:${PATH}"
	. test_trash/musical_chairs/mcr_env/bin/activate
}


add_migration() (
	cd ..
	alembic_exe='test_trash/musical_chairs/mcr_env/bin/alembic'
	"$alembic_exe" revision --autogenerate -m "$1"
)


blank_migration() (
	cd ..
	alembic_exe='test_trash/musical_chairs/mcr_env/bin/alembic'
	"$alembic_exe" revision -m "$1"
)


apply_migrations() (
	cd ..
	alembic_exe='test_trash/musical_chairs/mcr_env/bin/alembic'
	"$alembic_exe" upgrade head
)


gen_sql() (
	cd ..
	alembic_exe='test_trash/musical_chairs/mcr_env/bin/alembic'
	"$alembic_exe" upgrade head --sql
)


if [ $isSourced = 0 ]; then
	command="$1"
	shift
	"$command" "$@"
fi