#!/bin/sh

. ./radio_common.sh
. ./icecast_check.sh

echo 'Enter radio station public name or description:'
read public_name

echo 'Enter radio station internal name:'
read internal_name

echo "public: $public_name"
echo "internal: $internal_name"

sourcePassword=$(sudo grep '<source-password>' "$ic_conf_loc" | perl -e 'print "$1" if />(\w+)/')

added_config_name="$ices_configs_dir"/ices."$internal_name".conf
cp ./templates/configs/ices.conf "$added_config_name"
sed -i -e "/<Password>/s/>[[:alnum:]]*/>${sourcePassword}/" \
  -e "/<Module>/s/internal_station_name/${internal_name}/" \
  -e "/<Name>/s/public_station_name/${public_name}/" \
  "$added_config_name"

added_module_name="$pyModules_dir"/"$internal_name".py
cp ./templates/template.py "$added_module_name"
sed -i -e "s/<internal_station_name>/${internal_name}/" "$added_module_name" 

export config_file

if [ "$test_flag" = "test" ]; then 
  env_path='./src/maintenance' 
else 
  env_path="$maintenance_dir_cl"
fi

. "$env_path"/env/bin/activate &&
{ python3  <<EOF
from musical_chairs_libs.station_manager import add_station
add_station('${internal_name}','${public_name}')
EOF
} && {
while read tagname; do
{ 
python3 <<EOF
from musical_chairs_libs.station_manager import assign_tag_to_station

EOF
    }
  done
} ||
{
  echo 'no 1'
  echo 'no 2'
}
deactivate
