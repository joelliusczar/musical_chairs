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

#we have this as a seperate script so I can easily run it without being tangled
#with the rest

case $(uname) in
	Darwin*)
		PATH="/opt/homebrew/opt/libtool/libexec/gnubin:$PATH"
		;;
	*) ;;
esac
ices_build_dir="$build_home"/ices
(
	name_prefix='mc-'
	empty_dir_contents "$ices_build_dir"
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
	rm -rf "$ices_build_dir"
)