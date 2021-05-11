#!/bin/bash

db_file="$HOME"/data/radio_db
if [ ! -e "$db_file" ]; then
  sqlite3 "$db_file" ./sql_scripts/data_def_1.sql
fi