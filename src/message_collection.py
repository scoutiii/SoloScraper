import os
import csv

def count_job(driver, id):
	url = "https://phx.gosolo.io/proposal-admin/" + id
	driver.get(url)
	# Closes best practices
	#bp_close = driver.find_elements_by_xpath('//*[@id="body"]/div[4]/div[3]/div/div[3]/button')
	#if len(bp_close) > 0:
	#	bp_close[0].click()

	# Loops through each message
	messages = driver.find_elements_by_xpath('//*[@id="sideNotes"]/div')
	all_msg = ""
	for msg in messages:
		all_msg += msg.text
	all_msg = all_msg.split("\n")
	all_msg = " <<>> ".join(all_msg)
	all_msg = all_msg.replace(",", "!COMMA!")

	entry = id + "," + str(len(messages)) + "," + all_msg
	return entry

def run(driver, file_in, file_out):
	print("\nStarting message routine...\n")
	if file_in is None:
		file_in = input("Need an input file (path or name): ")
	f_in = open(file_in, "r")
	f_ut = open(file_out, "w")
	# Defines headers for file
	f_ut.write("ID,NUM_MSG,MSG")
	# Loops through each line of the input file
	for line in f_in:
		res = count_job(driver, line.strip())
		f_ut.write(res)
	f_in.close()
	f_ut.close()
