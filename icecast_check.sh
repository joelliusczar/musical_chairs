#!/bin/sh

if [ -e ./radio_common.sh ]; then
. ./radio_common.sh
elif [ -e ../radio_common.sh]; then
. ../radio_common.sh
elif [ -e "$HOME"/radio/radio_common.sh]; then
. "$HOME"/radio/radio_common.sh
else
	echo "radio_common.sh not found"
	exit 1
fi

set_pkg_mgr

set_icecast_name

case $(uname) in
	Linux*)
		if ! systemctl status "$icecast_" >/dev/null 2>&1; then
				echo "$icecast_ is not running at the moment"
				exit 1
		fi

		ic_conf_loc=$(systemctl status "$icecast_" | grep -A2 CGroup | \
				head -n2 | tail -n1 | awk '{ print $NF }' \
		)
		;;
	*) ;;
esac

