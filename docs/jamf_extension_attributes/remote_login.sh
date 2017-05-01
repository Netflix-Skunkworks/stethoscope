#!/bin/sh
echo "<result>`/usr/sbin/systemsetup -getremotelogin | awk '{print $3}'`</result>"