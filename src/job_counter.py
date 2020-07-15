import csv
import sys
import re
from datetime import datetime
from tqdm import tqdm


# Class which has all characteristics of a message
class MessageInfo:
    def __init__(self, message):
        self.msg_full = re.sub('[^a-zA-Z0-9 \`\~\!\@\#\$\%\^\&\*\(\)\_\+\-\=\[\{\]\}\\\|\;\:\'\"\,\<\.\>\/\?\\n]*',
                               "", message)
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


# Class which classifies messages, and determines timings
class CountMessages:
    # Lists of notable titles
    props_titles = ["proposalist", "junior proposalist", "senior proposalist"]
    QA_titles = ["proposal qa", "super admin"]

    # Takes a message and its prior to determine what type it is
    @staticmethod
    def classify_message(previous, msg):
        # Finds time type
        if msg.msg.find("URGENT CHECKED") != -1:
            msg.time = "Real"
        elif previous.time == "NA" or previous.sub_type == "Archive" or previous.sub_type == "Sent":
            msg.time = "Standard"
        else:
            msg.time = previous.time

        # Checks for easy to catch note types

        # END NOTES:
        # TYPE: end, archive
        if msg.msg.find("Customer Archived") != -1:
            msg.type = "End"
            msg.sub_type = "Archive"
            return
        # TYPE: end, QA
        if msg.msg.find("Proposal(s) Completed and needs QA") != -1:
            msg.type = "End"
            msg.sub_type = "QA"
            return
        # TYPE: end, sent
        if msg.msg.find("New Solar Proposal") != -1:
            msg.type = "End"
            msg.sub_type = "Sent"
            return

        # REJECTION NOTES:
        # TYPE: rejection, rejection
        if msg.msg.find("Proposal Rejected for") != -1:
            msg.type = "Rejection"
            msg.sub_type = "Rejected"
            return

        # RESPONSE NOTES:
        # TYPE: response, prop Response
        if msg.title in CountMessages.props_titles:
            msg.type = "Response"
            msg.sub_type = "Prop Response"
            return
        # TYPE: response, QA Response
        if msg.title in CountMessages.QA_titles:
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

    # Goes through the series of classified messages, and determines if there are any jobs sent or rejected
    def get_entries(self):
        entries = []
        i = 0
        while i < len(self.messages):
            message = self.messages[i]
            if message.type == "Rejection" and message.sub_type == "Rejected":
                entries.append(self.__create_entry__(message))
            elif message.type == "End" and message.sub_type == "Sent":
                entries.append(self.__create_entry__(message))
            i += 1

        return entries

    # Takes a message and creates an entry
    def __create_entry__(self, message):
        time = message.time
        name = message.name
        title = message.title
        id_url = 'https://phx.gosolo.io/customer/' + str(self.customer_id)
        date = message.date
        type_ = message.sub_type
        entry = {"Name": name, "Title": title, "Type": type_,
                 "Time_Type": time, "Date_Time": date, "Customer_Id": id_url}
        return entry

    # Takes a list series of messages and classifies them
    def __init__(self, messages, customer_id):
        self.messages = []
        self.customer_id = customer_id
        for msg in messages:
            self.messages.append(MessageInfo(msg))
        for i in range(len(self.messages)):
            if i == 0:
                prev = MessageInfo("")
            else:
                prev = self.messages[i - 1]
            self.classify_message(prev, self.messages[i])


# Takes a customer id and returns a list of every message
def get_messages(driver, customer_id):
    driver.get('https://phx.gosolo.io/customer/' + str(customer_id))
    msg_elements = driver.find_elements_by_xpath('//*[@id="sideNotes"]/div')
    messages = []
    for msg in msg_elements:
        messages.append(msg.text)
    return messages


# Is called first, will return a list of entries to put into the csv
def create_entries(driver, customer_id):
    # Gets notes section for the customer
    messages = get_messages(driver, customer_id)
    # Processes messages to get timings
    counts = CountMessages(messages, customer_id)
    entries = counts.get_entries()
    return entries


# run functions goes through customers and creates a csv with time worked info
def run(driver, file_in, file_out):
    print("\nStarting job counting routine\n")
    sys.stdout.flush()
    driver.minimize_window()

    # opens files and csv files
    f_in = open(file_in, "r", encoding="utf8")
    f_ut = open(file_out, "w")
    csv_in = csv.DictReader(f_in)
    csv_ut = csv.DictWriter(f_ut, ["Name", "Title", "Type", "Time_Type", "Date_Time", "Customer_Id"])
    csv_ut.writeheader()

    # Gets all ids first, so that we can have a progress bar
    customer_ids = set()
    for line in csv_in:
        customer_ids.add(line["customer_id"])

    # loops through all customer ids, and writes the csv entries
    customer_ids = list(customer_ids)
    customer_ids.sort()
    for customer_id in tqdm(customer_ids):
        entries = create_entries(driver, customer_id)
        csv_ut.writerows(entries)

    f_in.close()
    f_ut.close()
    print("\nRoutine Complete\n")
