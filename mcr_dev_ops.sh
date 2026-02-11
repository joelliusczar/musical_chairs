#!/bin/sh


meName="mcr_dev_ops.sh"
isSourced=0
[ "${0##*/}" != "${meName}" ] && isSourced=1

deploy_app() (
	ansible-playbook dev_ops/deploy_api.yml -i ~/.ansible/inventories/musical_chairs  --ask-vault-pass -K
)


setup_new_box_vm() (
	ansible-playbook dev_ops/new_box.yml -i ~/.ansible/inventories/vms_inv  --ask-vault-pass -K
)


setup_new_box() (
	ansible-playbook dev_ops/new_box.yml -i ~/.ansible/inventories/musical_chairs  --ask-vault-pass -K
)


deploy_app_vm() (
	ansible-playbook dev_ops/deploy_api.yml -i ~/.ansible/inventories/vms_inv  --ask-vault-pass -K
)


setup_schedules_vm() (
	ansible-playbook dev_ops/setup_schedules.yml -i ~/.ansible/inventories/vms_inv  --ask-vault-pass
)


deploy_local_app() (
	ansible-playbook dev_ops/startup_api.yml -i ~/.ansible/inventories/testing  --ask-vault-pass -K
)


deploy_local_radio() (
	ansible-playbook dev_ops/setup_radio.yml -i ~/.ansible/inventories/testing  --ask-vault-pass -K
)


update_db() (
	ansible-playbook dev_ops/update_db.yml --skip-tags  entitled
)


setup_schedules() (
	ansible-playbook dev_ops/run_schedule_setup.yml -i ~/.ansible/inventories/musical_chairs  --ask-vault-pass -K
)


replace_local_db() (
	ansible-playbook dev_ops/replace_local_db.yml -i ~/.ansible/inventories/testing --ask-vault-pass -K
)


print_db_schema() (
	cd src/musical_chairs_libs/one_offs
	python_exe='../../../test_trash/musical_chairs/mcr_env/bin/python'
	"$python_exe" -m db_print
)


add_migration() (
	alembic_exe='test_trash/musical_chairs/mcr_env/bin/alembic'
	"$alembic_exe" revision --autogenerate -m "$1"
)


blank_migration() (
	alembic_exe='test_trash/musical_chairs/mcr_env/bin/alembic'
	"$alembic_exe" revision -m "$1"
)


apply_migrations() (
	alembic_exe='test_trash/musical_chairs/mcr_env/bin/alembic'
	"$alembic_exe" upgrade head
)


gen_sql() (
	cd ..
	alembic_exe='test_trash/musical_chairs/mcr_env/bin/alembic'
	"$alembic_exe" upgrade head --sql
)


pyenv() {
	export PATH="$(pwd)/test_trash/musical_chairs/mcr_env/bin/:${PATH}"
	. test_trash/musical_chairs/mcr_env/bin/activate
}


app_py() {
	test_trash/musical_chairs/mcr_env/bin/python
}


s3_move() {
	cd src/musical_chairs_libs/one_offs
	python_exe='../../../test_trash/musical_chairs/mcr_env/bin/python'
	"$python_exe" -m s3_move
}


if [ $isSourced = 0 ]; then
	command="$1"
	shift
	"$command" "$@"
fi