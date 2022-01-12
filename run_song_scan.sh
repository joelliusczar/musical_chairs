#!/bin/bash

. ./radio_common.sh

if [ ! -e "$radio_home"/music/radio/Soundtrack ]; then 
  if [ -n "$IS_RADIO_LOCAL_DEV" ]; then
    s3fs joelradio "$radio_home"/music/radio/
  else
    s3fs joelradio "$radio_home"/music/radio/ -o iam_role="music_reader"
  fi
fi

pyMaintenancePath="$radio_home"/process/maintenance
"$pyMaintenancePath"/env/bin/python3 "$pyMaintenancePath"/scan_new_songs.py
