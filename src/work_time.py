import csv
import sys
import re
from datetime import datetime
from tqdm import tqdm




# Class which has all characteristics of a message
class message_info:
	def __init__(self, message):
		self.msg_full = re.sub('[^a-zA-Z0-9 \`\~\!\@\#\$\%\^\&\*\(\)\_\+\-\=\[\{\]\}\\\|\;\:\'\"\,\<\.\>\/\?\\n]*', "", message)
		reg_res = re.match("(.*) \((.*)\) - (.*)\\n(.*)", self.msg_full)
		if reg_res is not None:
			self.name = reg_res.group(1)
			self.title = reg_res.group(2).lower()
			self.date = datetime.strptime(reg_res.group(3), "%m/%d/%Y %H:%M")
			self.msg = reg_res.group(4)
			self.type = "Other"
			self.sub_type = "Other"
			self.time = "Non"
		else:
			self.name = "NA"
			self.title = "NA"
			self.date = "NA"
			self.msg = "NA"
			self.type = "NA"
			self.sub_type = "NA"
			self.time = "NA"


# Class which classifies messages, and determins timings
class message_timings:
	# Lists of notable titles
	props_titles = ["proposalist", "junior proposalist", "senior proposalist"]
	QA_titles = ["proposal qa", "super admin"]

	# Takes a message and its prior to determine what type it is
	def classify_message(self, previous, msg):
		# Finds time type
		if msg.msg.find("URGENT CHECKED") != -1:
			msg.time = "Real"
		elif previous.time == "NA":
			msg.time = "Standard"
		else:
			msg.time = previous.time

		# Checks for easy to catch note types

		# END NOTES:
		# TYPE: end, archive
		if msg.msg.find("Customer Archived") != -1:
			msg.type = "End"
			msg.sub_type = "Archive"
			msg.time = "Standard"
			return
		# TYPE: end, QA
		if msg.msg.find("Proposal(s) Completed and needs QA") != -1:
			msg.type = "End"
			msg.sub_type = "Archive"
			msg.time = "Standard"
			return
		# TYPE: end, sent
		if msg.msg.find("New Proposal") != -1:
			msg.type = "End"
			msg.sub_type = "Sent"
			msg.time = "Standard"
			return

		# REJECTION NOTES:
		# TYPE: rejection, rejection
		if msg.msg.find("Proposal Rejected for") != -1:
			msg.type = "Rejection"
			msg.sub_type = "Rejected"
			return

		# RESPONSE NOTES:
		# TYPE: response, prop Response
		if msg.title in message_timings.props_titles:
			msg.type = "Response"
			msg.sub_type = "Prop Response"
			return
		# TYPE: response, QA Response
		if msg.title in message_timings.QA_titles:
			msg.type = "Response"
			msg.sub_type = "QA Response"
			return

		# REQUEST NOTES:
		# TYPE: request, create
		if msg.msg.find("New customer created successfully") != -1:
			msg.type = "Request"
			msg.sub_type = "Create"
			return
		# TYPE (DEFAULT): request, other
		msg.type = "Request"
		msg.sub_type = "Other"
		return

	# Goes through the series of classified messages, and determines if there are any work time events
	def get_entries(self):
		entries = []
		start = None
		end = None
		target = None

		i = 0
		while i < len(self.messages):
			msg = self.messages[i]
			if start is None:
				if msg.type == "Request":
					start = msg
					target = "Response"
				elif msg.type == "Response":
					start = msg
					target = "End"
				elif msg.type == "Rejection":
					start = msg
					tartget = "End"
			else:
				if msg.type == target:
					end = msg
					entries.append(self.__create_entry__(start, end))
					if start.type == "Response":
						start = end = target = None
						continue
					start = end = target = None
			i += 1

		return(entries)


	# Takes a start and end and creates a work time event
	def __create_entry__(self, start, end):
		if start.type == "Request" and end.type == "Response":
			type = "Queue Time"
		elif start.type == "Response" and end.type == "End":
			type = "Prop Work Time"
		elif start.type == "Rejection" and end.type == "End":
			type = "Rejection Work Time"
		else:
			type = "Other"

		diff = end.date - start.date
		work_time = divmod(diff.total_seconds(), 60)[0]
		time = start.time
		name = end.name
		title = end.title
		id = self.customer_id
		date = end.date.date()
		entry = {"Type":type, "Name":name, "Title":title, "Work_Time":work_time,
				 "Time_Type":time, "Date":date, "Customer_Id":id}
		return(entry)


	# Takes a list series of messages and classifies them
	def __init__(self, messages, customer_id):
		self.messages = []
		self.customer_id = customer_id
		for msg in messages:
			self.messages.append(message_info(msg))
		for i in range(len(self.messages)):
			if i == 0:
				prev = message_info("")
			else:
				prev = self.messages[i-1]
			self.classify_message(prev, self.messages[i])


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
	# Gets notes section for the cutomer
	messages = get_messages(driver, customer_id)
	# Processes messages to get timings
	timings = message_timings(messages, customer_id)
	entries = timings.get_entries()
	return(entries)



# run functions goes through customers and creates a csv with time worked info
def run(driver, file_in, file_out):
	print("\nStarting work_time routine\n")
	sys.stdout.flush()
	driver.minimize_window()

	# opens files and csv files
	f_in = open(file_in, "r", encoding="utf8")
	f_ut = open(file_out, "w")
	csv_in = csv.DictReader(f_in)
	csv_ut = csv.DictWriter(f_ut, ["Type", "Name", "Title", "Work_Time", "Time_Type", "Date", "Customer_Id"])
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
