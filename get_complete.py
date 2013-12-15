#! /usr/bin/python
import csv
import sys


def get_log_lines(log_path):
	log_file = open(log_path, 'rb')
	log = log_file.read()
	log_file.close()
	log = log.split('\n')
	if '' in log:
		log.remove('')
	return log

def get_completed_user_list_from_log(log_path):
	log_lines = get_log_lines(log_path)
	completed_users = []
	for line in log_lines:
		if 'Finish migrating user' in line:
			tmp = line.split(' ')
			for txt in tmp:
				if '@' in txt:
					completed_users.append(txt)
	return completed_users

def list_to_csv(list_data, csv_path):
	csv_file = open(csv_path, 'wb')

	writer = csv.writer(csv_file, dialect='excel')

	for data in list_data:
		writer.writerow([data])

	csv_file.close()


def export_completed_users_to_csv(log_path, csv_path):
	completed_users = get_completed_user_list_from_log(log_path)
	list_to_csv(completed_users, csv_path)



if __name__ == "__main__":
	log_path = sys.argv[1]
	csv_path = sys.argv[2]

	export_completed_users_to_csv(log_path, csv_path)
