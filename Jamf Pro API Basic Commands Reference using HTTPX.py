#!/usr/bin/env python

"""NOTE: You'll need to install httpx: pip install httpx"""
import httpx

username = 'apiman'
password = 'apipass'
url = 'https://ganderson.jamfcloud.com/api/v1/' #note, in this example /api/v1/ at the end is needed for below. could change below and not need it up here if you wanted
"""This file is just a basic command refernce for the Jamf Pro API (the new one) using httpx module instead of requests"""

"""If you are coming from Requests, httpx.Client() is what you can use instead of requests.Session()."""
client = httpx.Client()

test = client.get("https://ganderson.jamfcloud.com/api/v1/advanced-mobile-device-searches", auth=('apiman', 'apipass'))
print(test)

"""This method gets us a bearer token from Jamf Pro."""
def getToken(url, jpUser, jpPass):
	try:
		print(jpPass)
		print(jpUser)
		response = client.post(url + "auth/token", auth=(jpUser, jpPass))
		print(url + "auth/token")
		print(response)
		
		if response.status_code == 401:
			return "bad creds"
		
		print(response)
		print(response.text)
		responseData = response.json()
		token = responseData["token"]
		print(token)
		return token
	except httpx.RequestError as error:
		errorMsg = str(error)
		print(f"error is {errorMsg}")
		return errorMsg

# Make an asynchronous call to getToken
# is async really needed?
getToken(url, username, password)
#print("Token:", token)






"""This method gets us a bearer token from Jamf Pro.
def getToken(url, jpUser, jpPass):
	try:
		response = client.post(url + "auth/token", auth = (jpUser, jpPass))
		print(response)
		if response.status_code == 401:
			return "bad creds"
		print(response)
		#print(response.text)
		print(f"this is the response data: {response.text}")
		responseData = response.json()
		token = responseData["token"]
		return token
	except httpx.HTTPError as error:
		errorMsg = str(error)
		return errorMsg
getToken(url, username, password)
"""

"""———————————————————————————————————————"""
"""We will use token auth like last time. Doing a simple GET here"""
"""———————————————————————————————————————"""
"""response = session.post(url + "auth/token", auth = (username, password))
print(response.text)
print(response)
response_data = response.json()
token = response_data["token"]
head = {'Authorization': f'Bearer {token}' }"""
"""Building on the Classic API examples, we're going to make some more 're-usable' formatting here with creating functions
The below is a simple GET
Realistically, this isn't the most useful task to use in this way, but we're still going to practice it here
Notice that the Jamf Pro API uses json formatting"""
"""def getAnItem(urlForCall, dataForHeader):
	response = session.get(urlForCall + "advanced-mobile-device-searches", headers=dataForHeader )
	content = response.text
	print(content)
getAnItem(url, head)
"""

"""———————————————————————————————————————"""
"""Time to POST an item"""
"""———————————————————————————————————————"""
"""jsonData = {"name":"Made by API2","priority":"9"}
def postAnItem(urlForCall, dataForHeader, dataForNewItem):"""
"""Thing to notice in this one is the use of the json parameter to encode it instead of data"""
"""client	response = session.post(urlForCall + "categories", headers=dataForHeader, json = dataForNewItem )
	content = response.text
	print(content)
postAnItem(url, head, jsonData)
"""

"""———————————————————————————————————————"""
"""Time to PUT an item. We are simply updating a few fields for script 16."""
"""———————————————————————————————————————"""
"""jsonData = {"name": "Updated Name via API", "notes": "using the API to PUT this here"}
def putAnItem(urlForCall, dataForHeader, dataForNewItem):
	response = session.put(urlForCall + "scripts/16", headers=dataForHeader, json = dataForNewItem )
	content = response.text
	print(content)
putAnItem(url, head, jsonData)

"""
"""———————————————————————————————————————"""
"""I intentionally did not include a DELETE,
my reasoning is that you should be able to figure that out based on the other commands
and _only_ should be running it if you are comfortable enough to produce your own solution
Never test in prod, especially if you have a loop of some sort"""
"""———————————————————————————————————————"""





