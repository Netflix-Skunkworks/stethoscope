#!/bin/bash

criticalUpdate=$(/usr/bin/defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist CriticalUpdateInstall)
if [[ "${criticalUpdate}" = 1 ]] || [[ "${criticalUpdate}" = *rue ]] || [[ "${criticalUpdate}" = TRUE ]]; then
    echo "<result>True</result>"
elif [[ "${criticalUpdate}" = 0 ]] || [[ "${criticalUpdate}" = *alse ]] || [[ "${criticalUpdate}" = FALSE ]]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
