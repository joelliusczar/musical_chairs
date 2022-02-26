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

case "$OSTYPE" in
	darwin*)
		PATH="/opt/homebrew/opt/libtool/libexec/gnubin:$PATH"
		;;
	*) ;;
esac
ices_build_dir="$build_home"/ices
old_dir=$(pwd)
name_prefix='mc-'
rm -rf "$ices_build_dir"
mkdir -pv "$ices_build_dir" 
cd "$ices_build_dir"
git clone https://github.com/joelliusczar/ices0.git
cd ices0
if [ "$test_flag" = "dbg" ]; then
	git checkout debuging
	name_prefix='dbg-'
fi
aclocal &&
autoreconf -fi &&
automake --add-missing &&
./configure --prefix="$HOME"/.local \
	--with-python=$(which mc-python) \
	--with-moddir="$pyModules_dir" \
	--program-prefix="$name_prefix" &&
make &&
make install &&
cd "$old_dir" &&
rm -rf "$ices_build_dir"