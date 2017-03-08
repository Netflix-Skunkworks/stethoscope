#!/bin/bash

autoCheck=`defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist AutomaticCheckEnabled`
if [ ${autoCheck} = 1 ]; then
    echo "<result>True</result>"
elif [ ${autoCheck} = 0 ]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
