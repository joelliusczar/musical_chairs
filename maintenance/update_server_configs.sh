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

if [ -e ./icecast_check.sh ]; then
. ./icecast_check.sh
elif [ -e ../icecast_check.sh]; then
. ../icecast_check.sh
elif [ -e "$HOME"/radio/icecast_check.sh]; then
. "$HOME"/radio/icecast_check.sh
else
  echo "icecast_check.sh not found"
  exit 1
fi

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