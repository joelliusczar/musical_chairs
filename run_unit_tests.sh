#!/bin/sh

if [ -e ./radio_common.sh ]; then
. ./radio_common.sh test
elif [ -e ../radio_common.sh ]; then
. ../radio_common.sh test
elif [ -e "$HOME"/radio/radio_common.sh ]; then
. "$HOME"/radio/radio_common.sh test
else
	echo "radio_common.sh not found"
	exit 1
fi


if [ -n "$(find ./src/"$lib_name" -newer "$utest_env_dir"/"$py_env")" ]; then
	echo "changes?"
	setup_py3_env "$utest_env_dir" || 
	show_err_and_exit 
fi

test_src="$src_path"/tests

export PYTHONPATH="$src_path"
export dbName="$app_root"/"$sqlite_file"
export searchBase="$app_root"/"$content_home"

. "$utest_env_dir"/"$py_env"/bin/activate &&
pytest -s "$test_src"