#!/bin/sh


. ./radio_common.sh


empty_dir_contents "$start_up_dir_cl"

cp -v ./start_up/* "$start_up_dir_cl"
