#!/usr/bin/env python

import requests
import json
import sys

username = 'USERNAME'
password = 'PASSWORD!'
groupID = 'GROUPIDHERE'
newPassword = "NEWPASSWORD"
#MDM or JMF
adminType = 'MDM'
computerIDs = []
clientManagementIDs = []
associatedUsernames = []
url = 'https://CLOUDINSTANCE.jamfcloud.com/' #note, in this example /api/v1/ at the end is needed for below. could change below and not need it up here if you wanted
"""This file is just a basic command refernce for the Jamf Pro API (the new one)"""

session = requests.Session()

"""———————————————————————————————————————"""
"""We will use token auth like last time. Doing a simple GET here"""
"""———————————————————————————————————————"""
response = session.post(url + "api/v1/auth/token", auth = (username, password))
print(response.text)
print(response)
response_data = response.json()
token = response_data["token"]
head = {'Authorization': f'Bearer {token}', "Accept": "application/json"}
"""Building on the Classic API examples, we're going to make some more 're-usable' formatting here with creating functions
The below is a simple GET
Realistically, this isn't the most useful task to use in this way, but we're still going to practice it here
Notice that the Jamf Pro API uses json formatting"""
def getAnItem(urlForCall, dataForHeader):
	response = session.get(urlForCall + f"JSSResource/computergroups/id/{groupID}", headers=dataForHeader)
	print(response.text)
	content = response.json()
	print(content)
	for x in content['computer_group']['computers']:
		print (x['id'])
		item = x['id']
		computerIDs.append(item)
getAnItem(url, head)

def getManagementID(url, dataForHeader, computerID):
	global clientManagementId
	"""This endpint only appears as computers-inventory in the API GUI"""
	response = session.get(url + f"api/v1/computers-inventory-detail/{computerID}", headers=dataForHeader)
	if response.status_code == 401:
		return "Token may have expired. Please close and reopen app."
	elif response.status_code == 200:
		content = response.json()
		clientManagementId = content["general"]["managementId"]
		print(clientManagementId)
		clientManagementIDs.append(clientManagementId)
		return clientManagementId
	elif response.status_code == 404:
		clientManagementId = "Unable"
		return "Unable"
	else:
		clientManagementId = "Unable"
		return "Unable to gather Client ID when executing the command. Most likely this computer ID either doesn't exist in Jamf Pro or was not configured for this workflow on enrollment"

	"""Get the LAPS capable admin accounts for a device. (returns just the account name)"""
def getLAPSAccount(url, dataForHeader, computerID):
	if computerID == "":
		return "Missing Computer ID"
	else:
		if clientManagementId.startswith("Unable") == True:
			return "Unable to get history, Client ManagementID appears to be incorrect. Most likely this computer ID doesn't exist."
		response = session.get(url + f"api/v2/local-admin-password/{clientManagementId}/accounts", headers=dataForHeader)
		print(f"{url}api/v2/local-admin-password/{clientManagementId}/accounts")
		if response.status_code == 401:
			return "Token may have expired. Please close and reopen app."
		elif response.status_code == 200:
			content = response.json()
			for x in content['results']:
				print(" ———————————————————————————————————————")
				if x['userSource'] == adminType:
					associatedUsernames.append(x['username'])
			try:
				lapsAccount = content['results'][0]['username']
				return lapsAccount
			except IndexError:
				return "This computer does not appear to have a LAPS enabled account."
		else:
			return "Something went wrong, please ensure your Jamf Pro version is greater than 10.45."

#getting the client management IDs useing computer ids
for x in computerIDs:
	print(f"first computer id is: {x}")
	print(type(x))
	getManagementID(url, head, x)

#getting the usernames using client management IDs
for y in clientManagementIDs:
	print(f"client management id is: {y}")
	getLAPSAccount(url, head, y)

for z in associatedUsernames:
	print(f"username collected is: {z}")

"""———————————————————————————————————————"""
"""Time to PUT the new pw """
"""———————————————————————————————————————"""
def putAnItem(urlForCall, dataForHeader, dataForNewItem, clientManagementId):
	response = session.put(urlForCall + f"api/v2/local-admin-password/{clientManagementId}/set-password", headers=dataForHeader, json = dataForNewItem )
	content = response.text
	print(content)
	print(response.status_code)

#checking things line up
if len(associatedUsernames) == len(clientManagementIDs) == len(computerIDs):
	print("numbers match, let's go")
else:
	sys.exit()
	#something isn't write if this goes, so we're exiting before editing anything

for clientManagementId in clientManagementIDs:
	print(f"setting the password for client management id of {clientManagementId}")
	index = clientManagementIDs.index(clientManagementId)
	curUsername = associatedUsernames[index]
	print(f"with associated username of {curUsername}")
	jsonData = {
    "lapsUserPasswordList": [
        {
            "username": curUsername,
            "password": newPassword
        }
    ]
}
	print("here is what our current json looks like")
	#print(jsonData)
	putAnItem(url, head, jsonData, clientManagementId)



"""Query a group of computers (ie a site)✅
computer group>computers>ID
snag the IDS of those✅
loop through them✅
grab clientmanagementid✅
query usernames✅
get MDM username from json✅
use the username and clientmanagement ID to update the password ✅ (if the computer it set up for it, it works)
disable laps """
