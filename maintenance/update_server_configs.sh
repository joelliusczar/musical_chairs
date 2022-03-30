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


sourcePassword=$(gen_pass)
relayPassword=$(gen_pass)
adminPassword=$(gen_pass)


sudo -p 'Pass required for modifying icecast config: ' \
	sed -i -e "/source-password/s/>[[:alnum:]]*/>${sourcePassword}/" \
	"$ic_conf_loc" &&
sudo -p 'Pass required for modifying icecast config: ' \
	sed -i -e "/relay-password/s/>[[:alnum:]]*/>${relayPassword}/" \
	"$ic_conf_loc" &&
sudo -p 'Pass required for modifying icecast config: ' \
	sed -i -e "/admin-password/s/>[[:alnum:]]*/>${adminPassword}/" \
	"$ic_conf_loc" || 
show_err_and_exit 


for conf in "$ices_configs_dir"/*.conf; do
	[ ! -e "$conf" ] && continue
	sed -i -e "/Password/s/>[[:alnum:]]*/>${sourcePassword}/" "$conf"
done