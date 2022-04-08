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

test_src="$abs_src_path/src/tests"


. "$utest_env_dir"/"$py_env"/bin/activate &&
pytest -s "$test_src"