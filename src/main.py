import sys
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import message_collection
import work_time
import job_counter


# Logs into the phx website
def login(driver, user_name, password, wait):
    print("\n")
    # Gets username and password if needed
    if user_name is None:
        user_name = input("Enter Username: ")
    if password is None:
        password = input("Enter Password: ")

    print("Attempting Login...")
    try:
        driver.find_element_by_id("email").send_keys(user_name)
        driver.find_element_by_id("password").send_keys(password)
        driver.find_element_by_name("btn-submit").click()
        # Checks to see if webpage changes indicating successful login
        WebDriverWait(driver, wait).until(lambda driver: driver.current_url == "https://phx.gosolo.io/")
    except:
        print("Login failed\n")
        return False
    print("Login successful")
    print("\n")
    sys.stdout.flush()
    return True


# Sets up the driver
def init_driver(driver_path, url, wait):
    try:
        print("\nInitializing driver\n")
        driver = webdriver.Chrome(driver_path)
        # print("webdriver")
        driver.implicitly_wait(wait)
        # print("wait")
        driver.set_page_load_timeout(wait)
        # print("timeout")
        driver.get(url)
        # print("url")
        driver.maximize_window()
        # print("maximize")
    except:
        print("Something failed while initializing the driver!")
        print(sys.exc_info())
        print("\n")
        return False
    print("\n")
    sys.stdout.flush()
    return driver


# Prints help menu with commands
def help():
    print("\nCommand options:\n")
    print("-h or --help :")
    print("\tPrints this help message")
    print("-d :")
    print("\tThe path to a chrome driver, default is Scout's driver path")
    print("-u :")
    print("\tUsername to log into solo, if not given you will be asked to later")
    print("-p :")
    print("\tPassword to log into solo, if not given you will be asked for it later")
    print("-s :")
    print("\tThe url where the driver will start, defaults to the phx login page")
    print("-w :")
    print("\tThe implicit wait time and page wait time for driver, default is 10 seconds")
    print("-i :")
    print("\tThe path to the file for input, if one is not defined you will be asked for one")
    print("-o :")
    print("\tThe path or name for the output file, default is to 'out_put.txt'")
    print("-v :")
    print("\tSpecify the random seed, default is 42069")
    print("-r :")
    print("\tThe routine you want to run (defaults to work_time, current options are:")
    print("\t\tmessage : takes a list of jobs to look at, and collects info on the messages")
    print("\t\twork_time : takes a list of customer ids, and determines work times")
    print("\t\tcount : takes a list of customer ids and counts the number of new proposals and rejections")
    print("\n")
    sys.stdout.flush()


# The main function which starts the scraper
def main():
    # Checks for help command
    if len(sys.argv) >= 2:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            help()
            return
    # If there is not an even number of args (excluding first arg), it terminates
    if (len(sys.argv) - 1) % 2 == 1:
        print("Wrong number of arguments.")
        return

    # Sets defaults based on Scout Jarman's computer
    driver_path = "D:\downloads\solo\SoloScraper\src\drivers\chromedriver83.exe"
    user_name = None
    password = None
    url = "https://phx.gosolo.io/login"
    wait = 10
    file_in = None
    file_out = "out_put.txt"
    routine = "work_time"
    seed = 42069

    # Goes through and sets given arguments
    for i in range(1, len(sys.argv), 2):
        if i >= len(sys.argv):
            break
        option = sys.argv[i]
        argument = sys.argv[i + 1]
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
        # sets the file for input
        elif option == "-i":
            file_in = argument
        # sets the output file
        elif option == "-o":
            file_out = argument
        # specifies the routine
        elif option == "-r":
            routine = argument
        # Sets the seed
        elif option == "-v":
            seed = argument

    print("Driver Path : " + str(driver_path))
    print("       Wait : " + str(wait))
    print("        Url : " + str(url))
    print("    File In : " + str(file_in))
    print("   File Out : " + str(file_out))
    print("  User Name : " + str(user_name))
    print("   Password : " + str(password))
    print("    Routine : " + str(routine))
    print("       Seed : " + str(seed))
    sys.stdout.flush()

    # initializes the scraper
    random.seed(seed)
    driver = init_driver(driver_path, url, wait)
    if driver is False:
        return
    if login(driver, user_name, password, wait) is False:
        return
    sys.stdout.flush()
    if routine == "message":
        message_collection.run(driver, file_in, file_out)
    elif routine == "work_time":
        work_time.run(driver, file_in, file_out)
    elif routine == "count":
        job_counter.run(driver, file_in, file_out)

    print("\nEnd program\n")
    driver.close()


# classic way to use a main function for python
if __name__ == "__main__":
    main()
