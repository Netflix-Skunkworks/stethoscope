#!/bin/bash

autoUpdate=`defaults read /Library/Preferences/com.apple.commerce.plist AutoUpdate`
if [ ${autoUpdate} = 1 ]; then
    echo "<result>True</result>"
elif [ ${autoUpdate} = 0 ]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
