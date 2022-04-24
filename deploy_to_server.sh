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

#Would have prefered to just use a variable
#but it seems to choke on certain characters like ')' for some reason
#when I do it like 
#myVar=$(cat<<EOF
#...
#)
mkfifo radio_common_fifo clone_repo_fifo script_select_fifo 
mkfifo remote_script_fifo


cat "$radio_common_path" > radio_common_fifo &


#clone repo
{ cat <<'RemoteScriptEOF1'


if ! git --version 2>/dev/null; then
	install_package git
fi

empty_dir_contents "$build_home"/"$proj_name" &&
cd "$build_home"/"$proj_name" &&
git clone "$radio_server_repo_url" "$proj_name" &&
cd "$proj_name" &&
if [ -n "$diag_flag" ]; then
	git checkout -t diagnosis
fi


RemoteScriptEOF1
} > clone_repo_fifo &

#select which setup script to run
{ cat<<RemoteScriptEOF2


if [ "$setup_lvl" = 'api' ]; then
	echo "$setup_lvl"
	sh ./setup_backend.sh
elif [ "$setup_lvl" = 'client' ]; then
	echo "$setup_lvl"
	sh ./setup_client.sh
elif [ "$setup_lvl" = 'radio' ]; then
	echo "$setup_lvl"
	sh ./radio_dir_setup.sh
elif [ "$setup_lvl" = 'install' ]; then
	echo "$setup_lvl"
	sh ./install_setup.sh
else 
	echo "$setup_lvl"
	sh ./radio_dir_setup.sh &&
	sh ./setup_backend.sh &&
	sh ./setup_client.sh 
fi

RemoteScriptEOF2
} > script_select_fifo &



{
	cat<<RemoteScriptEOF3
$(cat radio_common_fifo)

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






