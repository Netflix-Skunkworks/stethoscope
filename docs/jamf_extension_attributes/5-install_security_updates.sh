#!/bin/bash

criticalUpdate=`defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist CriticalUpdateInstall`
if [ ${criticalUpdate} = 1 ]; then
    echo "<result>True</result>"
elif [ ${criticalUpdate} = 0 ]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
