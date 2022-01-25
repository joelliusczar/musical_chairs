#!/bin/sh

. ./radio_common.sh

set_pkg_mgr

case "$pkgMgrChoice" in
    "$PACMAN_CONST") icecast_='icecast';;
    "$APT_CONST") icecast_='icecast2';;
    *) icecast_='icecast2';;
esac

if ! systemctl status "$icecast_" &>/dev/null; then
    echo "$icecast_ is not running at the moment"
    exit 1
fi

ic_conf_loc=$(systemctl status "$icecast_" | grep -A2 CGroup | \
    head -n2 | tail -n1 | awk '{ print $NF }' \
)