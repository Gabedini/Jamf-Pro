#!/usr/bin/env python
import requests
import customtkinter

username = ''
password = ''
#jpURL = 'https://jkezuol.kube.jamf.build'
"""This is a placeholder file for a fun project being worked on"""
session = requests.Session()

"""This method gets us a bearer token from Jamf Pro."""
def getToken(url, jpUser, jpPass):
	response = session.post(url + "auth/token", auth = (jpUser, jpPass))
	print(f"{url}auth/token")
	print(response)
	responseData = response.json()
	print(responseData)
	token = responseData["token"]
	print(f"this is the token: {token}")
	return token

"""Grabs the current settings in Jamf Pro"""
def getCurrentSettings(url, dataForHeader):
	response = session.get(url + "local-admin-password/settings", headers=dataForHeader )
	print(response)
	currentSettings = response.json()
	print(f"returning current settings {currentSettings}")
	return currentSettings

"""Enables LAPS if disabled"""
def enableIfDisabled(url, dataForHeader):
	print("is this thing on?")
	if currentAutoDeployEnabled == False:
		print("Currently disbaled, activating")
		"""putting the 'current' variables in here, likely would make more sense to update these independently, but this can work as default data for now
		It won't accept leaving out data points, we need to supply them all, it seems. I'll look to see if we can skip them somehow, later"""
		jsonToEnable = {"autoDeployEnabled":"true", "passwordRotationTime":currentPasswordRotationTime, "autoExpirationTime":currentAutoExpirationTime}
		response = session.put(url + "local-admin-password/settings", headers=dataForHeader, json = jsonToEnable)
		print(f"attempt to enable response: {response}")
		content = response.text
		print(content)
		print('print something about this not working on machines enrolled before selecting this option')
		return content
	else:
		print("LAPS already enabled, skipping")
"""Note: not sure in what context this would useful other than initial setup, as this would need to be enabled prior to machine enrollment.
I'll probably just make this a button and then mention that in the GUI somewhere"""
#enableIfDisabled(jpURL, head)


"""Get LAPS password viewed history. (returns the whole json for formatting later)"""
def getViewedHistory(url, dataForHeader, clientManagementId, username):
	if clientManagementId == "" or username == "":
		print("Missing Client Management ID or Username")
		return "Missing Client Management ID or Username"
	else:
		response = session.get(url + f"local-admin-password/{clientManagementId}/account/{username}/audit", headers=dataForHeader )
		print(f"history collection response: {response}")
		history = response.json()
		print(f"is it running the history function? {history}")
		return history

"""Get current LAPS password for specified username on a client. (returns just the password)"""
def getLAPSPassword(url, dataForHeader, clientManagementId, username):
	if clientManagementId == "" or username == "":
		print("Missing Client Management ID or Username")
		return "Missing Client Management ID or Username"
	else:
		response = session.get(url + f"local-admin-password/{clientManagementId}/account/{username}/password", headers=dataForHeader )
		print(response)
		content = response.json()
		print(f"{url}local-admin-password/{clientManagementId}/account/{username}/password")
		print(content)
		lapsPass = content["password"]
		return lapsPass

"""Get the LAPS capable admin accounts for a device. (returns just the account name)"""
def getLAPSAccount(url, dataForHeader, clientManagementId):
	if clientManagementId == "":
		print("Missing Client Management ID")
		return "Missing Client Management ID"
	else:
		response = session.get(url + f"local-admin-password/{clientManagementId}/accounts", headers=dataForHeader )
		print(f"password collection response: {response}")
		content = response.json()
		print(content)
		lapsAccount = content["username"]
		print(f"Returning Account: {lapsAccount}")
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
		self.grid_columnconfigure((0, 3), weight=1)
		
		self.inputURL = customtkinter.CTkEntry(master=self, placeholder_text="https://example.com")
		self.inputURL.pack(pady=12, padx=10)

		self.inputUsernm = customtkinter.CTkEntry(master=self, placeholder_text="Username")
		self.inputUsernm.pack(pady=12, padx=10)
		
		self.inputPasswd = customtkinter.CTkEntry(master=self, placeholder_text="Password", show="*")
		self.inputPasswd.pack(pady=12, padx=10)
		
		self.loginButton = customtkinter.CTkButton(master=self, text="Login", command=self.userLogin)
		self.loginButton.pack(padx=20, pady=20)


	def enabling(self):
		enableIfDisabled(jpURL, head)
		print("you clicked the enable laps button")

	def lapsPass(self):
		getLAPSPassword(jpURL, head, self.inputClientManagementId.get(), self.inputComputerUser.get())
		print("you clicked the collecting password button")

	def gettingHistory(self):
		getViewedHistory(jpURL, head, self.inputClientManagementId.get(), self.inputComputerUser.get())
		print("you clicked the getting laps history button")

	def lapsAccount(self):
		getLAPSAccount(jpURL, head, self.inputClientManagementId.get())
		print("you clicked the getting account button")

	def optionPage(self):
		self.inputClientManagementId = customtkinter.CTkEntry(master=self, placeholder_text="Client Management ID")
		self.inputClientManagementId.grid(row=0, column=0, pady=12, padx=10)

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


		"""gets and sets token (note: token is app global but not program global)"""
		token = getToken(jpURL, username, password)
		print(token)
		"""puts token in header for us to pass later"""
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
		self.optionPage()


if __name__ == "__main__":
	app = App()
	app.mainloop()




#SDG
