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

pkgMgrChoice=$(get_pkg_mgr)
icecast_name=$(get_icecast_name "$pkgMgrChoice")

if ! systemctl status "$icecast_name" >/dev/null 2>&1; then
		sudo -p 'Pass required for starting icecast service: ' \
			systemctl start "$icecast_name" || 
		show_err_and_exit 
fi

export searchBase="$music_home"
export dbName="$sqlite_file"
. "$maintenance_dir_cl"/"$py_env"/bin/activate &&
for conf in "$ices_configs_dir"/*.conf; do
	mc-ices -c "$conf"
done
