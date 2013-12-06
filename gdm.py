#! /usr/bin/python

import sys
import socket
if socket.gethostname() in ['trinh-pc',]: # add your hostname here
	from settings_local import *
else:
	from settings import *
from gapis import *
from commons import *




# email_list = [{'src_email': 'genius@olddomain.com', 'dest_email': 'genius@newdomain.com'}]
def google_drive_migrate(email_map_list):
	for email_pair in email_map_list:
		src_service = create_drive_service(SERVICE_ACCOUNT_PKCS12_FILE,\
							SERVICE_ACCOUNT_EMAIL, OAUTH_SCOPE, email_pair['src_email'])

		# search file not in trash
		allfiles = search_files(src_service, "trashed = false")

		files_map = [{'src': email_pair['src_email'], 'dest': email_pair['dest_email'], 'files': allfiles}]

		# Step 1. share files with new account
		shared_perms_list = share_files_with_another(src_service, files_map)

		# Step 2. make a copy of shared files in new account
		dest_service = create_drive_service(SERVICE_ACCOUNT_PKCS12_FILE,\
							SERVICE_ACCOUNT_EMAIL, OAUTH_SCOPE, email_pair['dest_email'])
		new_files_map = make_a_copy_of_shared_files(dest_service, allfiles)

		# Step 3. disable sharing on source account
		disable_sharing(src_service, shared_perms_list)

		# Step 4. copy permissions
		# print new_files_map
		copy_perms(src_service, dest_service, email_pair['src_email'], email_pair['dest_email'], new_files_map)


#########################################################################


if __name__ == "__main__":

	#drive_service = create_drive_service_web_2_steps(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)

	# the email_list maybe read from a csv file
	email_map_list = [{'src_email': 'genius@olddomain.com', 'dest_email': 'genius@newdomain.com'}]
	google_drive_migrate(email_map_list)
