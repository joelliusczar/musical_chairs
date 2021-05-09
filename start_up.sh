#!/bin/bash

s3fs joelradio ~/music/radio/ -o iam_role="music_reader"

/usr/local/bin/ices -c /etc/ices/ices.vg.conf
/usr/local/bin/ices -c /etc/ices/ices.thinking.conf