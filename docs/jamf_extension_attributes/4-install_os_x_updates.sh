#!/bin/bash

updateRestart=`defaults read /Library/Preferences/com.apple.commerce.plist AutoUpdateRestartRequired`
if [ ${updateRestart} = 1 ]; then
    echo "<result>True</result>"
elif [ ${updateRestart} = 0 ]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
