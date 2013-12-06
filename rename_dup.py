#! /usr/bin/python

from gapis import *
import socket
if socket.gethostname() in ['trinh-pc',]: # add your hostname here
	from settings_local import *
else:
	from settings import *
import sys
from commons import *



# 1. get a list of duplate file name = filenamelist
# 2. loop through filenamelist, for each name, get all files
# have that name. 
# 3. If the result has more than one file, process rename

# dup_files_dict = {'timestamp1': file1, 'timestamp2': file2,}
def rename_dup_files_by_timestamp(service, dup_files_dict):
	order = dup_files_dict.keys()
	order.sort() # keys list in sorted order
	for i in order:
		if i > 0:
			new_title = dict[i]['title'] + "(" + str(order.index(i)) + ")"
			rename_file(service, dict[i]['id'], new_title)

# rename duplicate files of a single user
def rename_all_dup_files(service):
	files = retrieve_own_files(service)
	filename_list = get_filename_list(files)
	for fn in filenamelist:
		dup_files_dict = {}
		

# rename duplicate files of all users from a list
def rename_all_users_dup_files(src_emails, condition_number):
	pass



if __name__ == "__main__":
