#!/bin/bash

if [ ! -e "$HOME"/music/radio/Soundtrack ]; then 
  s3fs joelradio "$HOME"/music/radio/ -o iam_role="music_reader"
fi

"$HOME"/process/maintenance/env/bin/python3 "$HOME"/process/maintenance/scan_new_songs.py
