#!/bin/bash

configData=`defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist ConfigDataInstall`
if [ ${configData} = 1 ]; then
    echo "<result>True</result>"
elif [ ${configData} = 0 ]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
