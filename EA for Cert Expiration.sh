#!/bin/zsh --no-rcs

#echo commands on lines 11, 15, and 19 can be removed after testing

#replace the example certificate with any that need reporting on.
#In this case I'm looking for a certificate that has "managementAttestation in the CN field as is done with Okta SCEP
certExp=$(security find-certificate -c "managementAttestation" -p | openssl x509 -text | grep "Not After" | awk '{print $5 "-" $4 "-" $7}')
echo "cert expiration: $certExp"

time=$(security find-certificate -c "managementAttestation" -p | openssl x509 -text | grep "Not After" | awk '{print $6}')
echo "time expiration: $time"

#format the date gathered in line 7
formattedDate=$(date -j -f "%d-%b-%Y" "$certExp" "+%d-%m-%Y")
echo "formatted date: $formattedDate"

#combine the date and the time(gathered in line 10)
formattedDateWTime=$(echo $formattedDate $time)
echo $formattedDateWTime

echo "<result>$formattedDateWTime</result>"