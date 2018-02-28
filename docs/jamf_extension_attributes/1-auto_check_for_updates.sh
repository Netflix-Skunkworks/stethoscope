#!/bin/bash

autoCheck=$(/usr/bin/defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist AutomaticCheckEnabled)
if [[ "${autoCheck}" = 1 ]] || [[ "${autoCheck}" = *rue ]] || [[ "${autoCheck}" = TRUE ]]; then
    echo "<result>True</result>"
elif [[ "${autoCheck}" = 0 ]] || [[ "${autoCheck}" = *alse ]] ||  [[ "${autoCheck}" = FALSE ]]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
