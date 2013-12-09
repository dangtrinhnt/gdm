#! /usr/bin/python

from gapis import *
import socket
if socket.gethostname() in ['trinh-pc',]: # add your hostname here
	from settings_local import *
else:
	from settings import *
import sys
from commons import *
from dateutil import parser



# 1. get a list of duplate file name = filenamelist
# 2. loop through filenamelist, for each name, get all files
# have that name. 
# 3. If the result has more than one file, process rename

# dup_files_dict = {'timestamp1': file1, 'timestamp2': file2,}
def rename_dup_files_by_modified_date(service, dup_files_dict):
	order = dup_files_dict.keys()
	order.sort(reverse=True) # keys list in sorted order, DESC
	for i in order:
		if order.index(i) > 0:
			new_title = dup_files_dict[i]['title'] + " (" \
								+ str(order.index(i)) + ")"
			rename_file(service, dup_files_dict[i]['id'], new_title)

# rename duplicate files of a single user
def rename_all_dup_files(service):
	files = retrieve_own_files(service)
	filename_list = get_unique_file_name_list(files)
	for fn in filename_list:
		dup_files_dict = {}
		for file in files:
			if file['mimeType'] == fn['mimeType']:
				if file['parents'][0]['id'] == fn['parentid']:
					if file['title'] == fn['title']:
						dt = parser.parse(file['modifiedDate'])
						dup_files_dict[dt] = file
		if len(dup_files_dict) > 1:
			rename_dup_files_by_modified_date(service, dup_files_dict)



# rename duplicate files of all users from a list
def rename_all_users_dup_files(src_csv, condition_number):
	email_list = get_dict_data_from_csv_file(src_csv)
	for email in email_list:
		num = str_to_num(email['username']) % 10
		if num in condition_number:
			print "Processing %s" % (email['email'])
			service = create_drive_service(SERVICE_ACCOUNT_PKCS12_FILE,\
							SERVICE_ACCOUNT_EMAIL, OAUTH_SCOPE, email['email'])
			if service:
				rename_all_dup_files(service)
			print "Finish renaming duplicate files of user %s" % (email['email'])



if __name__ == "__main__":
	src_csv = sys.argv[1]
	condition_number = map(int, sys.argv[2].split(','))
	rename_all_users_dup_files(src_csv, condition_number)
