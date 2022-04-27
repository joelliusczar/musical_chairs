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
	perl -pi -e "s/>\w*/>${sourcePassword}/ if /source-password/" \
	"$ic_conf_loc" &&
sudo -p 'Pass required for modifying icecast config: ' \
	perl -pi -e "s/>\w*/>${relayPassword}/ if /relay-password/" \
	"$ic_conf_loc" &&
sudo -p 'Pass required for modifying icecast config: ' \
	perl -pi -e "s/>\w*/>${adminPassword}/ if /admin-password/" \
	"$ic_conf_loc" || 
show_err_and_exit 


for conf in "$app_root"/"$ices_configs_dir"/*.conf; do
	[ ! -e "$conf" ] && continue
	perl -pi -e "s/>\w*/>${sourcePassword}/ if /Password/" "$conf"
done