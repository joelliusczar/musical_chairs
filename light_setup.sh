#!/bin/sh


. ./radio_common.sh


empty_dir_contents "$start_up_dir_cl"

sudo cp -v ./start_up/* "$start_up_dir_cl"
sudo chown -R "$current_user": "$start_up_dir_cl"
