#! /usr/bin/python

from gapis import *
import socket
if socket.gethostname() in ['trinh-pc',]: # add your hostname here
	from settings_local import *
else:
	from settings import *
import sys
from commons import *





def export_user_has_dup_file(src_csv, dest_csv, condition_number):
	email_list = get_dict_data_from_csv_file(src_csv)
	has_dup_file_users = []
	for email in email_list:
		num = str_to_num(email['username']) % 10
		if num in condition_number:
			print "Processing %s" % (email['email'])
			service = create_drive_service(SERVICE_ACCOUNT_PKCS12_FILE,\
							SERVICE_ACCOUNT_EMAIL, OAUTH_SCOPE, email['email'])
			if service:
				query = "trashed = false" # not looking for files in trash
				allfiles = search_files(service, query)

				if allfiles:
					if has_dup_file(allfiles):
						print "User %s has duplicate file" % (email['email'])
						has_dup_file_users.append(email)
				print "Finish processing %s" % (email['email'])

	if has_dup_file_users:
		write_dict_data_to_csv_file(dest_csv, has_dup_file_users)
	else:
		print "No user has duplicate files"


if __name__ == '__main__':
	src_csv = sys.argv[1]
	dest_csv = sys.argv[2]
	condition_number = map(int, sys.argv[3].split(','))

	export_user_has_dup_file(src_csv, dest_csv, condition_number)
