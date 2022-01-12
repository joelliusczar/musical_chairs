#!/bin/bash

. ./radio_common.sh

if [ ! -e "$music_home"/radio/Soundtrack ]; then 
  if [ -n "$IS_RADIO_LOCAL_DEV" ]; then
    s3fs joelradio "$music_home"/radio/
  else
    s3fs joelradio "$music_home"/radio/ -o iam_role="music_reader"
  fi
fi

/usr/local/bin/ices -c /etc/ices/ices.vg.conf
/usr/local/bin/ices -c /etc/ices/ices.thinking.conf