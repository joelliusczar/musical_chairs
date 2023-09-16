#!/bin/sh

if [ -e ./radio_common.sh ]; then
	radioCommonPath='./radio_common.sh'
elif [ -e ../radio_common.sh]; then
	radioCommonPath='../radio_common.sh'
elif [ -e "$HOME"/radio/radio_common.sh]; then
	radioCommonPath="$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

. "$radioCommonPath"

process_global_vars "$@" ||
show_err_and_exit "error with global variabls"

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

run_unit_tests
unitTestSuccess="$?"


#Would have prefered to just use a variable
#but it seems to choke on certain characters like ')' for some reason
#when I do it like
#myVar=$(cat<<EOF
#...
#)
mkfifo clone_repo_fifo script_select_fifo remote_cleanup_fifo \
	remote_script_fifo



#clone repo
#we need this section to resolve its variables remotely on the server
{ cat <<'RemoteScriptEOF1'
#in addition to setting up any utilizing any passed in params
#we call process_global_vars to also set up directories
process_global_vars "$@" ||
show_err_and_exit "error with global variabls"
echo "$SSH_CONNECTION"
[ -n "$SSH_CONNECTION" ] ||
show_err_and_exit "This section should only be run remotely"

if ! git --version 2>/dev/null; then
	install_package git
fi

error_check_path "$(get_repo_path)" &&
rm -rf "$(get_repo_path)" &&
#since the clone will create the sub dir, we'll just start in the parent
cd "$appRoot"/"$BUILD_DIR" &&
git clone "$radioServerRepoUrl" "$projName" &&
cd "$projName"  &&
if [ "$currentBranch" != main ]; then
	echo "Using branch ${currentBranch}"
	git checkout -t origin/"$currentBranch" || exit 1
fi
cd "$appRoot"
RemoteScriptEOF1
} > clone_repo_fifo &

#select which setup script to run
{ cat<<RemoteScriptEOF2

export diagFlag="$diagFlag" &&
export expName="$expName" &&
export S3_ACCESS_KEY_ID="$S3_ACCESS_KEY_ID" &&
export S3_SECRET_ACCESS_KEY="$S3_SECRET_ACCESS_KEY" &&
export PB_SECRET=$(get_pb_secret)
export PB_API_KEY=$(get_pb_api_key)
export APP_AUTH_KEY=$(get_mc_auth_key)

if [ "$setupLvl" = 'api' ]; then
	echo "$setupLvl"
	(exit "$unitTestSuccess") &&
	. ./radio_common.sh &&
	sync_utility_scripts &&
	startup_api
elif [ "$setupLvl" = 'client' ]; then
	echo "$setupLvl"
	. ./radio_common.sh &&
	sync_utility_scripts &&
	setup_client &&
	echo "finished setup"
elif [ "$setupLvl" = 'radio' ]; then
	echo "$setupLvl"
	(exit "$unitTestSuccess") &&
	. ./radio_common.sh &&
	sync_utility_scripts &&
	startup_radio
elif [ "$setupLvl" = 'install' ]; then
	echo "$setupLvl"
	sh ./install_setup.sh &&
	echo "finished setup"
else
	echo "$setupLvl"
	. ./radio_common.sh &&
	sync_utility_scripts &&
	echo "finished setup"
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

	radioServerRepoUrl="$radioServerRepoUrl"
	currentBranch="$(git branch --show-current 2>/dev/null)"

	$(cat clone_repo_fifo)

	$(cat script_select_fifo)

	$(cat remote_cleanup_fifo)

)

scope $global_args

RemoteScriptEOF4
} > remote_script_fifo &


ssh -i "$radio_key_file" "$radio_server_ssh_address" \
	'bash -s' < remote_script_fifo &&
echo "All done" || echo "Onk!"

rm -f remote_script_fifo remote_cleanup_fifo
rm -f radio_common_fifo clone_repo_fifo script_select_fifo






