#!/bin/bash

. ./radio_common.sh
. ./icecast_check.sh

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
	sed -i -e "/Password/s/>[[:alnum:]]*/>${sourcePassword}/" "$conf"
done