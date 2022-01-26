#!/bin/sh

. ./radio_common.sh

ices_build_dir="$build_home"/ices
old_dir=$(pwd)
rm -rf "$ices_build_dir"
mkdir -pv "$ices_build_dir" 
cd "$ices_build_dir"
git clone https://github.com/joelliusczar/ices0.git
cd ices0
aclocal &&
autoreconf -fi &&
automake --add-missing &&
./configure --prefix="$HOME"/.local \
	--with-python=$(which python3) \
	--with-moddir="$pyModules_dir" \
	--program-prefix='mc-' &&
make &&
make install &&
cd "$old_dir" &&
rm -rf "$ices_build_dir"