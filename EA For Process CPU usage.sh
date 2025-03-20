#!/bin/zsh --no-rcs

#replace 'protect' with whatever string will find the desired process. In this case Jamf Protect 
percent=$(ps -A -o %cpu,comm | grep protect | awk '{print $1}')

echo "<result>$percent</result>"