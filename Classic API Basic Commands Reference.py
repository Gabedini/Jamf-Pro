#!/usr/bin/env python
import requests
import json

username = ''
password = ''
url = 'https://INSTANCE_NAME_HERE.jamfcloud.com/'
"""This file is just a basic command reference for the Jamf Pro Classic API"""

"""———————————————————————————————————————"""
"""About as basic as it gets. Note: Classic API Defualts XML return."""
"""———————————————————————————————————————"""
response = requests.get(url + "JSSResource/computers", auth = (username, password))
content = response.text
print(content)


"""———————————————————————————————————————"""
"""About as basic as it gets, except we ask for json formatting"""
"""———————————————————————————————————————"""
response = requests.get(url + "JSSResource/mobiledevices", auth = (username, password), headers = {"Accept": "application/json"})
jsoncontent = response.json()
print(jsoncontent)


"""———————————————————————————————————————"""
"""POSTing an item and supplying the XML for it"""
"""———————————————————————————————————————"""
xmlData = "<category><name>Getting Started with Python</name><priority>1</priority></category>"
response = requests.post(url + "JSSResource/categories", auth = (username, password), data = xmlData )
content = response.text
print(content)


"""———————————————————————————————————————"""
"""PUTing computer of ID 8 into a different site using json
Just kidding, you can't do that with the classic API, only XML"""
"""———————————————————————————————————————"""
modifyComputerSite = "<computer><general><site><name>Eau Claire</name></site></general></computer>"
response = requests.put(url + "JSSResource/computers/id/8", auth = (username, password), data = modifyComputerSite )
content = response.text
print(content)


"""———————————————————————————————————————"""
"""I intentionally did not include a DELETE,
my reasoning is that you should be able to figure that out based on the other commands
and _only_ should be running it if you are comfortable enough to produce your own solution
Never test in prod, especially if you have a loop of some sort"""
"""———————————————————————————————————————"""


"""———————————————————————————————————————"""
"""A requests session should help speed things up when doing multiple calls.
However, it may also present other considerations when doing so, as such, it may not be worth the performance gain in *all* scenarios
(This would be accompanied by a session.get instead of requests.get)"""
"""———————————————————————————————————————"""
session = requests.Session()


"""———————————————————————————————————————"""
"""Getting a bearer token and proving it works with a simple GET"""
"""———————————————————————————————————————"""
response = requests.post(url + "api/v1/auth/token", auth = (username, password))
response_data = response.json()
"""We can call the specific json value 'token' with this formatting, run a print on the token and response.json values if you want to see it in action"""
token = response_data["token"]
"""note the f string to include Bearer, that is needed, example https://docs.jamf.com/education-services/resources/20230120/Resources_300_Lesson_10.html"""
head = {'Authorization': f'Bearer {token}' }
response = requests.get(url + "JSSResource/networksegments", headers=head )
content = response.text
print(content)







