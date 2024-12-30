#!/bin/sh

caffeinate=$( pmset -g | grep caffeinate )
enabled=$(echo "This machine is being caffeinated")
disabled=$(echo "This machine is NOT being caffeinated")

if [[ -z "$caffeinate" ]]; then
    echo "<result>$disabled</result>"
    
else echo "<result>$enabled</result>"
    
fi
    
exit 0