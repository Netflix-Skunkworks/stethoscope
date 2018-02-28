#!/bin/bash

autoDownload=$(/usr/bin/defaults read /Library/Preferences/com.apple.SoftwareUpdate.plist AutomaticDownload)
if [[ "${autoDownload}" = 1 ]] || [[ "${autoDownload}" = *rue ]] || [[ "${autoDownload}" = TRUE ]]; then
    echo "<result>True</result>"
elif [[ "${autoDownload}" = 0 ] || [[ "${autoDownload}" = *alse ]] || [[ "${autoDownload}" = FALSE ]]; then
    echo "<result>False</result>"
else
    echo "<result>Unknown Status</result>"
fi

exit 0
