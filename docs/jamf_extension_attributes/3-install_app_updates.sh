#!/bin/bash

autoUpdate=$(/usr/bin/defaults read /Library/Preferences/com.apple.commerce.plist AutoUpdate)
if [[ "${autoUpdate}" = 1 ]] || [[ "${autoUpdate}" = *rue ]] || [[ "${autoUpdate}" = TRUE ]]; then
    echo "<result>True</result>"
elif [[ "${autoUpdate}" = 0 ]] || [[ "${autoUpdate}" = *alse ]] || [[ "${autoUpdate}" = FALSE ]]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
