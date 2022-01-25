#!/bin/sh

. ./radio_common.sh

set_pkg_mgr

if [ -z "$pkgMgr" ]; then
	echo "No package manager set"
	exit 1
fi

if ! perl -v 2>/dev/null; then
	eval "$pkgMrg" perl
fi

[ ! -e "$HOME/.local/bin" ] && mkdir -pv "$HOME/.local/bin"


if ! python3 -V 2>/dev/null; then
	eval "$pkgMgr" python3
fi

if [ "$pyMinor" -le 10 ] && [ "$pkgMgrChoice" = "$APT_CONST" ]; then
	eval "$pkgMgr" python3-distutils
fi

if ! python3 -m pip -V 2>/dev/null; then
	curl https://bootstrap.pypa.io/pip/get-pip.py | python3 /dev/stdin
fi


if ! python3 -m  virtualenv --version 2>/dev/null; then
	python3 -m pip install --user virtualenv
fi

if ! npm version 2>/dev/null; then
	eval "$pkgMgr" npm
fi

if ! s3fs --version 2>/dev/null; then
	eval "$pkgMgr" s3fs
fi

if ! sqlite3 -version 2>/dev/null; then
	eval "$pkgMgr" sqlite3
fi

if ! git --version 2>/dev/null; then
	eval "$pkgMgr" git
fi

if ! aclocal --version 2>/dev/null; then
	eval "$pkgMgr" automake
fi

if ! libtool --version 2>/dev/null && [ "$pkgMgrChoice" = "$APT_CONST" ]; then
	eval "$pkgMgr" libtool-bin
fi

if [ "$pkgMgrChoice" = "$APT_CONST" ]; then
	if [  -z "$(apt version libxml2-dev)" ]; then
		eval "$pkgMgr" libxml2-dev
	fi
	if [  -z "$(apt version libogg-dev)" ]; then
		eval "$pkgMgr" libogg-dev
	fi
	if [  -z "$(apt version libvorbis-dev)" ]; then
		eval "$pkgMgr" libvorbis-dev
	fi
	if [  -z "$(apt version libshout3-dev)" ]; then
		eval "$pkgMgr" libshout3-dev
	fi
	if [  -z "$(apt version libmp3lame-dev)" ]; then
		eval "$pkgMgr" libmp3lame-dev
	fi
	if [  -z "$(apt version libflac-dev)" ]; then
		eval "$pkgMgr" libflac-dev
	fi
	if [  -z "$(apt version libfaad-dev)" ]; then
		eval "$pkgMgr" libfaad-dev
	fi
	if [ -z "$(apt version python"$pyMajor"."$pyMinor"-dev)" ]; then
		eval "$pkgMgr" python"$pyMajor"."$pyMinor"-dev
	fi
	if [  -z "$(apt version libperl-dev)" ]; then
		eval "$pkgMgr" libperl-dev
	fi

fi

if ! [ -e "$build_home" ]; then
	mkdir -pv "$build_home"
fi

if ! [ -e "$radio_home" ]; then
	mkdir -pv "$radio_home"
fi

if [ "$pkgMgrChoice" = "$PACMAN_CONST" ]; then
	if ! icecast -v 2>/dev/null; then
		eval "$pkgMgr" icecast
	fi
elif [ "$pkgMgrChoice" = "$APT_CONST" ]; then
	if ! icecast2 -v 2>/dev/null; then
		eval "$pkgMgr" icecast2
	fi
fi

if perl -e "exit 1 if index('$PATH','$HOME/.local/bin') != -1"; then
	echo 'Please add "$HOME/.local/bin" to path'
	export PATH="$PATH":"$HOME"/.local/bin
fi

if ! mc-ices -V 2>/dev/null; then
	ices_build_dir="$build_home"/ices
	rm -rf "$ices_build_dir"
	mkdir -pv "$ices_build_dir" 
	cd "$ices_build_dir"
	git clone https://github.com/joelliusczar/ices0.git
	cd ices0
	aclocal &&
	autoreconf -fi &&
	automake --add-missing &&
	./configure --prefix="$HOME"/.local \
		--with-python=/usr/bin/python3 \
		--with-moddir="$pyModules_dir" \
		--program-prefix='mc-' &&
	make &&
	make install &&
	cd - &&
	rm -rf "$ices_build_dir"
fi

create_db() {
	echo "creating $sqlite_file"
	sqlite3 "$sqlite_file" ".read ./sql_scripts/data_def_1.sql" &&
	sqlite3 "$sqlite_file" ".read ./sql_scripts/insert_tags_1.sql" &&
	sqlite3 "$sqlite_file" ".read ./sql_scripts/security_def_1.sql"
}

if [ -e "$sqlite_file" ]; then
	echo 'The database already exits. Do you want to start from scratch? Y to confirm'
	read db_choice
	if [ "$db_choice" = 'Y' ]; then
		rm -f "$sqlite_file"
		create_db
		db_res="$?"
	else
		echo 'Using existing db'
		db_res=1
	fi
else 
	create_db
	db_res="$?"
fi



link_to_music_files

$(exit "$db_res") && sh ./commit_setup.sh 
#sh ./run_song_scan.sh