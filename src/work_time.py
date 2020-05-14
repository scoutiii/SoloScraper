import csv
import sys
from tqdm import tqdm


# Class which has all characteristics of a message
class message_info:
	def __init__(self, message, customer_id):
		self.msg = message
		self.cid = customer_id

# Takes a customer id and returns a list of every message
def get_messages(driver, customer_id):
	driver.get('https://phx.gosolo.io/customer/' + str(customer_id))
	msg_elmt = driver.find_elements_by_xpath('//*[@id="sideNotes"]/div')
	messages = []
	for msg in msg_elmt:
		messages.append(msg.text)
	return(messages)

# Is called first, will return a list of entries to put into the csv
def create_entries(driver, customer_id):
	messages = get_messages(driver, customer_id)
	messages_info = []
	for msg in messages:
		msg_info = message_info(msg, customer_id)
		messages_info.append(msg_info)
		#print(str(len(msg_info.msg)) + " : " + str(msg_info.cid))
		#sys.stdout.flush()
	return([{"ID" : customer_id, "NUM" : len(messages_info)}])

# run functions goes through customers and creates a csv with time worked info
def run(driver, file_in, file_out):
	print("\nStarting work_time routine\n")
	sys.stdout.flush()

	# opens files and csv files
	f_in = open(file_in, "r")
	f_ut = open(file_out, "w")
	csv_in = csv.DictReader(f_in)
	csv_ut = csv.DictWriter(f_ut, ["ID","NUM"])
	csv_ut.writeheader()

	# Gets all ids first, so that we can have a progress bar
	customer_ids = []
	for line in csv_in:
		customer_ids.append(line)

	# loops through all customer ids, and writes the csv entries
	for customer_id in tqdm(customer_ids):
		entries = create_entries(driver, customer_id["customer_id"])
		csv_ut.writerows(entries)

	f_in.close()
	f_ut.close()
	print("\nRoutine Complete\n")
