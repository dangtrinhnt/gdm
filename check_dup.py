#! /usr/bin/python

from gdm import *
import socket
if socket.gethostname() in ['trinh-pc',]: # add your hostname here
	from settings_local import *
else:
	from settings import *

import sys


def str_to_num(input_str):
	return_num = 0
	for ch in input_str:
		return_num += ord(ch)

	return return_num



def has_dup_file(files):
	tmp = []
	for i in range(len(files)):
		if files[i]['parents']:
			file = {}
			file['mimeType'] = files[i]['mimeType']
			file['parentid'] = files[i]['parents'][0]['id']
			file['title'] = files[i]['title']
			if file in tmp:
				return True
			else:
				tmp.append(file)

	return False


def export_user_has_dup_file(src_csv, dest_csv, condition_number):
	email_list = get_dict_data_from_csv_file(src_csv)
	has_dup_file_users = []
	for email in email_list:
		num = str_to_num(email['username']) % 10
		if num in condition_number:
			print "Processing %s" % (email['email'])
			service = create_drive_service(SERVICE_ACCOUNT_PKCS12_FILE,\
							SERVICE_ACCOUNT_EMAIL, OAUTH_SCOPE, email['email'])
			allfiles = retrieve_all(service)
			# allfiles = remove_no_parent_file(allfiles)
			if allfiles:
				if has_dup_file(allfiles):
					has_dup_file_users.append(email)

	if has_dup_file_users:
		write_dict_data_to_csv_file(dest_csv, has_dup_file_users)
	else:
		print "No user has duplicate files"


if __name__ == '__main__':
	src_csv = sys.argv[1]
	dest_csv = sys.argv[2]
	condition_number = map(int, sys.argv[3].split(','))

	print condition_number
	export_user_has_dup_file(src_csv, dest_csv, condition_number)
