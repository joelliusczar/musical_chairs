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

. "$radioCommonPath"

set -e
sh ./install_setup.sh 
set +e

# export __ICES_BRANCH__=restructure-logging
# export MC_REPO_URL='https://github.com/'
# export PB_SECRET='PB_SECRET'
# export PB_API_KEY='PB_API_KEY'
# export MC_AUTH_SECRET_KEY='MC_AUTH_SECRET_KEY'
# export __DB_SETUP_PASS__='setuppass'
# export MC_DB_PASS_API='apipass'
# export MC_DB_PASS_RADIO='radiopass'
# export MC_DB_PASS_OWNER='ownerpass'
# export MC_DATABASE_NAME='dbName'
# export MC_SERVER_KEY_FILE='ssh_file_location'
# export MC_SERVER_SSH_ADDRESS='ip_address'
# export S3_BUCKET_NAME=joelradio
# export AWS_ACCESS_KEY_ID='AWS_ACCESS_KEY_ID'
# export AWS_SECRET_ACCESS_KEY='AWS_SECRET_ACCESS_KEY'
# export MC_APP_ENV='local'