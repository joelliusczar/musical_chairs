#!/bin/sh

if [ -e ./radio_common.sh ]; then
. ./radio_common.sh
elif [ -e ../radio_common.sh ]; then
. ../radio_common.sh
elif [ -e "$HOME"/radio/radio_common.sh ]; then
. "$HOME"/radio/radio_common.sh
else
	echo "radio_common.sh not found"
	exit 1
fi

pkgMgrChoice=$(get_pkg_mgr)

icecast_name=$(get_icecast_name "$pkgMgrChoice")

case $(uname) in
	Linux*)
		if ! systemctl status "$icecast_name" >/dev/null 2>&1; then
				echo "$icecast_name is not running at the moment"
				exit 1
		fi

		ic_conf_loc=$(systemctl status "$icecast_name" | grep -A2 CGroup | \
				head -n2 | tail -n1 | awk '{ print $NF }' \
		)
		;;
	*) ;;
esac

