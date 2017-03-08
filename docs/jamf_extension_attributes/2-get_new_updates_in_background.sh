#!/bin/bash

autoDownload=`defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist AutomaticDownload`
if [ ${autoDownload} = 1 ]; then
    echo "<result>True</result>"
elif [ ${autoDownload} = 0 ]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
