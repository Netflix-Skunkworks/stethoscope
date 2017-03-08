#!/bin/sh
lastUser=`defaults read /Library/Preferences/com.apple.loginwindow lastUserName`
passwordStatus=`defaults read /Users/$lastUser/Library/Preferences/com.apple.screensaver askForPassword`

if [ "$passwordStatus" == "0" ]; then
	echo "<result>Disabled</result>"
else
	echo "<result>Enabled</result>"
fi