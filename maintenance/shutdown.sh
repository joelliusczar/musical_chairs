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

link_to_music_files

if [ "$test_flag" = "test" ]; then 
  env_path='./src/maintenance' 
else 
  env_path="$maintenance_dir_cl"
fi

export config_file
. "$env_path"/env/bin/activate &&
{ mc-python  <<EOF
from musical_chairs_libs.station_service import end_all_stations
end_all_stations()
print("Done")
EOF
}
deactivate