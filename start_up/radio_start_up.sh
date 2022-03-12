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

link_to_music_files

set_pkg_mgr
set_icecast_name

if ! systemctl status "$icecast_" >/dev/null 2>&1; then
		sudo -p 'Pass required for starting icecast service: ' \
			systemctl start "$icecast_" || 
		show_err_and_exit 
fi

export config_file
. "$maintenance_dir_cl"/env/bin/activate &&
for conf in "$ices_configs_dir"/*.conf; do
	mc-ices -c "$conf"
done
