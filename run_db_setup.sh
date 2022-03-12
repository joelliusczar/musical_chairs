#!/bin/bash

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

db_file="$radio_home"/data/radio_db
if [ ! -e "$db_file" ]; then
  sqlite3 "$db_file" '.read ./sql_scripts/data_def_1.sql'
  sqlite3 "$db_file" '.read ./sql_scripts/insert_tags_1.sql'
fi