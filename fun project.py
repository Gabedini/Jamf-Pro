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
		logs.write(f"{datetime.now().strftime(' %Y-%m-%d %H:%M:%S')} Getting token from: {url}auth/token")
		logs.write(response.text)
		responseData = response.json()
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Reply: {str(responseData)}")
		token = responseData["token"]
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} This is the token: {token}")
		return token
	except requests.exceptions.MissingSchema as error:
		errorMsg = str(error)
		print(f"testing print of error {errorMsg}")
		return errorMsg

"""Grabs the current settings in Jamf Pro"""
def getCurrentSettings(url, dataForHeader):
	response = session.get(url + "local-admin-password/settings", headers=dataForHeader )
	logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Collecting Current settings: {response.text}")
	currentSettings = response.json()
	logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} returning current settings {currentSettings}")
	return currentSettings

def getManagmentID(url, dataForHeader, computerID):
	global clientManagementId
	response = session.get(url + f"computers-inventory-detail/{computerID}", headers=dataForHeader )
	logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Collecting Managment ID for: {url}computers-inventory-detail/{computerID}")
	content = response.json()
	clientManagementId = content["general"]["managementId"]
	logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Collected managemend ID: {clientManagementId}")
	return clientManagementId


"""Enables LAPS if disabled"""
def enableIfDisabled(url, dataForHeader):
	print("is this thing on?")
	if currentAutoDeployEnabled == False:
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Currently disbaled, activating")
		"""putting the 'current' variables in here, likely would make more sense to update these independently, but this can work as default data for now
		It won't accept leaving out data points, we need to supply them all, it seems. I'll look to see if we can skip them somehow, later"""
		jsonToEnable = {"autoDeployEnabled":"true", "passwordRotationTime":currentPasswordRotationTime, "autoExpirationTime":currentAutoExpirationTime}
		response = session.put(url + "local-admin-password/settings", headers=dataForHeader, json = jsonToEnable)
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} attempt to enable response: {response}")
		content = response.text
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {content}")
		print('print something about this not working on machines enrolled before selecting this option')
		return content
	else:
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} LAPS already enabled, skipping...")
		return "LAPS already enabled, skipping"
"""Note: not sure in what context this would useful other than initial setup, as this would need to be enabled prior to machine enrollment.
I'll probably just make this a button and then mention that in the GUI somewhere"""
#enableIfDisabled(jpURL, head)


"""Get LAPS password viewed history. (returns the whole json for formatting later)"""
def getViewedHistory(url, dataForHeader, computerID, username):
	if computerID == "" or username == "":
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Computer ID or Username")
		return "Missing Computer ID or Username"
	else:
		if clientManagementId == "":
			logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Client Management ID, collecting...")
			clientManagementID = getManagmentID(jpURL, head, computerID)
		response = session.get(url + f"local-admin-password/{computerID}/account/{username}/audit", headers=dataForHeader )
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} History collection response: {response}")
		history = response.json()
		print(f"is it running the history function? {history}")
		return history

"""Get current LAPS password for specified username on a client. (returns just the password)"""
def getLAPSPassword(url, dataForHeader, computerID, username):
	if computerID == "" or username == "":
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Computer ID or Username")
		return "Missing Computer ID or Username"
	else:
		if clientManagementId == "":
			logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Client Management ID, collecting...")
			clientManagementID = getManagmentID(jpURL, head, computerID)
		response = session.get(url + f"local-admin-password/{computerID}/account/{username}/password", headers=dataForHeader )
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {response.text}")
		content = response.json()
		print(f"{url}local-admin-password/{computerID}/account/{username}/password")
		print(content)
		lapsPass = content["password"]
		return lapsPass

"""Get the LAPS capable admin accounts for a device. (returns just the account name)"""
def getLAPSAccount(url, dataForHeader, computerID):
	logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Getting LAPS Enabled Account for computer ID:  {computerID}")
	if computerID == "":
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Computer ID")
		return "Missing Computer ID"
	else:
		if clientManagementId == "":
			logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Missing Client Management ID, collecting...")
			clientManagementID = getManagmentID(jpURL, head, computerID)
		response = session.get(url + f"local-admin-password/{clientManagementId}/accounts", headers=dataForHeader )
		print(f"{url}local-admin-password/{clientManagementId}/accounts")
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Password collection response: {response}")
		content = response.json()
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {content}")
		lapsAccount = content['results'][0]['username']
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Returning Account: {lapsAccount}")
		return lapsAccount



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


	def enabling(self):
		output = enableIfDisabled(jpURL, head)
		print(f"Printing the return from the enable laps button{output}")
		self.outputBox.insert("insert", f"{output}" + "\n")
		print("you clicked the enable laps button")

	def lapsPass(self):
		output = getLAPSPassword(jpURL, head, self.inputComputerID.get(), self.inputComputerUser.get())
		print(f"Printing the return from the collecting password button{output}")
		self.outputBox.insert("insert", f"{output}" + "\n")
		print("you clicked the collecting password button")

	def gettingHistory(self):
		output = getViewedHistory(jpURL, head, self.inputComputerID.get(), self.inputComputerUser.get())
		print(f"Printing the return from the getting laps history button{output}")
		self.outputBox.insert("insert", f"{output}" + "\n")
		print("you clicked the getting laps history button")

	def lapsAccount(self):
		output = getLAPSAccount(jpURL, head, self.inputComputerID.get())
		print(f"Printing the return from the getting account button{output}")
		self.outputBox.insert("insert", f"{output}" + "\n")
		print("you clicked the getting account button")

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
		logs.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Logging into {jpURL} with username {username}")


		"""gets and sets token (note: token is app global but not program global)"""
		token = getToken(jpURL, username, password)
		print(token)
		"""puts token in header for us to pass later"""
		if token.startswith("Invalid URL") == True:
			self.outputBox = customtkinter.CTkTextbox(master=self)
			self.outputBox.pack(padx=20, pady=20)
			self.outputBox.insert("insert", f"{token}")
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
		self.outputBox.pack_forget()
		self.optionPage()


if __name__ == "__main__":
	app = App()
	app.mainloop()




#SDG
