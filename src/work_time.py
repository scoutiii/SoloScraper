import csv


def run(driver, file_in, file_out):
	print("\nStarting work_time routine\n")

	f_in = open(file_in, "r")
	f_ut = open(file_out, "w")

	csv_in = csv.DictReader(f_in)
	csv_ut = csv.
	for line in csv_in:
		print(line["customer_id"] + line["proposal_id"])
