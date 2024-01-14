#!/bin/sh

if [ -e ./radio_common.sh ]; then
	radioCommonPath='./radio_common.sh'
elif [ -e ../radio_common.sh ]; then
	radioCommonPath='../radio_common.sh'
elif [ -e "$HOME"/radio/radio_common.sh ]; then
	radioCommonPath="$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

#this is included locally. Any changes here are not going to be on the server
#unless they've been pushed to the repo
. "$radioCommonPath"


process_global_vars "$@" ||
show_err_and_exit "local error with global variables"

deployment_local_env_check ||
show_err_and_exit "local error with missing keys"

if [ -n "$(git status --porcelain)" ]; then
	echo "There are uncommited changes that will not be apart of the deploy"
	echo "continue?"
	read c
	if [ "$c" = 'n' ] || [ "$c" = 'N' ]; then
		echo 'Canceling action'
		exit
	fi
fi

git fetch
if [ "$(git rev-parse @)" != "$(git rev-parse @{u})" ]; then
	echo "remote branch may not have latest set of commits"
	echo "continue?"
	read c
	if [ "$c" = 'n' ] || [ "$c" = 'N' ]; then
		echo 'Canceling action'
		exit
	fi
fi

if ! str_contains "$__SKIP__" 'unit_tests'; then
	run_unit_tests
fi
unitTestSuccess="$?"


#Would have prefered to just use a variable
#but it seems to choke on certain characters like ')' for some reason
#when I do it like
#myVar=$(cat<<EOF
#...
#)
mkfifo env_var_fifo clone_repo_fifo script_select_fifo remote_cleanup_fifo \
	remote_script_fifo


{ cat<<RemoteScriptEOF0


export expName="$expName" &&
export AWS_ACCESS_KEY_ID=$(__get_s3_api_key__) &&
export AWS_SECRET_ACCESS_KEY=$(__get_s3_secret__) &&
export S3_ACCESS_KEY_ID=$(__get_s3_api_key__) &&
export S3_SECRET_ACCESS_KEY=$(__get_s3_secret__) &&
export PB_SECRET=$(__get_pb_secret__) &&
export PB_API_KEY=$(__get_pb_api_key__) &&
export MC_AUTH_SECRET_KEY=$(__get_mc_auth_key__) &&
export MC_DATABASE_NAME='musical_chairs_db';
export __DB_SETUP_PASS__=$(__get_db_setup_key__) &&
export MC_DB_PASS_OWNER=$(__get_db_owner_key__) &&
export MC_DB_PASS_API=$(__get_api_db_user_key__) &&
export MC_DB_PASS_RADIO=$(__get_radio_db_user_key__) &&
export S3_BUCKET_NAME=$(__get_s3_bucket_name__) &&
export S3_REGION_NAME=$(__get_s3_region_name__) &&
export __ICES_BRANCH__=$(__get_ices_branch__) &&


RemoteScriptEOF0
} > env_var_fifo &

#clone repo
#we need this section to resolve its variables remotely on the server
{ cat <<'RemoteScriptEOF1'
echo "SSH connection? ${SSH_CONNECTION}"
[ -n "$SSH_CONNECTION" ] ||
show_err_and_exit "This section should only be run remotely"
#in addition to setting up any utilizing any passed in params
#we call process_global_vars to also set up directories
process_global_vars "$@" ||
show_err_and_exit "error with global variables on server"

deployment_server_env_check ||
show_err_and_exit "error with missing keys on server"

create_install_directory &&

if ! git --version 2>/dev/null; then
	install_package git
fi

error_check_path "$(get_repo_path)" &&
rm -rf "$(get_repo_path)" &&
#since the clone will create the sub dir, we'll just start in the parent
cd "$(__get_app_root__)"/"$MC_BUILD_DIR" &&
git clone "$MC_REPO_URL" "$MC_PROJ_NAME" &&
cd "$MC_PROJ_NAME"  &&
if [ "$currentBranch" != main ]; then
	echo "Using branch ${currentBranch}"
	git checkout -t origin/"$currentBranch" || exit 1
fi
cd "$(__get_app_root__)"
RemoteScriptEOF1
} > clone_repo_fifo &

#select which setup script to run
{ cat<<RemoteScriptEOF2


if is_ssh; then
	sync_utility_scripts
	echo 'radio_common hash:'
	get_hash_of_file './radio_common.sh'
	if [ "$__SETUP_LVL__" = 'api' ]; then
		echo "$__SETUP_LVL__"
		(exit "$unitTestSuccess") &&
		. ./radio_common.sh &&
		startup_api
	elif [ "$__SETUP_LVL__" = 'client' ]; then
		echo "$__SETUP_LVL__"
		. ./radio_common.sh &&
		setup_client &&
		echo "finished setup"
	elif [ "$__SETUP_LVL__" = 'radio' ]; then
		echo "$__SETUP_LVL__"
		(exit "$unitTestSuccess") &&
		. ./radio_common.sh &&
		startup_radio
	elif [ "$__SETUP_LVL__" = 'install' ]; then
		echo "$__SETUP_LVL__"
		. ./radio_common.sh &&
		run_initial_install_script
		echo "finished setup"
	else
		echo "$__SETUP_LVL__"
		. ./radio_common.sh &&
		sync_utility_scripts &&
		echo "finished setup"
	fi
fi

RemoteScriptEOF2
} > script_select_fifo &

#we need this section to also resolve its variables remotely on the server
{
cat<<'RemoteScriptEOF3'
exitCode="$?"

echo 'Done Server side'
(exit "$exitCode")
RemoteScriptEOF3
} > remote_cleanup_fifo &

{
	cat<<RemoteScriptEOF4
$(cat "$radioCommonPath")
scope() (

	MC_REPO_URL="$MC_REPO_URL"
	currentBranch="$(git branch --show-current 2>/dev/null)"

	$(cat env_var_fifo)

	$(cat clone_repo_fifo)

	$(cat script_select_fifo)

	$(cat remote_cleanup_fifo)

)

scope $global_args

RemoteScriptEOF4
} > remote_script_fifo &

echo "connectiong to $(__get_address__) using $(__get_id_file__)"
ssh -i $(__get_id_file__) "root@$(__get_address__)" \
	'bash -s' < remote_script_fifo &&
echo "All done" || echo "Onk!"

rm -f env_var_fifo remote_script_fifo remote_cleanup_fifo
rm -f radio_common_fifo clone_repo_fifo script_select_fifo






