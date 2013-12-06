#! /usr/bin/python
import csv


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