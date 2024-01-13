#!/bin/sh

if [ -e ./radio_common.sh ]; then
	radioCommonPath='./radio_common.sh'
elif [ -e ../radio_common.sh ]; then
	radioCommonPath='../radio_common.sh'
elif [ -e "$HOME"/radio/radio_common.sh ]; then
	radioCommonPath="$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

#this is included locally. Any changes here are not going to be on the server
#unless they've been pushed to the repo
. "$radioCommonPath"

### replace below with function to be tested ###
process_global_vars "$@" &&

publicKeyName=$(__get_debug_cert_name__).public.key.crt 
cat '/usr/share/firefox-esr/distribution/policies.json' | get_trusted_by_firefox_json_with_added_cert "$publicKeyName"
