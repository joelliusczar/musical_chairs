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

link_to_music_files

export dbName="$app_root"/"$sqlite_file"
. "$app_root"/"$maintenance_dir_cl"/"$py_env"/bin/activate &&
# #python_env
{ python  <<EOF
from musical_chairs_libs.station_service import StationService
stationService = StationService()
stationService.end_all_stations()
print("Done")
EOF
}
deactivate