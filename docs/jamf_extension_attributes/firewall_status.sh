#!/bin/bash

fwResult=$(/usr/bin//usr/bin/defaults read /Library/Preferences/com.apple.alf globalstate)

echo "<result>$fwResult</result>"

exit 0