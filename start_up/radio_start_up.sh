#!/bin/sh

test_flag="$1"
[ "$test_flag" = "test" ] && defs_home='../' || defs_home="$HOME"/radio

. "$defs_home"/radio_common.sh

link_to_music_files

set_pkg_mgr
set_icecast_version

if ! systemctl status "$icecast_" >/dev/null 2>&1; then
    sudo systemctl start "$icecast_"
fi

export config_file
. "$maintenance_dir_cl"/env/bin/activate &&
for conf in "$ices_configs_dir"/*.conf; do
	mc-ices -c "$conf"
done
