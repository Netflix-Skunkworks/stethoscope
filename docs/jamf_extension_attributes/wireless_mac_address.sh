#!/bin/bash

wifiPort=$(/usr/sbin/networksetup -listallhardwareports | awk '/Hardware Port: Wi-Fi/,/Ethernet/' | awk 'NR==2' | cut -d " " -f 2)
macAddy=$(/usr/sbin/networksetup -getmacaddress "$wifiPort" | awk {'print $3'})

echo "<result>$macAddy</result>"

exit 0