#!/bin/bash

. ../radio_common.sh

link_to_music_files

/usr/local/bin/ices -c /etc/ices/ices.vg.conf
/usr/local/bin/ices -c /etc/ices/ices.thinking.conf