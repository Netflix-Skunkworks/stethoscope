#!/bin/bash

fwResult=`/usr/bin/defaults read /Library/Preferences/com.apple.alf globalstate`

echo "<result>$fwResult</result>"