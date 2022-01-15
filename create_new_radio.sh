#!/bin/sh

. ./radio_common.sh
. ./icecast_check.sh

echo 'Enter radio station public name:'
read public_name

echo 'Enter radio station internal name:'
read internal_name

echo "public: $public_name"
echo "internal: $internal_name"



cp ./templates/configs/ices.conf "$ices_configs_dir"/ices."$internal_name".conf