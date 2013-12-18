#! /usr/bin/python

import sys
import socket
if socket.gethostname() in ['trinh-pc',]: # add your hostname here
	from settings_local import *
else:
	from settings import *
from gapis import *
from commons import *
#~ from rename_dup import rename_all_dup_files



# email_list = [{'src': 'genius@olddomain.com', 'dest': 'genius@newdomain.com'}]
def google_drive_migrate(csv_file, condition_number):
	email_map_list =  get_dict_data_from_csv_file(csv_file)
	for email in email_map_list:
		num = str_to_num(email['src']) % 10
		if num in condition_number or condition_number[0]==-1:

			src_service = create_drive_service(SERVICE_ACCOUNT_PRIVATE_KEY,\
							SERVICE_ACCOUNT, OAUTH_SCOPE, email['src'])
			if src_service:
				print "Processing %s" % (email['src'])
				# rename duplicate files/folders before migrating
				print "Renaming duplicate files and folders of user %s" % (email['src'])
				rename_all_dup_files(src_service)
				print "Finish renaming files and folders of user %s" % (email['src'])

				dest_service = create_drive_service(SERVICE_ACCOUNT_PRIVATE_KEY,\
									SERVICE_ACCOUNT, OAUTH_SCOPE, email['dest'])
				if dest_service:

					files = get_own_files(src_service)

					if files:
						files_map = [{'src': email['src'], 'dest': email['dest'], 'files': files}]

						# Step 1. share files with new account
						print "Share permissions to destionation account %s" % email['dest']
						perms, shared_files = share_files(src_service, files_map)

						# Step 2. make a copy of shared files in new account
						print "Make a copy of shared files of user %s" % email['dest']
						new_files_map = make_a_copy(dest_service, shared_files)

						# Step 3. disable sharing on source account
						print "Disable sharing on source account %s" % email['src']
						disable_sharing(src_service, perms)

						# Step 4. copy permissions
						if new_files_map:
							print "Copy permissions of all files of %s" % email['src']
							copy_perms(src_service, dest_service, email['src'], email['dest'], new_files_map)
					else:
						print "User %s has no file" % email['dest']
				else:
					print "Canot initiate drive service of user %s. Skipped!" % (email['dest'])
			else:
				print "Skip processing user %s" % (email['src'])
			print "Finish migrating user %s" % (email['src'])

#########################################################################


if __name__ == "__main__":

	src_csv = sys.argv[1]
	if sys.argv[2] == 'all':
		condition_number = [-1]
	else:
		condition_number = map(int, sys.argv[2].split(','))

	google_drive_migrate(src_csv, condition_number)
