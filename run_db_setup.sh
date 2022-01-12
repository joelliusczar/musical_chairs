#!/bin/bash

. ./radio_common.sh

db_file="$radio_home"/data/radio_db
if [ ! -e "$db_file" ]; then
  sqlite3 "$db_file" '.read ./sql_scripts/data_def_1.sql'
  sqlite3 "$db_file" '.read ./sql_scripts/insert_tags_1.sql'
fi