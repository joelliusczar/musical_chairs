#!/bin/sh

if [ -e ./radio_common.sh ]; then
. ./radio_common.sh
elif [ -e ../radio_common.sh]; then
. ../radio_common.sh
elif [ -e "$HOME"/radio/radio_common.sh]; then
. "$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

if [ -e ./icecast_check.sh ]; then
. ./icecast_check.sh
elif [ -e ../icecast_check.sh]; then
. ../icecast_check.sh
elif [ -e "$HOME"/radio/icecast_check.sh]; then
. "$HOME"/radio/icecast_check.sh
else
  echo "icecast_check.sh not found"
  exit 1
fi


echo 'Enter radio station public name or description:'
read public_name

echo 'Enter radio station internal name:'
read internal_name

echo "public: $public_name"
echo "internal: $internal_name"

sourcePassword=$(sudo grep '<source-password>' "$ic_conf_loc" | perl -ne 'print "$1\n" if />(\w+)/')

added_config_name="$ices_configs_dir"/ices."$internal_name".conf
cp "$templates_dir_cl"/configs/ices.conf "$added_config_name" &&
sed -i -e "/<Password>/s/>[[:alnum:]]*/>${sourcePassword}/" \
  -e "/<Module>/s/internal_station_name/${internal_name}/" \
  -e "/<Name>/s/public_station_name/${public_name}/" \
  -e "/<Mountpoint>/s/internal_station_name/${internal_name}/" \
  "$added_config_name" ||
{
  exit 1
}

added_module_name="$pyModules_dir"/"$internal_name".py &&
cp "$templates_dir_cl"/template.py "$added_module_name" &&
sed -i -e "s/<internal_station_name>/${internal_name}/" "$added_module_name" ||
{
  exit 1
}

export config_file

env_path="$maintenance_dir_cl"


. "$env_path"/env/bin/activate &&
{ mc-python  <<EOF
from musical_chairs_libs.station_service import add_station
add_station('${internal_name}','${public_name}')
print('${internal_name} added')
EOF
} && {
while true; do
echo -n 'Enter a tag to assign to station: '
read tagname
[ -z "$tagname" ] && break
{ mc-python <<EOF
from musical_chairs_libs.station_service import assign_tag_to_station
assign_tag_to_station('${internal_name}','${tagname}')
print('tag ${tagname} assigned to ${internal_name}')
EOF
}
done
} ||
{
  echo 'no 1'
  echo 'no 2'
}
deactivate
