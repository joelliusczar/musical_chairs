#!/bin/sh

if [ -e ./radio_common.sh ]; then
	radio_common_path='./radio_common.sh'
elif [ -e ../radio_common.sh]; then
	radio_common_path='../radio_common.sh'
elif [ -e "$HOME"/radio/radio_common.sh]; then
	radio_common_path="$HOME"/radio/radio_common.sh
else
  echo "radio_common.sh not found"
  exit 1
fi

. "$radio_common_path"

clone_script=$(cat <<'EOF'
if [ -z "$pkgMgr" ]; then
	echo "No package manager set"
	exit 1
fi

if ! git --version 2>/dev/null; then
	eval "$pkgMgr" git
fi

empty_dir_contents "$build_home"/"$proj_name" &&
cd "$build_home"/"$proj_name" &&
git clone "$radio_server_repo_url" "$proj_name" &&
cd "$proj_name" 

EOF
)

setup_script=$(cat<<EOF
if [ "$setup_lvl" = 'api' ]; then
	sh ./setup_backend.sh
elif [ "$setup_lvl" = 'client' ]; then
	sh ./setup_client.sh
elif [ "$setup_lvl" = 'radio' ]; then
	sh ./radio_dir_setup.sh
elif [ "$setup_lvl" = 'install' ]; then
	sh ./install_setup.sh
else 
	sh ./radio_dir_setup.sh &&
	sh ./setup_backend.sh &&
	sh ./setup_client.sh &&
fi
EOF
)

remote_script=$(cat<<EOF
$(cat "$radio_common_path")

set_pkg_mgr

$(echo "$clone_script")

$(echo "$setup_script")

EOF
)

echo "$remote_script"






