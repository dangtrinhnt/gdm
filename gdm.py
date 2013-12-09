#! /usr/bin/python

import sys
import socket
if socket.gethostname() in ['trinh-pc',]: # add your hostname here
	from settings_local import *
else:
	from settings import *
from gapis import *
from commons import *
from rename_dup import rename_all_dup_files



# email_list = [{'src_email': 'genius@olddomain.com', 'dest_email': 'genius@newdomain.com', 'username': 'genius'}]
def google_drive_migrate(csv_file, condition_number):
	email_map_list =  get_dict_data_from_csv_file(csv_file)
	for email_pair in email_map_list:
		num = str_to_num(email_pair['username']) % 10
		if num in condition_number:

			src_service = create_drive_service(SERVICE_ACCOUNT_PKCS12_FILE,\
							SERVICE_ACCOUNT_EMAIL, OAUTH_SCOPE, email_pair['src_email'])
			if src_service:
				print "Processing %s" % (email_pair['email'])
				# rename duplicate files/folders before migrating
				print "Renaming duplicate files and folders of user %s" % (email_pair['username'])
				rename_all_dup_files(src_service)
				print "Finish renaming files and folders of user %s" % (email_pair['username'])

				dest_service = create_drive_service(SERVICE_ACCOUNT_PKCS12_FILE,\
									SERVICE_ACCOUNT_EMAIL, OAUTH_SCOPE, email_pair['dest_email'])
				if dest_service:

					allfiles = retrieve_own_files(src_service)

					files_map = [{'src': email_pair['src_email'], 'dest': email_pair['dest_email'], 'files': allfiles}]

					# Step 1. share files with new account
					shared_perms_list = share_files_with_another(src_service, files_map)

					# Step 2. make a copy of shared files in new account
					new_files_map = make_a_copy_of_shared_files(dest_service, allfiles)

					# Step 3. disable sharing on source account
					disable_sharing(src_service, shared_perms_list)

					# Step 4. copy permissions
					copy_perms(src_service, dest_service, email_pair['src_email'], email_pair['dest_email'], new_files_map)
				else:
					print "Canot initiate drive service of user %s. Skipped!" % (email_pair['dest_email'])
			else:
				print "Skip processing user %s" % (email_pair['src_email'])
			print "Finish migrating user %s" % (email['email'])

#########################################################################


if __name__ == "__main__":

	src_csv = sys.argv[1]
	condition_number = map(int, sys.argv[2].split(','))

	google_drive_migrate(src_csv, condition_number)
