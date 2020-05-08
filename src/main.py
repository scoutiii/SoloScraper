import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Logs into the phx website
def login(driver, user_name, password):
	print("\n")
	print("Attempting Login...")
	try:
		driver.find_element_by_id("email").send_keys(user_name)
		driver.find_element_by_id("password").send_keys(password)
		driver.find_element_by_name("btn-submit").click()
	except:
		print("Login failed\n")
	print("Login successful")
	print("\n")

# Sets up the driver
def init_driver(driver_path, url, wait):
	print("\nInitializing driver\n")
	driver = webdriver.Chrome(driver_path)
	driver.implicitly_wait(wait)
	driver.get(url)
	return(driver)


# The main function which starts the scraper
def main():
	# If there is not an even number of args (excluding first arg), it terminates
	if (len(sys.argv)-1) % 2 == 1:
		print("Wrong number of arguments.")
		return

	# Sets defaults based on Scout Jarman's computer
	driver_path = "D:\downloads\solo\WebScraper\SoloScraper\src\drivers\chromedriver.exe"
	user_name = "scout@gosolo.io"
	password = "W8fa7p5m"
	url = "https://phx.gosolo.io/login"
	wait = 10

	# Goes through and sets given arguments
	for i in range(1,len(sys.argv),2):
		if i >= len(sys.argv):
			break
		option = sys.argv[i]
		argument = sys.argv[i+1]
		# changes the path for the chrome driver
		if option == "-d":
			driver_path = argument
		# sets the user name for login
		elif option == "-u":
			user_name = argument
		# sets the password for login
		elif option == "-p":
			password = argument
		# changes the starting url
		elif option == "-s":
			url = argument
		# Time in seconds for implicit waiting for driver
		elif option == "-w":
			wait = argument


	# print("Driver:    " + driver_path)
	# print("User Name: " + user_name)
	# print("Password:  " + password)

	# initializes the scraper
	driver = init_driver(driver_path, url, wait)
	login(driver, user_name, password)

	input("Click Anything to End")

if __name__ == "__main__":
	main()
