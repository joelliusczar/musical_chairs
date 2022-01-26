#!/bin/sh

base_path="$(dirname "$0")/"
current_path=$(pwd)
cd "$base_path"

. ../radio_common.sh

set_pkg_mgr

set_icecast_version

if ! systemctl status "$icecast_" >/dev/null 2>&1; then
    echo "$icecast_ is not running at the moment"
    exit 1
fi

ic_conf_loc=$(systemctl status "$icecast_" | grep -A2 CGroup | \
    head -n2 | tail -n1 | awk '{ print $NF }' \
)

