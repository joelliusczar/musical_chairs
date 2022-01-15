#!/bin/sh

. ./radio_common.sh

case "$pkgMgrChoice" in
    "$PACMAN_CONST") icecast_='icecast';;
    *) icecast_='icecast2';;
esac

ic_conf_loc=$(systemctl status "$icecast_" | grep -A2 CGroup | \
    head -n2 | tail -n1 | awk '{ print $NF }' \
)