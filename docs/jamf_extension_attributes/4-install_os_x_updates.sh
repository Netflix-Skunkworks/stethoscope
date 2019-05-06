#!/bin/bash

updateRestart=$(/usr/bin/defaults read /Library/Preferences/com.apple.commerce.plist AutoUpdateRestartRequired)
if [ "${updateRestart}" = 1 ]] || [[ "${updateRestart}" = *rue ]] || [[ "${updateRestart}" = TRUE ]]; then
    echo "<result>True</result>"
elif [[ "${updateRestart}" = 0 ]] || [[ "${updateRestart}" = *alse ]] || [[ "${updateRestart}" = FALSE ]]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
