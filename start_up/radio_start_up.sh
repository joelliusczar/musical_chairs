#!/bin/bash

. ../radio_common.sh

link_to_music_files

for conf in "$ices_configs_dir"/*.conf; do
	mc-ices -c "$conf"
done

# /usr/local/bin/ices -c /etc/ices/ices.vg.conf
# /usr/local/bin/ices -c /etc/ices/ices.thinking.conf