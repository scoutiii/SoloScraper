import csv
import sys
import re
from datetime import datetime
from tqdm import tqdm




# Class which has all characteristics of a message
class message_info:
	def __init__(self, message, customer_id):
		self.msg_full = re.sub('[^a-zA-Z0-9 \`\~\!\@\#\$\%\^\&\*\(\)\_\+\-\=\[\{\]\}\\\|\;\:\'\"\,\<\.\>\/\?\\n]*', "", message)
		self.cid = customer_id
		reg_res = re.match("([a-zA-Z0-9 -]*) \(([a-zA-Z0-9 ]*)\) - ([a-zA-Z0-9/ :]*)\\n([a-zA-Z0-9 \`\~\!\@\#\$\%\^\&\*\(\)\_\+\-\=\[\{\]\}\\\|\;\:\'\"\,\<\.\>\/\?\\n]*)", self.msg_full)
		if reg_res is not None:
			self.name = reg_res.group(1)
			self.title = reg_res.group(2)
			self.date = datetime.strptime(reg_res.group(3), "%m/%d/%Y %H:%M")
			self.msg = reg_res.group(4)
			self.type = "Other"
			self.sub_type = "Other"
		else:
			self.name = "NA"
			self.title = "NA"
			self.date = "NA"
			self.msg = "NA"
			self.type = "NA"
			self.sub_type = "NA"


# Class which classifies messages, and determins timings
class message_timings:
	def __init__(self, messages, customer_id):
		self.messages = []
		for msg in messages:
			self.messages.append(message_info(msg, customer_id))


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
		entry = {"ID":msg_info.cid, "NAME":msg_info.name, "TITLE":msg_info.title,
				 "DATE":msg_info.date, "MSG":msg_info.msg}
		messages_info.append(entry)
	return(messages_info)



# run functions goes through customers and creates a csv with time worked info
def run(driver, file_in, file_out, is_sub):

	if is_sub:
		print("sub routine")
		return

	


	print("\nStarting work_time routine\n")
	sys.stdout.flush()
	driver.minimize_window()

	# opens files and csv files
	f_in = open(file_in, "r", encoding="utf8")
	f_ut = open(file_out, "w")
	csv_in = csv.DictReader(f_in)
	csv_ut = csv.DictWriter(f_ut, ["ID","NAME", "TITLE", "DATE", "MSG"])
	csv_ut.writeheader()

	# Gets all ids first, so that we can have a progress bar
	customer_ids = set()
	for line in csv_in:
		customer_ids.add(line["customer_id"])

	# loops through all customer ids, and writes the csv entries
	for customer_id in tqdm(customer_ids):
		entries = create_entries(driver, customer_id)
		csv_ut.writerows(entries)

	f_in.close()
	f_ut.close()
	print("\nRoutine Complete\n")
