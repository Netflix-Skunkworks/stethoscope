#!/bin/sh

wifiPort=`networksetup -listallhardwareports | awk '/Hardware Port: Wi-Fi/,/Ethernet/' | awk 'NR==2' | cut -d " " -f 2`
macAddy=`networksetup -getmacaddress $wifiPort | awk {'print $3'}`

echo "<result>$macAddy</result>"