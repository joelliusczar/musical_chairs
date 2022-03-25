#!/bin/sh

called_from='.'

if [ -e "$called_from/test_trash" ]; then
	test_root="$called_from/test_trash"
else
	echo "test_trash not found"
	exit 1
fi



if [ -e ./radio_common.sh ]; then
. ./radio_common.sh radio_home="$test_root"
elif [ -e ../radio_common.sh ]; then
. ../radio_common.sh radio_home="$test_root"
elif [ -e "$HOME"/radio/radio_common.sh ]; then
. "$HOME"/radio/radio_common.sh radio_home="$test_root"
else
	echo "radio_common.sh not found"
	exit 1
fi

utest_env_dir="$test_root"/utest

setup_config_file


test_dir="$called_from/src/tests"

export config_file
. "$maintenance_dir_cl"/env/bin/activate &&
pytest "$test_dir"