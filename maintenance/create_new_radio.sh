#!/bin/sh

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

if [ -e ./icecast_check.sh ]; then
. ./icecast_check.sh
elif [ -e ../icecast_check.sh ]; then
. ../icecast_check.sh
elif [ -e "$HOME"/radio/icecast_check.sh ]; then
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

sourcePassword=$(sudo -p 'Pass required to read icecast config: ' \
  grep '<source-password>' "$ic_conf_loc" \
  | perl -ne 'print "$1\n" if />(\w+)/') || 
show_err_and_exit 

station_conf="$app_root"/"$ices_configs_dir"/ices."$internal_name".conf
cp "$app_root"/"$templates_dir_cl"/ices.conf "$station_conf" &&
perl -pi -e "s/icecast_password/$sourcePassword/ if /<Password>/" \
  "$station_conf" &&
perl -pi -e "s/internal_station_name/$internal_name/ if /<Module>/" \
  "$station_conf" &&
perl -pi -e "s/public_station_name/$public_name/ if /<Name>/" \
  "$station_conf" &&
perl -pi -e "s/internal_station_name/$internal_name/ if /<Mountpoint>/" \
  "$station_conf" ||
show_err_and_exit

station_module="$app_root"/"$pyModules_dir"/"$internal_name".py &&
cp "$app_root"/"$templates_dir_cl"/template.py "$station_module" &&
perl -pi -e "s/<internal_station_name>/$internal_name/" "$station_module" ||
show_err_and_exit

export dbName="$app_root"/"$sqlite_file"


. "$app_root"/"$maintenance_dir_cl"/"$py_env"/bin/activate &&
# #python_env
{ python  <<EOF
from musical_chairs_libs.station_service import StationService
stationService = StationService()
stationService.add_station('${internal_name}','${public_name}')
print('${internal_name} added')
EOF
} && {
while true; do
echo -n 'Enter a tag to assign to station: '
read tagname
[ -z "$tagname" ] && break
# #python_env
{ python <<EOF
from musical_chairs_libs.station_service import StationService
stationService = StationService()
stationService.assign_tag_to_station('${internal_name}','${tagname}')
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
