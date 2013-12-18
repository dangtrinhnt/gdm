#! /usr/bin/python

from gapis import *
import socket
if socket.gethostname() in ['trinh-pc',]: # add your hostname here
	from settings_local import *
else:
	from settings import *
import sys
from commons import *
#~ from dateutil import parser



# 1. get a list of duplate file name = filenamelist
# 2. loop through filenamelist, for each name, get all files
# have that name. 
# 3. If the result has more than one file, process rename


# rename duplicate files of all users from a list
# email_list = [{'usename': 'abc', 'email': 'abc@mydomain.com'}, {},...]
def rename_all_users_dup_files(src_csv, condition_number):
	email_list = get_dict_data_from_csv_file(src_csv)
	for email in email_list:
		num = str_to_num(email['email']) % 10
		if num in condition_number or condition_number[0]==-1:
			print "Processing %s" % (email['email'])
			service = create_drive_service(SERVICE_ACCOUNT_PRIVATE_KEY,\
							SERVICE_ACCOUNT, OAUTH_SCOPE, email['email'])
			if service:
				rename_all_dup_files(service)
			print "Finish renaming duplicate files of user %s" % (email['email'])



if __name__ == "__main__":
	src_csv = sys.argv[1]
	if sys.argv[2] == 'all':
		condition_number = [-1]
	else:
		condition_number = map(int, sys.argv[2].split(','))
	rename_all_users_dup_files(src_csv, condition_number)
