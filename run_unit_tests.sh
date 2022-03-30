#!/bin/sh

called_from=$(dirname $0)

if [ -e "$called_from/test_trash" ]; then
	test_root="$called_from/test_trash"
else
	echo "test_trash not found"
	exit 1
fi


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

utest_env_dir="$test_root"/utest

setup_py3_env "$utest_env_dir" || 
show_err_and_exit 

if [ -n "$test_flag" ]; then
	cp -v "$called_from/reference/songs_db" "$sqlite_file" || 
	show_err_and_exit 
fi

setup_config_file


test_src="$called_from/src/tests"

export config_file
. "$utest_env_dir"/"$py_env"/bin/activate &&
pytest "$test_src"