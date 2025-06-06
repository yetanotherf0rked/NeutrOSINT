from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException

import time
import os
import re
import json
import requests
import dns.resolver
from datetime import datetime
from colorama import Fore, Style

DOMAINS = ["proton.me", "protonmail.com", "pm.me", "protonmail.ch", "passmail.net"]

class NeutrOSINT():
	def __init__(self):
		self.driver = None
		self.username = None
		self.password = None
		self.emails = []
		self.time = 16
		self.output_file = None
		self.proxy = {}
		self.light = False
		self.key = False
		self.max_retries = 0
		self.login_url = "https://account.proton.me/mail"

	def banner(self):
		print("""

		  ██████   █████                      █████                 ███████     █████████  █████ ██████   █████ ███████████                 ████████ 
		 ░░██████ ░░███                      ░░███                ███░░░░░███  ███░░░░░███░░███ ░░██████ ░░███ ░█░░░███░░░█                ███░░░░███
		  ░███░███ ░███   ██████  █████ ████ ███████   ████████  ███     ░░███░███    ░░░  ░███  ░███░███ ░███ ░   ░███  ░     █████ █████░░░    ░███
		  ░███░░███░███  ███░░███░░███ ░███ ░░░███░   ░░███░░███░███      ░███░░█████████  ░███  ░███░░███░███     ░███       ░░███ ░░███    ███████ 
		  ░███ ░░██████ ░███████  ░███ ░███   ░███     ░███ ░░░ ░███      ░███ ░░░░░░░░███ ░███  ░███ ░░██████     ░███        ░███  ░███   ███░░░░  
		  ░███  ░░█████ ░███░░░   ░███ ░███   ░███ ███ ░███     ░░███     ███  ███    ░███ ░███  ░███  ░░█████     ░███        ░░███ ███   ███      █
		  █████  ░░█████░░██████  ░░████████  ░░█████  █████     ░░░███████░  ░░█████████  █████ █████  ░░█████    █████        ░░█████   ░██████████
		 ░░░░░    ░░░░░  ░░░░░░    ░░░░░░░░    ░░░░░  ░░░░░        ░░░░░░░     ░░░░░░░░░  ░░░░░ ░░░░░    ░░░░░    ░░░░░          ░░░░░    ░░░░░░░░░░ 

			""")

	def setup(self):
		chrome_options = Options()
		chrome_options.add_argument("--headless")
		chrome_options.add_argument('--no-sandbox')
		#chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"')

		if(len(self.proxy) != 0):
			chrome_options.add_argument('--proxy-server=%s' % self.proxy)

		self.driver = webdriver.Chrome(options=chrome_options)

		try:
			self.driver.get(self.login_url)
		except:
			print(f"{Fore.YELLOW}[!] Error! Verify the arguments given to the command line...\n{Style.RESET_ALL}")
	
	def set_email(self, email):
		if "@" not in email:
			self.emails = [f"{email}@{domain}" for domain in DOMAINS]
		else:
			self.emails = [ email ]

	def set_username(self, username):
		self.username = username

	def set_password(self, password):
		self.password = password

	def set_output_file(self, file):
		self.output_file = file

	def set_proxy(self, proxy):
		self.proxy = proxy

	def set_key(self, key):
		self.key = key

	def set_light_mode(self, light):
		self.light = light

	def load_emails(self, file):
		try:
			handle = open(file, 'r')
			lines = handle.read().splitlines()
			for line in lines:
				if "@" not in line:
					for domain in DOMAINS:
						self.emails.append(f"{line}@{domain}")
				else:
					self.emails.append(line)

			handle.close()

			#Tell the user the API limit will be exceeded
			if(len(self.emails) > 100):
				if(self.light):
					print(f"{Fore.YELLOW}[?] Warning! There are more than 100 email addresses to check. The API's limit is 100 requests. All the email addresses won't be tested. You can either use the credentials mode (--username and --password) or use a proxy (--proxy)\n{Style.RESET_ALL}")

		except:
			print(f"{Fore.RED}[-] Unable to load emails{Style.RESET_ALL}")
			exit()
		
	def write_to_file(self, data):
		try:
			handle = open(self.output_file, "a")
			handle.write(data)
			handle.close()
		except:
			print(f"{Fore.RED}[-] Unable to save data to file{Style.RESET_ALL}")
			exit()

	def login(self):
		try:
			print(f"{Fore.YELLOW}[?] Connecting to ProtonMail with credentials...{Style.RESET_ALL}")

			#Find the username field
			element = WebDriverWait(self.driver, self.time).until(EC.presence_of_element_located((By.ID, 'username')))
			user_element = self.driver.find_element(By.ID,'username')
			user_element.send_keys(self.username)

			#Find the password field
			element = WebDriverWait(self.driver, self.time).until(EC.presence_of_element_located((By.ID, 'password')))
			password_element = self.driver.find_element(By.ID,'password') 
			password_element.send_keys(self.password)

			#Submit the form
			#password_element.submit()
			element = WebDriverWait(self.driver, self.time).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[4]/div[1]/main/div[1]/div[2]/form/button')))
			login_element = self.driver.find_element(By.XPATH,'/html/body/div[1]/div[4]/div[1]/main/div[1]/div[2]/form/button') 
			login_element.click()

			#Wait to connect to our account
			time.sleep(self.time)

			# Check if the URL is still the login form. In that case, login failed
			WebDriverWait(self.driver, self.time).until(EC.url_to_be("https://mail.proton.me/u/0/inbox"))

			print(f"{Fore.GREEN}[+] Connected to ProtonMail\n{Style.RESET_ALL}")
		except:
			print(f"{Fore.RED}[-] Error when connecting to ProtonMail...{Style.RESET_ALL}")
			exit()

	def clear_element(self, method, element_path):
		try:
			wait_element = WebDriverWait(self.driver, self.time).until(EC.presence_of_element_located((method, element_path)))
			element = self.driver.find_element(method, element_path)
			element.clear()
		except:
			print(f"{Fore.RED}[-] Unable to clear the element{Style.RESET_ALL}")
			exit()

	def new_email(self):
		try:
			print(f"{Fore.YELLOW}[?] Accessing 'New email' to check email addresses...{Style.RESET_ALL}")
			#Retrieve the "New email" button
			element = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div/div/div/div[1]/div[2]/button')))
			new_email_element = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/div/div[1]/div[2]/button')

			new_email_element.click()

			#Retrieve the "To" field to insert emails
			element = WebDriverWait(self.driver, self.time).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[4]/div/div/div/div/div/div[2]/div/div/div/div/div/div/input')))
			to_email_element = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div/div/div/div/div/div[2]/div/div/div/div/div/div/input')

			print(f"{Fore.YELLOW}[?] Checking email addresses...{Style.RESET_ALL}\n")

			#Create a copy of emails to avoid the modifications
			tmp_emails_array = self.emails[:]

			while(len(tmp_emails_array) > 100):
				#Check the first 100 emails
				emails_to_check_str = ','.join(tmp_emails_array[:100])
				#Convert list to string + add "," at the end (for the last occurence to be updated)
				emails_to_check_str += ','

				#Write all emails in the "To" field and wait until protonmail detects if they exist or not
				to_email_element.send_keys(emails_to_check_str)

				self.check_emails(tmp_emails_array[:100])

				#Remove the first 100 email addresses
				tmp_emails_array = tmp_emails_array[100:]
				#Clear the 'To' field
				to_email_element.clear()

			#If we are here it means there are less than 100 email addresses
			emails_to_check_str = ','.join(tmp_emails_array)
			#Convert list to string + add "," at the end (for the last occurence to be updated)
			emails_to_check_str += ','

			#Write all emails in the "To" field and wait until protonmail detects if they exist or not
			to_email_element.send_keys(emails_to_check_str)
			self.check_emails(tmp_emails_array)

		except TimeoutException:
			if(self.max_retries == 1):
				print(f"{Fore.RED}[-] Too many retries. Try to launch the script again{Style.RESET_ALL}")
				exit()
			self.max_retries = self.max_retries + 1
			print(f"{Fore.RED}[-] Unable to access new email to check email addresses. Trying again...{Style.RESET_ALL}")
			self.new_email()

	def extract_pgp_key_information(self, email):
		source_code = requests.get('https://api.protonmail.ch/pks/lookup?op=index&search=' + email)

		try:
			result = re.search(r'pub:([a-f0-9]+):(?:\d+):(\d+)?:(\d+)::', source_code.text)
			if(result):
				fingerprint = result.group(1)
				if(result.group(2) == "2048"):
					key_type = "RSA 2048"
				elif(result.group(2) == "4096"):
					key_type = "RSA 4096"
				else:
					key_type = "ECC Curve25519"
				timestamp = datetime.fromtimestamp(int(result.group(3)))

				return fingerprint, key_type, timestamp
		except AttributeError:
			#print(Fore.RED + "[-] Error! Impossible to retrieve the creation date. Maybe API restriction...{Style.RESET_ALL}")
			return None

	def format_pgp_key_information(self, fingerprint, key_type, timestamp):
		return f"PGP key creation date: {str(timestamp)} - Fingerprint: {str(fingerprint)} - Algorithm: {str(key_type)}"

	def get_pgp_public_key(self, email):
		if(self.key):
			return requests.get('https://api.protonmail.ch/pks/lookup?op=get&search=' + email).text
		return ""

	def is_syntax_correct(self, email):
		return re.match('([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email)

	def is_proton_domain(self, email):
		return email.split("@")[1] in DOMAINS

	def check_domain(self, email):
		try:
			if(not self.is_proton_domain(email)):
				for data in dns.resolver.query(email.split("@")[1], "MX"):
					if("protonmail" in data.to_text()):
						return True
			return False
		except dns.resolver.NXDOMAIN:
			print(f"{Fore.RED}[-] Domain doesn't exist...{Style.RESET_ALL}")
			return False
		except dns.resolver.LifetimeTimeout:
			print(f"{Fore.RED}[-] DNS timeout error... Please verify your connection{Style.RESET_ALL}")
			return False

	#Pass emails as argument to use for printing (pass tmp_emails_array)
	def check_emails(self, emails):
		try:
			#Retrieve the emails we inserted in the input field
			element = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[4]/div/div/div/div/div/div[2]/div/div/div/div/div/div')))
			elements_to_loop = self.driver.find_elements(By.XPATH, '/html/body/div[1]/div[4]/div/div/div/div/div/div[2]/div/div/div/div/div/div')

			#Remove the last div (which is always null)
			elements_to_loop = elements_to_loop[:-1]

			count = 0

			time.sleep(1)

			#Loop over all divs
			for item in elements_to_loop:
				if(not self.is_syntax_correct(emails[count])):
					print(f"{Fore.RED}[-] Invalid format: {Style.RESET_ALL}{emails[count]}")
					count = count + 1
					continue

				#foreach retrieve their classes
				class_str = item.get_attribute('class')

				print()

				if("invalid" in class_str):
					if(self.output_file != None):
						self.write_to_file(f"Proton email does not exist: {emails[count]}\n")
					print(f"{Fore.RED}[-] Proton email does not exist: {Style.RESET_ALL}{emails[count]}")

					#Check if domain is linked to protonmail
					if(self.check_domain(emails[count])):
						domain = emails[count].split("@")[1]
						if(self.output_file != None):
							self.write_to_file(f"Valid business domain: {domain}, catch-all is not configured\n")
						print(f"{Fore.GREEN}[+] Valid business domain: {Style.RESET_ALL}{domain}, {Fore.RED}catch-all is not configured{Style.RESET_ALL}")
						count = count + 1
						continue
				else:
					try:
						fingerprint, key_type, creation_date = self.extract_pgp_key_information(emails[count])
						display = self.format_pgp_key_information(fingerprint, key_type, creation_date)
					except TypeError:
						display = "Can't retrieve PGP keys. API limitation reached"
						creation_date = ""

					if(creation_date == None and not self.check_domain(emails[count])):
						if(self.output_file != None):
							self.write_to_file(f"Not a protonmail address, can't determine validity: {emails[count]}\n")
						print(f"{Fore.YELLOW}[?] Not a protonmail address, can't determine validity: {Style.RESET_ALL}{emails[count]}")
						count = count + 1
						continue
					else:
						#Check if business domain
						if(self.check_domain(emails[count])):
							domain = emails[count].split("@")[1]
							if(self.output_file != None):
								self.write_to_file(f"Valid business domain: {domain}\n")
							print(f"{Fore.GREEN}[+] Valid business domain: {Style.RESET_ALL}{domain}")

							print(f"{Fore.YELLOW}[?] Checking catch-all setup...{Style.RESET_ALL}")

							result_email = self.get_catch_all_address(emails[count])

							#If catch-all functionality is enabled
							if(result_email != None):
								#If email is already a source address of catch-all configuration
								if(result_email == True):
									pgp_key = self.get_pgp_public_key(emails[count])
									if(self.output_file != None):
										self.write_to_file(f"Valid email: {emails[count]} - {display}\n")
										self.write_to_file(f"{pgp_key}\n")
									print(f"{Fore.GREEN}[+] Valid email: {Style.RESET_ALL}{emails[count]} - {display}{Style.RESET_ALL}")
									print(pgp_key, end='')
								else:
									pgp_key = self.get_pgp_public_key(emails[count])
									if(self.output_file != None):
										self.write_to_file(f"Catch-all configured. Here is the source address: {result_email} - {display}\n")
										self.write_to_file(f"{pgp_key}\n")
									print(f"{Fore.GREEN}[+] Catch-all configured. Here is the source address: {Style.RESET_ALL}{result_email} - {display}{Style.RESET_ALL}")
									print(pgp_key, end='')
							else:
								pgp_key = self.get_pgp_public_key(emails[count])
								if(self.output_file != None):
									self.write_to_file(f"Valid email: {emails[count]} - {display}\n")
									self.write_to_file(f"{pgp_key}\n")
								print(f"{Fore.GREEN}[+] Valid email: {Style.RESET_ALL}{emails[count]} - {display}{Style.RESET_ALL}")
								print(pgp_key, end='')
							count = count + 1
							continue

						pgp_key = self.get_pgp_public_key(emails[count])

						#Basic protonmail accounts
						if(self.output_file != None):
							
							self.write_to_file(f"Valid email: {emails[count]} - {display}\n")
							self.write_to_file(f"{pgp_key}\n")
						print(f"{Fore.GREEN}[+] Valid email: {Style.RESET_ALL}{emails[count]} - {display}{Style.RESET_ALL}")
						print(pgp_key, end='')

				count = count + 1
		except UnexpectedAlertPresentException:
			print(f"{Fore.RED}[-] Unable to check emails addreses...{Style.RESET_ALL}")
			exit()
		except IndexError:
			pass

	def close(self):
		self.driver.close()

	def get_catch_all_address(self, email):
		url = "https://mail-api.proton.me/pks/lookup?op=index&search="
		catch_all_trigger = "lxitpwo308p3dacnsjsq"
		domain = email.split("@")[1]
		built_url = f"{url}{catch_all_trigger}@{domain}"

		response = requests.get(built_url)

		if(response.status_code == 2028):
			print(f"{Fore.RED}[-] Too many requests. Try with a proxy/VPN or wait some time...{Style.RESET_ALL}")
			exit()

		if(catch_all_trigger in response.text):
			return None
		else:
			source_email = response.text.split("uid:")[1].split(" ")[0]
			if(source_email == email):
				return True
			else:
				return source_email

	def generate_auth_cookie(self):
		url_session = "https://account.proton.me/api/auth/v4/sessions"
		url_cookies = "https://account.proton.me/api/core/v4/auth/cookies"

		data_session = {
			"x-pm-appversion":"web-account@5.0.153.3",
			"x-pm-locale":"en_US",
			"x-enforce-unauthsession":"true"
		}

		response = requests.post(url_session, headers=data_session)

		json_dump = json.loads(response.text)
		access_token = json_dump['AccessToken']
		refresh_token = json_dump['RefreshToken']
		uid = json_dump['UID']

		data_cookie = {
			"x-pm-appversion":"web-account@5.0.153.3",
			"x-pm-locale":"en_US",
			"x-pm-uid":uid,
			"Authorization":f"Bearer {access_token}"
		}

		request_data = {
			"GrantType": "refresh_token",
			"Persistent": 0,
			"RedirectURI": "https://protonmail.com",
			"RefreshToken": refresh_token,
			"ResponseType": "token",
			"State": "C72g4sTNltu4TAL5bUQlnvUT",
			"UID": uid
		}

		response = requests.post(url_cookies, headers=data_cookie, json=request_data)

		for cookie in response.cookies:
			if("AUTH" in str(cookie)):
				auth_cookie = str(cookie).split(" ")[1]
				break

		return uid,auth_cookie

	def request_api(self):
		for email in self.emails:
			#First check if syntax is correct
			if(not self.is_syntax_correct(email)):
				if(self.output_file != None):
					self.write_to_file(f"Invalid format: {email}\n")
				print(f"{Fore.RED}[-] Invalid format: {Style.RESET_ALL}{email}")
				continue

			try:
				uid, auth_cookie = self.generate_auth_cookie()
				request = requests.get("https://account.proton.me/api/core/v4/users/available", 
					headers={
						"x-pm-appversion":"web-account@5.0.153.3",
						"x-pm-locale":"en_US",
						"x-pm-uid":uid,
						"Cookie":auth_cookie
					},
					params={
						"Name":email,
						"ParseDomain":"1"
					},

					proxies=self.proxy)

				#Detected as valid but no suggestion means it doesn't exist
				if('"Suggestions":[]' in request.text):
					if(self.output_file != None):
						self.write_to_file(f"Proton email does not exist: {email}\n")
					print(f"{Fore.RED}[-] Proton email does not exist: {Style.RESET_ALL}{email}")

				elif(request.status_code == 409):
					pgp_key = self.get_pgp_public_key(email)
					try:
						fingerprint, key_type, creation_date = self.extract_pgp_key_information(email)
						display = self.format_pgp_key_information(fingerprint, key_type, creation_date)
					except TypeError:
						display = "Can't retrieve PGP keys. API limit reached"

					if(self.output_file != None):
						self.write_to_file(f"Valid email: {email} - {display}\n")
						self.write_to_file(f"{pgp_key}\n")

					print(f"{Fore.GREEN}[+] Valid email: {Style.RESET_ALL}{email} - {display}{Style.RESET_ALL}")
					print(pgp_key)

				#Return code 429 = API limit exceeded
				elif(request.status_code == 429):
					print(f"{Fore.RED}[-] API requests limit exceeded... Try again with the credentials mode (--username and --password) or use a proxy (--proxy){Style.RESET_ALL}")
				else:
					if(self.check_domain(email)):
						result_email = self.get_catch_all_address(email)
						if(result_email != None):
							try:
								fingerprint, key_type, creation_date = self.extract_pgp_key_information(email)
								display = self.format_pgp_key_information(fingerprint, key_type, creation_date)
							except TypeError:
								display = "Can't retrieve PGP keys. API limit reached"

							if(result_email == True):
								pgp_key = self.get_pgp_public_key(email)
								if(self.output_file != None):
									self.write_to_file(f"Valid email (custom domain): {email} - {display}\n")
									self.write_to_file(f"{pgp_key}\n")
								print(f"{Fore.GREEN}[+] Valid email (custom domain): {Style.RESET_ALL}{email} - {display}{Style.RESET_ALL}")
								print(pgp_key)
							else:
								pgp_key = self.get_pgp_public_key(email)
								if(self.output_file != None):
									self.write_to_file(f"Business protonmail domain. Catch-all configured. Here is the source address: {result_email} - {display}\n")
									self.write_to_file(f"{pgp_key}\n")
								print(f"{Fore.GREEN}[+] Business protonmail domain. Catch-all configured. Here is the source address: {Style.RESET_ALL}{result_email} - {display}{Style.RESET_ALL}")
								print(pgp_key)
						else:
							pgp_key = self.get_pgp_public_key(email)
							if(self.output_file != None):
								self.write_to_file(f"Valid proton domain (business), can't check validity of email: {email}\n")
								self.write_to_file(f"{pgp_key}\n")
							print(f"{Fore.GREEN}[+] Valid proton domain (business), can't check validity of email: {Style.RESET_ALL}{email}")
							print(pgp_key)
						
						continue

					pgp_key = self.get_pgp_public_key(email)

					if(self.output_file != None):
						self.write_to_file(f"Proton email does not exist: {email}\n")
						self.write_to_file(f"{pgp_key}\n")
					print(f"{Fore.RED}[-] Proton email does not exist: {Style.RESET_ALL}{email}")
					print(pgp_key)

			except:
				print(f"{Fore.RED}[-] Error when requesting the API{Style.RESET_ALL}")
				exit()

	def run(self):
		try:
			self.banner()

			#Check if we are running in light mode
			if(self.light):
				self.request_api()
				print(f"\nFor business emails, please use the selenium mode to check the validity (-u/-p).")				
			else:
				self.setup()
				self.login()
				self.new_email()
				self.close()
		except KeyboardInterrupt:
			print(f"{Fore.YELLOW}[?] Exiting...{Style.RESET_ALL}\n")
			return
