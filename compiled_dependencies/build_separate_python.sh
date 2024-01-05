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

pkgMgrChoice=$(get_pkg_mgr)

if [ "$pkgMgrChoice" = "$MC_APT_CONST" ]; then
	if ! dpkg -s build-essential >/dev/null 2>&1; then
		install_package build-essential
	fi &&
	if ! dpkg -s zlib1g-dev >/dev/null 2>&1; then
		install_package zlib1g-dev
	fi &&
	if ! dpkg -s libncurses5-dev >/dev/null 2>&1; then
		install_package libncurses5-dev
	fi &&
	if ! dpkg -s libgdbm-dev >/dev/null 2>&1; then
		install_package libgdbm-dev
	fi &&
	if ! dpkg -s libnss3-dev >/dev/null 2>&1; then
		install_package libnss3-dev
	fi &&
	if ! dpkg -s libssl-dev >/dev/null 2>&1; then
		install_package libssl-dev
	fi &&
	if ! dpkg -s libreadline-dev >/dev/null 2>&1; then
		install_package libreadline-dev
	fi &&
	if ! dpkg -s libffi-dev >/dev/null 2>&1; then
		install_package libffi-dev
	fi &&
	if ! dpkg -s libsqlite3-dev >/dev/null 2>&1; then
		install_package libsqlite3-dev
	fi &&
	if ! dpkg -s wget >/dev/null 2>&1; then
		#not sure if this is actually needed or just the guide I
		#was reading was using it to download the tar file
		install_package wget
	fi &&
	if ! dpkg -s libbz2-dev >/dev/null 2>&1; then
		install_package libbz2-dev
	fi &&
	(
		pythonBuildDir="$(__get_app_root__)"/"$MC_BUILD_DIR"/python
		empty_dir_contents "$pythonBuildDir"
		cd "$pythonBuildDir"
		verNum='3.9.1'
		curl -o Python-"$verNum".tgz \
			https://www.python.org/ftp/python/"$verNum"/Python-"$verNum".tgz
		tar -xf Python-"$verNum".tgz &&
		cd Python-"$verNum" &&
		./configure --enable-optimizations &&
		make &&
		sudo -p "install python3.9" make altinstall
	)
fi