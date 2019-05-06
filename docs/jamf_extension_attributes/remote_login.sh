#!/bin/bash

remoteLogin=$(/usr/sbin/systemsetup -getremotelogin | awk '{print $3}')

echo "<result>$remoteLogin</result>"

exit 0