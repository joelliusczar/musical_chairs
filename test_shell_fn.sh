#!/bin/sh

if [ -e ./mc_dev_ops.sh ]; then
	radioCommonPath='./mc_dev_ops.sh'
elif [ -e ../mc_dev_ops.sh ]; then
	radioCommonPath='../mc_dev_ops.sh'
elif [ -e "$HOME"/radio/mc_dev_ops.sh ]; then
	radioCommonPath="$HOME"/radio/mc_dev_ops.sh
else
  echo "mc_dev_ops.sh not found"
  exit 1
fi

#this is included locally. Any changes here are not going to be on the server
#unless they've been pushed to the repo
. "$radioCommonPath"

### replace below with function to be tested ###
process_global_vars "$@" &&

echo "$(__get_app_root__)"/keys/"$MC_PROJ_NAME"

echo $(__get_s3_region_name__)