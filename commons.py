#! /usr/bin/python
import csv
from datetime import datetime
# http://labix.org/python-dateutil
from dateutil import parser


# utilities
def get_dict_data_from_csv_file(csv_file_path):
	csv_file = open(csv_file_path, 'rb')
	csv_file.seek(0)
	sniffdialect = csv.Sniffer().sniff(csv_file.read(10000), delimiters='\t,;')
	csv_file.seek(0)
	dict_reader = csv.DictReader(csv_file, dialect=sniffdialect)
	csv_file.seek(0)
	dict_data = []
	for record in dict_reader:
		dict_data.append(record)

	csv_file.close()

	return dict_data


def write_dict_data_to_csv_file(csv_file_path, dict_data):
	csv_file = open(csv_file_path, 'wb')
	writer = csv.writer(csv_file, dialect='excel')
	
	headers = dict_data[0].keys()
	writer.writerow(headers)

	# headers must be the same with dat.keys()
	for dat in dict_data:
		line = []
		for field in headers:
			line.append(dat[field])
		writer.writerow(line)
		
	csv_file.close()


def str_to_num(input_str):
	return_num = 0
	for ch in input_str:
		return_num += ord(ch)

	return return_num


def remove_no_parent_files(files):
	tmp = files
	for file in files:
		if not file['parents']:
			tmp.remove(file)
	return tmp


def switch_email_domain(src_email, new_domain):
	username = src_email.split('@')[0]
	return '%s@%s' % (username, new_domain)


def has_dup_file(files):
	tmp = []
	for i in range(len(files)):
		if files[i]['parents']:
			file = {}
			file['mimeType'] = files[i]['mimeType']
			file['parentid'] = files[i]['parents'][0]['id']
			file['title'] = files[i]['title']
			if file in tmp:
				print "Found duplicate file: %s" % file
				return True
			else:
				tmp.append(file)

	return False


def get_unique_file_name_list(files):
	unique_file_name = []
	for file in files:
		if file['parents']:
			file_item = {}
			file_item['mimeType'] = file['mimeType']
			file_item['parentid'] = file['parents'][0]['id']
			file_item['title'] = file['title']
			if file_item not in unique_file_name:
				unique_file_name.append(file_item)
	return unique_file_name



# check if the src_file is newer than the dest_file
def is_older(src_file, dest_file):
	src_modified_date = parser.parse(src_file['modifiedDate'])
	dest_modified_date = parser.parse(dest_file['modifiedDate'])

	if src_modified_date < dest_modified_date:
		return True

	return False


def clean_query_string(title):
	return title.replace(r"'", r"\'")