#!/bin/sh

run_api_setup() {
  local setup_script="$1"
  if [ -e ./"$setup_script" ]; then
    sh ./"$setup_script"
  elif [ ./api_setup/"$setup_script" ]; then
    sh ./api_setup/"$setup_script"
  fi
}

run_api_setup 'setup_backend.sh'
run_api_setup 'setup_client.sh'

