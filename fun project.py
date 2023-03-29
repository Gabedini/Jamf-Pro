#!/usr/bin/env python
import requests
import customtkinter
from datetime import datetime

username = ''
password = ''
#jpURL = 'https://jkezuol.kube.jamf.build'
"""This is a placeholder file for a fun project being worked on"""
session = requests.Session()
logs = open("/tmp/LAPSTool.log", "a")
global clientManagementId
clientManagementId = ""

"""This method gets us a bearer token from Jamf Pro."""
def getToken(url, jpUser, jpPass):
	try:
		response = session.post(url + "auth/token", auth = (jpUser, jpPass))
		print(response)
		if response.status_code == 401:
			logs.write(f"\n{datetime.now().strftime(' %Y-%m-%d %H:%M:%S')} Tried to get a token: {response} - incorrect username or password.")
			return "bad creds"
		logs.write(f"\n{datetime.now().strftime(' %Y-%m-%d %H:%M:%S')} Getting token from: {url}auth/token")
		responseData = response.json()
		token = responseData["token"]
		return token
	except requests.exceptions.MissingSchema as error:
		errorMsg = str(error)
		logs.write(f"\n{datetime.now().strftime(' %Y-%m-%d %H:%M:%S')} Seems like the URL was malformed: {errorMsg}")
		return errorMsg

"""Grabs the current settings in Jamf Pro"""
def getCurrentSettings(url, dataForHeader):
	response = session.get(url + "local-admin-password/settings", headers=dataForHeader)
	if response.status_code == 401:
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Attempt to collect Current LAPS Settings: {response} - the token may have expired. Please close and reopen app....")
		return "Token may have expired. Please close and reopen app."
	elif response.status_code == 200:
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Collecting current settings: {response.text}")
		currentSettings = response.json()
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} returning current settings: {currentSettings}")
		return currentSettings
	else:
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Something went wrong collecting the current settings. It may be that simply your Jamf Pro does not support this endpoint")
		return "Something went wrong, please ensure your Jamf Pro version is greater than 10.45."

"""Gets the Client Management ID from the computer record"""
def getManagementID(url, dataForHeader, computerID):
	global clientManagementId
	"""This endpint only appears as computers-inventory in the API GUI"""
	response = session.get(url + f"computers-inventory-detail/{computerID}", headers=dataForHeader)
	if response.status_code == 401:
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Attempt to collect Client Management ID: {response} - the token may have expired. Please close and reopen app....")
		return "Token may have expired. Please close and reopen app."
	elif response.status_code == 200:
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Collecting Managment ID for: {url}computers-inventory-detail/{computerID}")
		content = response.json()
		clientManagementId = content["general"]["managementId"]
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Collected managemend ID: {clientManagementId}")
		return clientManagementId
	else:
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Something went wrong. It may be that the computerID or local admin account supplied were unrecognized by the server, or that simply your Jamf Pro does not support this endpoint")
		return "Unable to gather Client ID when executing the command. Most likely this computer ID either doesn't exist in Jamf Pro or was not configured for this workflow on enrollment"

"""Enables LAPS if disabled"""
def enableIfDisabled(url, dataForHeader):
	print("is this thing on?")
	if currentAutoDeployEnabled == False:
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Currently disabled, activating")
		"""putting the 'current' variables in here, likely would make more sense to update these independently, but this can work as default data for now
		It won't accept leaving out data points, we need to supply them all, it seems. I'll look to see if we can skip them somehow, later"""
		jsonToEnable = {"autoDeployEnabled":"true", "passwordRotationTime":currentPasswordRotationTime, "autoExpirationTime":currentAutoExpirationTime}
		response = session.put(url + "local-admin-password/settings", headers=dataForHeader, json = jsonToEnable)
		if response.status_code == 401:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Attempt to enable LAPS: {response} - the token may have expired. Please close and reopen app....")
			return "Token may have expired. Please close and reopen app."
		elif response.status_code == 200:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Attempt to enable LAPS: {response}")
			content = response.text
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {content}")
			print('consider printing something about this not working on machines enrolled before selecting this option')
			return content
		else:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} If this option errors out it likely means it was a connection error. Closing and re-opening should clear that up.")
			return "Something went wrong, please ensure your Jamf Pro version is greater than 10.45."
	else:
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} LAPS already enabled, skipping...")
		return "LAPS already enabled, skipping"
"""Note: not sure in what context this would useful other than initial setup, as this would need to be enabled prior to machine enrollment.
I'll probably just make this a button and then mention that in the GUI somewhere"""


"""Get LAPS password viewed history. (returns the whole json for formatting later if we feel like it)"""
def getViewedHistory(url, dataForHeader, computerID, username):
	global clientManagementId
	if computerID == "" or username == "":
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Computer ID or Username")
		return "Missing Computer ID or Username"
	else:
		if clientManagementId == "":
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Client Management ID, collecting...")
			clientManagementId = getManagementID(jpURL, head, computerID)
			if clientManagementId.startswith("Unable") == True:
				return "Unable to get history, Client ManagementID appears to be incorrect. Most likely this computer ID doesn't exist."
		response = session.get(url + f"local-admin-password/{clientManagementId}/account/{username}/audit", headers=dataForHeader)
		if response.status_code == 401:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} History collection: {response} - the token may have expired. Please close and reopen app....")
			return "Token may have expired. Please close and reopen app."
		elif response.status_code == 200:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} History collection: {response}")
			history = response.json()
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} History: {history}")
			return history
		else:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Something went wrong. It may be that the computerID or local admin account supplied were unrecognized by the server, or that simply your Jamf Pro does not support this endpoint")
			return "Something went wrong, please ensure your Jamf Pro version is greater than 10.45 and that this computer is configured for this workflow."

"""Get current LAPS password for specified username on a client. (returns just the password)"""
def getLAPSPassword(url, dataForHeader, computerID, username):
	global clientManagementId
	if computerID == "" or username == "":
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Computer ID or Username")
		return "Missing Computer ID or Username"
	else:
		if clientManagementId == "":
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Client Management ID, collecting...")
			clientManagementId = getManagementID(jpURL, head, computerID)
			if clientManagementId.startswith("Unable") == True:
				return "Unable to get history, Client ManagementID appears to be incorrect. Most likely this computer ID doesn't exist."
		response = session.get(url + f"local-admin-password/{clientManagementId}/account/{username}/password", headers=dataForHeader)
		if response.status_code == 401:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Password collection: {response} - the token may have expired. Please close and reopen app....")
			return "Token may have expired. Please close and reopen app."
		elif response.status_code == 200:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Password collection: {response}. Printing to GUI")
			content = response.json()
			lapsPass = content["password"]
			return lapsPass
		else:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Something went wrong. It may be that the computerID or local admin account supplied were unrecognized by the server, or that simply your Jamf Pro does not support this endpoint")
			return "Something went wrong, please ensure your Jamf Pro version is greater than 10.45."

"""Get the LAPS capable admin accounts for a device. (returns just the account name)"""
def getLAPSAccount(url, dataForHeader, computerID):
	global clientManagementId
	logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Getting LAPS Enabled Account for computer ID:  {computerID}")
	if computerID == "":
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Computer ID")
		return "Missing Computer ID"
	else:
		if clientManagementId == "":
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Client Management ID, collecting...")
			clientManagementId == getManagementID(jpURL, head, computerID)
			if clientManagementId.startswith("Unable") == True:
				return "Unable to get history, Client ManagementID appears to be incorrect. Most likely this computer ID doesn't exist."
		response = session.get(url + f"local-admin-password/{clientManagementId}/accounts", headers=dataForHeader)
		print(f"{url}local-admin-password/{clientManagementId}/accounts")
		if response.status_code == 401:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Account collection: {response} - the token may have expired. Please close and reopen app....")
			return "Token may have expired. Please close and reopen app."
		elif response.status_code == 200:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Account collection: {response}")
			content = response.json()
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {content}")
			lapsAccount = content['results'][0]['username']
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Account Found: {lapsAccount}")
			return lapsAccount
		else:
			logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Something went wrong. It may be that the computerID or local admin account supplied were unrecognized by the server, or that simply your Jamf Pro does not support this endpoint")
			return "Something went wrong, please ensure your Jamf Pro version is greater than 10.45."


"""———————————————————————————————————————"""
"""Below this line is all the GUI items"""
"""———————————————————————————————————————"""
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")
class App(customtkinter.CTk):
	def __init__(self):
		super().__init__()
		self.title("LAPS Tool")
		self.minsize(400, 300)

		self.grid_rowconfigure((0, 1), weight=1)
		self.grid_columnconfigure((0, 4), weight=1)
		
		self.inputURL = customtkinter.CTkEntry(master=self, placeholder_text="https://example.com")
		self.inputURL.pack(pady=12, padx=10)

		self.inputUsernm = customtkinter.CTkEntry(master=self, placeholder_text="Username")
		self.inputUsernm.pack(pady=12, padx=10)
		
		self.inputPasswd = customtkinter.CTkEntry(master=self, placeholder_text="Password", show="*")
		self.inputPasswd.pack(pady=12, padx=10)
		
		self.loginButton = customtkinter.CTkButton(master=self, text="Login", command=self.userLogin)
		self.loginButton.pack(padx=20, pady=20)

		"""This is used later to ensure that we don't add our box to the GUI twice"""
		self.outputBox = None

	def enabling(self):
		output = enableIfDisabled(jpURL, head)
		self.outputBox.insert("insert", f"{output}\n")

	def lapsPass(self):
		output = getLAPSPassword(jpURL, head, self.inputComputerID.get(), self.inputComputerUser.get())
		self.outputBox.insert("insert", f"{output}\n")

	def gettingHistory(self):
		output = getViewedHistory(jpURL, head, self.inputComputerID.get(), self.inputComputerUser.get())
		self.outputBox.insert("insert", f"{output}\n")

	def lapsAccount(self):
		output = getLAPSAccount(jpURL, head, self.inputComputerID.get())
		self.outputBox.insert("insert", f"{output}\n")

	def optionPage(self):
		self.inputComputerID = customtkinter.CTkEntry(master=self, placeholder_text="Computer ID")
		self.inputComputerID.grid(row=0, column=0, pady=12, padx=10)

		self.inputComputerUser = customtkinter.CTkEntry(master=self, placeholder_text="Local Admin Acount")
		self.inputComputerUser.grid(row=0, column=1, pady=12, padx=10)

		self.enableLAPS = customtkinter.CTkButton(master=self, text="Enable LAPS", command=self.enabling)
		self.enableLAPS.grid(row=1, column=0, padx=20, pady=20)

		self.collectViewedHistory = customtkinter.CTkButton(master=self, text="Collect PW Viewed History", command=self.gettingHistory)
		self.collectViewedHistory.grid(row=1, column=1, padx=20, pady=20)

		self.collectCurrentPassword = customtkinter.CTkButton(master=self, text="Collect Current PW", command=self.lapsPass)
		self.collectCurrentPassword.grid(row=2, column=0, padx=20, pady=20)

		self.collectLAPSAccount = customtkinter.CTkButton(master=self, text="Collect LAPS capable Admin", command=self.lapsAccount)
		self.collectLAPSAccount.grid(row=2, column=1, padx=20, pady=20)

		self.outputBox = customtkinter.CTkTextbox(master=self)
		self.outputBox.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

	def userLogin(self):
		"""anything that might be referenced outside of the GUI button functions is global"""
		global jpURL
		global head
		global currentAutoDeployEnabled
		global currentPasswordRotationTime
		global currentAutoExpirationTime
		
		print("login button pressed")
		username = self.inputUsernm.get()
		password = self.inputPasswd.get()
		jpURL = f"{self.inputURL.get()}/api/v1/"
		print(username)
		print(password)
		print(jpURL)#debugging purposes
		logs.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Logging into {jpURL} with username {username}")


		"""gets and sets token (note: token is app global but not program global)"""
		token = getToken(jpURL, username, password)
		print(token)
		"""puts token in header for us to pass later"""
		if token.startswith("Invalid URL") == True:
			if self.outputBox is None:
				self.outputBox = customtkinter.CTkTextbox(master=self)
				self.outputBox.pack(padx=20, pady=20)
			self.outputBox.insert("insert", f"{token}")
		if token == "bad creds":
			if self.outputBox is None:
				self.outputBox = customtkinter.CTkTextbox(master=self)
				self.outputBox.pack(padx=20, pady=20)
			self.outputBox.insert("insert", "Incorrect username or password entered.")

		head = {'Authorization': f'Bearer {token}' }

		"""gets and returns whatever the current settings are"""
		currentSettings = getCurrentSettings(jpURL, head)
		print(currentSettings)
		"""———————————————————————————————————————"""
		"""For reference if needed later"""
		"""Setting means: Whether LAPS is enabled"""
		currentAutoDeployEnabled = currentSettings["autoDeployEnabled"]
		print(currentAutoDeployEnabled)
		"""Setting means: The length of time between viewing a local admin password and rotating the password — the default is one hour"""
		currentPasswordRotationTime = currentSettings["passwordRotationTime"]
		print(currentPasswordRotationTime)
		"""Setting means: The length of time Jamf Pro routinely rotates the local admin password — the default is 90 days"""
		currentAutoExpirationTime = currentSettings["autoExpirationTime"]
		print(currentAutoExpirationTime)
		"""———————————————————————————————————————"""

		self.loginButton.pack_forget()
		self.inputUsernm.pack_forget()
		self.inputPasswd.pack_forget()
		self.inputURL.pack_forget()
		if self.outputBox is None:
			print("good to go")
		else:
			self.outputBox.pack_forget()
		self.optionPage()

if __name__ == "__main__":
	app = App()
	app.mainloop()




#SDG
