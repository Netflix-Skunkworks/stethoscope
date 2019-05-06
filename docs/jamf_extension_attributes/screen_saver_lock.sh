#!/bin/bash

lastUser=$(/usr/bin/defaults read /Library/Preferences/com.apple.loginwindow lastUserName)
passwordStatus=$(/usr/bin/defaults read /Users/$lastUser/Library/Preferences/com.apple.screensaver askForPassword)

if [ "${passwordStatus}" == 0 ]; then
	echo "<result>Disabled</result>"
else
	echo "<result>Enabled</result>"
fi

exit 0