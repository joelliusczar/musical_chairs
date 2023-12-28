#!/bin/sh

echo '##### vimrc #####'
if [ ! -e "$HOME"/.vimrc ]; then
	touch "$HOME"/.vimrc
fi
perl -pi -e "s/set nonumber/set number/" "$HOME"/.vimrc
perl -pi -e "s/set expandtab/set noexpandtab/" "$HOME"/.vimrc
perl -pi -e "s/set tabstop=\d+/set tabstop=2/" "$HOME"/.vimrc
lineNum=$(perl -ne 'print "true" if /set number/' "$HOME"/.vimrc)
noexpandtabs=$(perl -ne 'print "true" if /set noexpandtab/' "$HOME"/.vimrc)
tabstop=$(perl -ne 'print "true" if /set tabstop=2/' "$HOME"/.vimrc)

if [ "$lineNum" != 'true' ]; then
	echo 'set number' >> "$HOME"/.vimrc
fi
if [ "$noexpandtabs" != 'true' ]; then
	echo 'set noexpandtab' >> "$HOME"/.vimrc
fi
if [ "$tabstop" != 'true' ]; then
	echo 'set tabstop=2' >> "$HOME"/.vimrc
fi