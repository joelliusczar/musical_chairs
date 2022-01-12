#!/bin/bash

. ./radio_common.sh

genPass() {
    LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 16 
}

sourcePassword=$(genPass)
relayPassword=$(genPass)
adminPassword=$(genPass)

sudo sed -i -e "/source-password/s/hackmeSource/${sourcePassword}/" \
    -e "/relay-password/s/hackmeRelay/${relayPassword}/" \
    -e "/admin-password/s/hackmeAdmin/${adminPassword}/ \
    /etc/icecast.xml