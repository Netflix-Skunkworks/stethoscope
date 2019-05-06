#!/bin/bash

configData=$(/usr/bin/defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist ConfigDataInstall)
if [ "${configData}" = 1 ]] || [[ "${configData}" = *rue ]] || [[ "${configData}" = TRUE ]]; then
    echo "<result>True</result>"
elif [[ "${configData}" = 0 ]] || [[ "${configData}" = *alse ]] || [[ "${configData}" = FALSE ]]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
