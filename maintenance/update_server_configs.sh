#!/bin/sh

test_flag="$1"
[ "$test_flag" = "test" ] && defs_home='.' || defs_home="$HOME"/radio

. "$defs_home"/radio_common.sh
. "$defs_home"/icecast_check.sh

genPass() {
	LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 16 
}

sourcePassword=$(genPass)
relayPassword=$(genPass)
adminPassword=$(genPass)


sudo sed -i -e "/source-password/s/>[[:alnum:]]*/>${sourcePassword}/" \
	-e "/relay-password/s/>[[:alnum:]]*/>${relayPassword}/" \
	-e "/admin-password/s/>[[:alnum:]]*/>${adminPassword}/" \
	"$ic_conf_loc"

for conf in "$ices_configs_dir"/*.conf; do
	[ ! -e "$conf" ] && continue
	sed -i -e "/Password/s/>[[:alnum:]]*/>${sourcePassword}/" "$conf"
done