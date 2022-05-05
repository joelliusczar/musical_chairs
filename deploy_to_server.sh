#!/bin/sh

if [ -e ./radio_common.sh ]; then
	radio_common_path='./radio_common.sh'
elif [ -e ../radio_common.sh]; then
	radio_common_path='../radio_common.sh'
elif [ -e "$HOME"/radio/radio_common.sh]; then
	radio_common_path="$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

. "$radio_common_path"

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
mkfifo clone_repo_fifo script_select_fifo \
	remote_script_fifo



#clone repo
{ cat <<'RemoteScriptEOF1'
#we need this to run remotely on the server
process_global_vars "$@" ||
show_err_and_exit "error with global variabls"

if ! git --version 2>/dev/null; then
	install_package git
fi

error_check_path "$app_root"/"$build_dir"/"$proj_name" &&
rm -rf "$app_root/$build_dir/$proj_name" &&
#since the clone will create the sub dir, we'll just start in the parent
cd "$app_root"/"$build_dir" && 
git clone "$radio_server_repo_url" "$proj_name" &&
cd "$proj_name"  &&

RemoteScriptEOF1
} > clone_repo_fifo &

#select which setup script to run
{ cat<<RemoteScriptEOF2

export diag_flag="$diag_flag" &&
export exp_name="$exp_name" &&

if [ "$setup_lvl" = 'api' ]; then
	echo "$setup_lvl"
	(exit "$unitTestSuccess") &&
	. ./radio_common.sh &&
	sync_utility_scripts &&
	startup_web_server &&
	echo "finished setup"
elif [ "$setup_lvl" = 'client' ]; then
	echo "$setup_lvl"
	. ./radio_common.sh &&
	sync_utility_scripts &&
	setup_client &&
	echo "finished setup"
elif [ "$setup_lvl" = 'radio' ]; then
	echo "$setup_lvl"
	(exit "$unitTestSuccess") &&
	. ./radio_common.sh &&
	sync_utility_scripts &&
	startup_radio &&
	echo "finished setup"
elif [ "$setup_lvl" = 'install' ]; then
	echo "$setup_lvl"
	sh ./install_setup.sh &&
	echo "finished setup"
else 
	echo "$setup_lvl"
	(exit "$unitTestSuccess") &&
	. ./radio_common.sh &&
	sync_utility_scripts &&
	setup_all &&
	echo "finished setup"
fi

RemoteScriptEOF2
} > script_select_fifo &



{
	cat<<RemoteScriptEOF3
$(cat "$radio_common_path")

radio_server_repo_url="$radio_server_repo_url"

$(cat clone_repo_fifo)

$(cat script_select_fifo)


RemoteScriptEOF3
} > remote_script_fifo &


ssh -i "$radio_key_file" "$radio_server_ssh_address" \
	'bash -s' < remote_script_fifo &&
echo "All done" || echo "Onk!"

rm -f remote_script_fifo
rm -f radio_common_fifo clone_repo_fifo script_select_fifo 






