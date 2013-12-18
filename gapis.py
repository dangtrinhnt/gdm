#! /usr/bin/python

import httplib2
from httplib import BadStatusLine
from dateutil import parser

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from apiclient import errors
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.client import AccessTokenRefreshError


from commons import *





# single user
def create_drive_service_2_steps(client_id, client_secrect, oauth_scope, redirect_uri):
	# Run through the OAuth flow and retrieve credentials
	flow = OAuth2WebServerFlow(client_id, client_secrect, oauth_scope, redirect_uri)
	authorize_url = flow.step1_get_authorize_url()
	print 'Go to the following link in your browser: ' + authorize_url
	code = raw_input('Enter verification code: ').strip()
	credentials = flow.step2_exchange(code)

	# Create an httplib2.Http object and authorize it with our credentials
	http = httplib2.Http()
	http = credentials.authorize(http)

	try:
		drive_service = build('drive', 'v2', http=http)
		return drive_service
	except AccessTokenRefreshError, error:
		print 'Error when get drive service: %s' % error

	return None


# domain-wide
def create_drive_service(service_account_pkcs12_file,\
						service_account_email, scope, user_email):
	"""Build and returns a Drive service object authorized with the service accounts
		that act on behalf of the given user.

	Args:
		user_email: The email of the user.
	Returns:
		Drive service object.
	"""
	f = file(service_account_pkcs12_file, 'rb')
	key = f.read()
	f.close()

	credentials = SignedJwtAssertionCredentials(service_account_email, key,\
						scope=scope, sub=user_email)
	print "Finish getting credentials for user %s" % user_email

	http = httplib2.Http()
	http = credentials.authorize(http)

	print "Finish authorize user %s" % user_email

	try:
		drive_service = build('drive', 'v2', http=http)
		return drive_service
	except AccessTokenRefreshError, error:
		print "Error when getting drive service of user %s:\n > Error: %s"\
						% (user_email, error)

	return None


######################### File utils #######################################

# get file by id
def get_file(service, file_id):
	"""Print a file's metadata.

	Args:
		service: Drive API service instance.
		file_id: ID of the file to print metadata for.
	"""
	try:
		file = service.files().get(fileId=file_id).execute()
		return file
	except BadStatusLine, badstatus:
		print 'Error when getting file by id: %s' % badstatus
		# break
	except errors.HttpError, error:
		print 'An error occurred: %s' % error

	return None


# Folder: mimeType = 'application/vnd.google-apps.folder'
# Text file: mimeType = 'text/plain'
def insert_file(service, title, description, mime_type, filename, parent_id=None):
	"""Insert new file.

	Args:
		service: Drive API service instance.
		title: Title of the file to insert, including the extension.
		description: Description of the file to insert.
		parent_id: Parent folder's ID.
		mime_type: MIME type of the file to insert.
		filename: Filename of the file to insert.
	Returns:
		Inserted file metadata if successful, None otherwise.
	"""
	media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
	body = {
		'title': title,
		'description': description,
		'mimeType': mime_type
	}

	# Set the parent folder.
	if parent_id:
		body['parents'] = [{'id': parent_id}]

	try:
		file = service.files().insert(
					body=body,
					media_body=media_body).execute()
		return file['id']
	except BadStatusLine, badstatus:
		print 'Error when inserting file: %s' % badstatus
		# break
	except errors.HttpError, error:
		print 'Insert file error: %s' % error

	return None


def retrieve_all(service):
	"""Retrieve a list of File resources.

	Args:
	service: Drive API service instance.
	Returns:
	List of File resources.
	"""

	result = []
	page_token = None
	while True:
		try:
			param = {}
			if page_token:
				param['pageToken'] = page_token
			files = service.files().list(**param).execute()

			result.extend(files['items'])
			page_token = files.get('nextPageToken')
			if not page_token:
				break
		except BadStatusLine, badstatus:
			print 'Error when retrieving all files: %s' % badstatus
			break
		except errors.HttpError, error:
			print 'An error occurred: %s' % error
			break

	return result


def retrieve_perms(service, obj_id):
	"""Retrieve a list of permissions.
	Args:
		service: Drive API service instance.
		file_id: ID of the file to retrieve permissions for.
	Returns:
		List of permissions.
	"""
	try:
		permissions = service.permissions().list(fileId=obj_id).execute()
		return permissions.get('items', [])
	except BadStatusLine, badstatus:
		print 'Error when retrieving permissions: %s' % badstatus
		# break
	except errors.HttpError, error:
		print 'Retrieve permissions error: %s' % error

	return None


def insert_perm(service, obj_id, value, perm_type, role, additionalRoles=[]):
	"""Insert a new permission.

	Args:
		service: 	Drive API service instance.
		file_id: 	ID of the file to insert permission for.
		value: 		User or group e-mail address, domain name or None for 'default'
		       		type.
		perm_type: 	The value 'user', 'group', 'domain' or 'default'.
		role: 		The value 'owner', 'writer' or 'reader'.
	Returns:
		The inserted permission if successful, None otherwise.
	"""

	new_permission = {
		'value': value,
		'type': perm_type,
		'role': role
	}
	if additionalRoles:
		new_permission['additionalRoles'] = additionalRoles

	try:
		perm = service.permissions().insert( \
					fileId=obj_id, body=new_permission, sendNotificationEmails=False).execute()
		return perm['id']
	except BadStatusLine, badstatus:
		print 'Error when inserting permission: %s' % badstatus
		# break
	except errors.HttpError, error:
		print 'Insert permission error: %s' % error

	return None



# copy file permissions across domains using service account
def copy_perm(src_service, dest_service, src_user_email, dest_user_email, src_obj_id, dest_obj_id):
	src_perms = retrieve_perms(src_service, src_obj_id)
	if src_perms:
		for perm in src_perms:
			if 'emailAddress' in perm.keys():
				# if only the user is in our domain
				src_domain = src_user_email.split('@')[1]
				if src_domain in perm['emailAddress']:
					dest_domain = dest_user_email.split('@')[1]
					value = switch_email_domain(perm['emailAddress'], dest_domain)
				else:
					value = perm['emailAddress']

				if perm['emailAddress'] != src_user_email:
					if perm['emailAddress'] != dest_user_email:
						perm_type = perm['type']
						role = perm['role']
						additionalRoles = []
						if 'additionalRoles' in perm.keys():
							additionalRoles = perm['additionalRoles']
						print "Copy perm role %s for %s to file %s of user %s" \
								% (role, perm['emailAddress'], dest_obj_id, dest_user_email)
						insert_perm(dest_service, dest_obj_id, value, perm_type, role, additionalRoles)



def remove_perm(service, obj_id, permission_id):
	"""Remove a permission.

	Args:
		service: Drive API service instance.
		file_id: ID of the file to remove the permission for.
		permission_id: ID of the permission to remove.
	"""
	try:
		service.permissions().delete(
			fileId=obj_id, permissionId=permission_id).execute()
	except BadStatusLine, badstatus:
		print 'Error when removing permission: %s' % badstatus
		# break
	except errors.HttpError, error:
		print 'Remove permissions error: %s' % error



def get_perm_id_for_email(service, email):
	"""Prints the Permission ID for an email address.

	Args:
		service: Drive API service instance.
		email: Email address to retrieve ID for.
	"""
	try:
		id_resp = service.permissions().getIdForEmail(email=email).execute()
		# print id_resp['id']
		return id_resp['id']
	except BadStatusLine, badstatus:
		print 'Error when getting permission id for email: %s' % badstatus
		# break
	except errors.HttpError, error:
		print 'An error occured: %s' % error

	return None



def get_existed_files(service, org_obj_id, parentid='root'):
	same_title_files = []
	is_existed = False
	is_old = False

	org_file = get_file(service, org_obj_id)

	# If parentid is provided, search in that folder,
	# If no, search in root only by default
	query_string = "'%s' in parents \
					and title = '%s' \
					and trashed = false" \
					% (parentid, org_file['title'])

	same_title_files = search_files(service, query_string)
	if same_title_files:
		is_existed = True
		for s_file in same_title_files:
			# if s_file['parents'][0]['id']==
			if s_file['mimeType'] == org_file['mimeType']:
				if s_file['modifiedDate'] < org_file['modifiedDate']:
					is_old = True
					break

	return same_title_files, is_existed, is_old


def delete_file(service, file_id):
	"""Permanently delete a file, skipping the trash.

	Args:
		service: Drive API service instance.
		file_id: ID of the file to delete.
	"""
	try:
		service.files().delete(fileId=file_id).execute()
	except BadStatusLine, badstatus:
		print 'Error when deleting file: %s' % badstatus
		# break
	except errors.HttpError, error:
		print 'Delete file error: %s' % error


def search_files(service, query_string):
	result = []
	page_token = None
	while True:
		try:
			param = {}
			if page_token:
				param['pageToken'] = page_token
			param['q'] = query_string
			files = service.files().list(**param).execute()

			result.extend(files['items'])
			page_token = files.get('nextPageToken')
			if not page_token:
				break
		except BadStatusLine, badstatus:
			print 'Error when searching files: %s' % badstatus
			break
		except errors.HttpError, error:
			print 'Error when searching file: %s' % error
			break

	return result


def retrieve_shared_with_me_files(service):
	query_string = 'sharedWithMe'
	return search_files(service, query_string)



def retrieve_own_files(service):
	tmp = []
	allfiles = search_files(service, "trashed = false")
	if allfiles:
		for file in allfiles:
			if file['owners'][0]['isAuthenticatedUser']:
				tmp.append(file)

	return tmp
	

def get_own_files_by_email(service, user_email):
	query = "'%s' in owners and trashed = false" % user_email
	files = search_files(service, query)
	return files


def get_own_files(service):
	query = "'me' in owners and trashed =false"
	files = search_files(service, query)
	return files


def get_parents(service, file_id):
	"""Print a file's parents.
	
	Args:
		service: Drive API service instance.
		file_id: ID of the file to print parents for.
	"""
	try:
		parents = service.parents().list(fileId=file_id).execute()
		#~ for parent in parents['items']:
		  #~ print 'File Id: %s' % parent['id']
		return parents
	except BadStatusLine, badstatus:
		print 'BadStatusLine error when getting parents of file (%s): %s' % (file_id, badstatus)
	except errors.HttpError, error:
		print 'HttpError when getting parents of file (%s): %s' % (file_id, error)

	return None


def rename_file(service, file_id, new_title):
	"""Rename a file.

	Args:
	service: Drive API service instance.
	file_id: ID of the file to rename.
	new_title: New title for the file.
	Returns:
	Updated file metadata if successful, None otherwise.
	"""
	try:
		file = {'title': new_title}

		# Rename the file.
		updated_file = service.files().patch(
							fileId=file_id,
							body=file,
							fields='title').execute()

		return updated_file
	except BadStatusLine, badstatus:
		print 'Error when renaming file: %s' % badstatus
		# break
	except errors.HttpError, error:
		print 'Rename file error: %s' % error

	return None


def update_file(service, file_id, new_title, new_description, new_mime_type,
					new_filename, new_revision):
	"""Update an existing file's metadata and content.

	Args:
		service: Drive API service instance.
		file_id: ID of the file to update.
		new_title: New title for the file.
		new_description: New description for the file.
		new_mime_type: New MIME type for the file.
		new_filename: Filename of the new content to upload.
		new_revision: Whether or not to create a new revision for this file.
	Returns:
		Updated file metadata if successful, None otherwise.
	"""
	try:
		# First retrieve the file from the API.
		file = service.files().get(fileId=file_id).execute()

		# File's new metadata.
		file['title'] = new_title
		file['description'] = new_description
		file['mimeType'] = new_mime_type

		# File's new content.
		media_body = MediaFileUpload(
			new_filename, mimetype=new_mime_type, resumable=True)

		# Send the request to the API.
		updated_file = service.files().update(
			fileId=file_id,
			body=file,
			newRevision=new_revision,
			media_body=media_body).execute()
		return updated_file
	except BadStatusLine, badstatus:
		print 'Error when updating file: %s' % badstatus
		# break
	except errors.HttpError, error:
		print 'An error occurred: %s' % error

	return None



def change_mimeType_file(service, file_id, new_mime_type):
	#~ try:
		#~ # First retrieve the file from the API.
		#~ file = service.files().get(fileId=file_id).execute()
#~ 
		#~ # File's new metadata.
		#~ file['mimeType'] = new_mime_type
		#~ filename = file['title']
#~ 
		#~ # File's new content.
		#~ media_body = MediaFileUpload(
			#~ filename, mimetype=new_mime_type, resumable=True)
#~ 
		#~ # Send the request to the API.
		#~ updated_file = service.files().update(
			#~ fileId=file_id,
			#~ body=file,
			#~ media_body=media_body).execute()
		#~ return updated_file
	#~ except BadStatusLine, badstatus:
		#~ print 'Error when updating file: %s' % badstatus
		#~ # break
	#~ except errors.HttpError, error:
		#~ print 'An error occurred: %s' % error
#~ 
	#~ return None
	pass



# make a copy of a file on a same account
def copy_file(service, org_file, parentid=None):
	"""Copy an existing file.

	Args:
		service: Drive API service instance.
		origin_file_id: ID of the origin file to copy.
		copy_title: Title of the copy.

	Returns:
		The copied file if successful, None otherwise.
	"""
	body = {}
	body['title'] = org_file['title']
	body['mimeType'] = org_file['mimeType']

	# if the copying file is a child of a folder
	if parentid:
		body['parents'] = [{'id': parentid}]

	try:
		copied_file = service.files().copy(fileId=org_file['id'], body=body).execute()
		return copied_file
	except BadStatusLine, badstatus:
		print 'Error when copying file: %s' % badstatus
		# break
	except errors.HttpError, error:
		print 'Copy file error: %s' % error

	return None


def copy_unique_file(service, org_file, parentid=None):
	print "Copying file %s of parentid %s" % (org_file['id'], parentid)
	#~ org_title = org_file['title']
	org_title = clean_query_string(org_file['title'])
	query = "'me' in owners and title = '%s' and trashed = false" \
				% org_title

	if parentid:
		query += " and '%s' in parents" % parentid
	else:
		query += " and 'root' in parents"
	existed_files = search_files(service, query)
	if existed_files:
		tmp = {}
		for file in existed_files:
			if org_file['mimeType'] == file['mimeType'] \
				or (org_file['mimeType'] == 'application/vnd.google-apps.spreadsheet' \
					and file['mimeType'] == 'application/vnd.google-apps.form'):
				
				if is_older(file, org_file):
					print "Delete existed file %s" % (file['title'].encode('utf8'))
					delete_file(service, file['id'])
				else:
					#~ print "Skip copying file %s" % org_file['title'].encode('utf8')
					tmp[parser.parse(file['modifiedDate'])] = file

		if len(tmp) >= 2: #rename duplicate files and return the unchanged file
			print "Skip copying file and rename duplicate files"
			return rename_dup_files_by_modified_date(service, tmp)
		elif len(tmp) == 1:
			print "Skip copying file"
			return tmp.values()[0]['id']

	copied_file = copy_file(service, org_file, parentid)

	print "Finish copying file %s" % (org_file['id'])

	return copied_file['id']


#########################################################################

###################### Folder ###########################################


def insert_folder(service, title, desc, parentid=None):
	body = {
		'title': title,
		'description': desc,
		'mimeType': 'application/vnd.google-apps.folder'
	}
	if parentid:
		body['parents'] = [{'id': parentid}]

	try:
		folder = service.files().insert(body=body).execute()
		# pprint.pprint(folder)
		return folder['id']
	except BadStatusLine, badstatus:
		print 'Error when inserting folder: %s' % badstatus
		# break
	except errors.HttpError, error:
		print 'Insert folder error: %s' % error
	return None


def copy_folder(service, folder_id, folder_title, parentid=None):
	# 1. create a folder with the same name in mydrive
	# 2. make a copy of all files in the source folder
	# 3. Assign the new folder as parents of the copied files

	new_created_ids = []
	new_folderid = insert_folder(service, folder_title, folder_title, parentid)
	new_created_ids.append({'src_id': folder_id, 'dest_id': new_folderid})

	query_string = "'%s' in parents" % (folder_id)

	files = search_files(service, query_string)
	for file in files:
		if file['mimeType'] == 'application/vnd.google-apps.folder':
			sub_created_ids = copy_folder(service, file['id'], file['title'], parentid=new_folderid)
			if sub_created_ids:
				new_created_ids += sub_created_ids
		else:
			copied_fileid = copy_unique_file(service, file, parentid=new_folderid)
			if copied_fileid:
				new_created_ids.append({'src_id': file['id'], 'dest_id': copied_fileid})

	return new_created_ids



def copy_unique_folder(service, folder_id, folder_title, parentid=None):
	# 1. create a folder with the same name in mydrive
	# 2. make a copy of all files in the source folder
	# 3. Assign the new folder as parents of the copied files

	new_created_ids = []

	folder_title = clean_query_string(folder_title)
	# copy the folder
	# check if there is any existed folder
	query = "'me' in owners and title = '%s' \
				and mimeType = 'application/vnd.google-apps.folder' \
				and trashed = false" \
				% (folder_title)
	if parentid:
		query += " and '%s' in parents" % parentid
	else:
		query += " and 'root' in parents"
	existed_folders = search_files(service, query)
	if existed_folders:
		new_folderid = existed_folders[0]['id']
	else:
		new_folderid = insert_folder(service, folder_title, folder_title, parentid)

	if new_folderid:
		new_created_ids.append({'src_id': folder_id, 'dest_id': new_folderid})
	
		# copy the children files and folders
		query_string = "'me' in owners and '%s' in parents and trashed = false" \
						% (folder_id)
		files = search_files(service, query_string)
		if files:
			print "All children of folder %s" % folder_title.encode('utf8')
			for file in files:
				print "+ %s" % file['title'].encode('utf8')
				if file['mimeType'] == 'application/vnd.google-apps.folder':
					sub_created_ids = copy_unique_folder(service, file['id'], file['title'], parentid=new_folderid)
					if sub_created_ids:
						new_created_ids += sub_created_ids
				else:
					copied_fileid = copy_unique_file(service, file, parentid=new_folderid)
					if copied_fileid:
						new_created_ids.append({'src_id': file['id'], 'dest_id': copied_fileid})
			print "Finish copying children of folder %s\n" % folder_title.encode('utf8')

	return new_created_ids


########################################################################

################## Rename duplicate files ##############################

# dup_files_dict = { datetime_obj1: file1, datetime_obj2: file2,}
def rename_dup_files_by_modified_date(service, dup_files_dict):
	order = dup_files_dict.keys()
	order.sort(reverse=True) # keys list in DESC order
	for i in order:
		if order.index(i) > 0:
			print "Renaming file %s" % dup_files_dict[i]['title']
			new_title = dup_files_dict[i]['title'] + " (" \
								+ str(order.index(i)) + ")"
			updated_file = rename_file(service, dup_files_dict[i]['id'], new_title)
			if updated_file:
				print "File %s has been renamed to %s" % (dup_files_dict[i]['title'], new_title)
			else:
				print "Fail to rename file %s" % dup_files_dict[i]['title']

	return dup_files_dict[order[0]]['id']


# rename duplicate files of a single user
def rename_all_dup_files(service):
	files = get_own_files(service)
	if files:
		filename_list = get_unique_file_name_list(files)
		if len(filename_list) < len(files):
			for fn in filename_list:
				dup_files_dict = {}
				for file in files:
					if file['mimeType'] == fn['mimeType']:
						if file['parents']:
							if file['parents'][0]['id'] == fn['parentid']:
								if file['title'] == fn['title']:
									dt = parser.parse(file['modifiedDate'])
									dup_files_dict[dt] = file
				if len(dup_files_dict) > 1:
					rename_dup_files_by_modified_date(service, dup_files_dict)

########################################################################




# main operations for migration

# files_map = [ {'src': 'src_email@domain.com', 'dest': 'dest_email@domain.com', 'files': fileslist}, {}, ]
def share_files(service, files_map):
	perm_type = 'user'
	role = 'reader'

	perms_list = []
	shared_files = []
	for fm in files_map:
		for file in fm['files']:
			# only share files and folders in root
			if file['parents']:
				if file['parents'][0]['isRoot']:
					permid = insert_perm(service, file['id'], fm['dest'], perm_type, role)
					if permid:
						perm_pair = {'fileid': file['id'], 'permid': permid}
						perms_list.append(perm_pair)
						shared_files.append(file)

	return perms_list, shared_files

# make a copy of shared files
def make_a_copy(service, shared_files):
	new_files_map = []
	for file in shared_files:
		if file['parents']:
			if file['parents'][0]['isRoot']:
				if file['mimeType'] == 'application/vnd.google-apps.folder':
					# have to check more
					new_folderids = copy_unique_folder(service, file['id'], file['title'])
					if new_folderids:
						new_files_map += new_folderids
				else:
					new_fileid = copy_unique_file(service, file)
					if new_fileid:
						new_files_map.append({'src_id': file['id'], 'dest_id': new_fileid})

	return new_files_map

# perms_list = [{'fileid': <fileid>, 'permid': <permid>}, {...},]
def disable_sharing(service, perms_list):
	for perm in perms_list:
		remove_perm(service, perm['fileid'], perm['permid'])


def copy_perms(src_service, dest_service, src_user_email, dest_user_email, new_files_map):
	for file_map in new_files_map:
		if file_map['dest_id']:
			copy_perm(src_service, dest_service, src_user_email,\
						dest_user_email, file_map['src_id'], file_map['dest_id'])
		else:
			print "Missing dest_id when copying permissions of %s" % src_user_email
