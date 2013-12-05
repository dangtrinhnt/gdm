#! /usr/bin/python

import httplib2
import pprint
import sys
import csv

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import SignedJwtAssertionCredentials
from apiclient import errors

import socket
if socket.gethostname() in ['trinh-pc',]: # add your hostname here
	from settings_local import *
else:
	from settings import *




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

	return build('drive', 'v2', http=http)


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

	http = httplib2.Http()
	http = credentials.authorize(http)

	return build('drive', 'v2', http=http)



###################### File ###########################################


def remove_no_parent_files(files):
	tmp = files
	for file in files:
		if not file['parents']:
			tmp.remove(file)
	return tmp


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

	except errors.HttpError, error:
		print 'An error occured: %s' % error

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
	except errors.HttpError, error:
		print 'An error occurred: %s' % error

	return None


def insert_perm(service, obj_id, value, perm_type, role):
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
	param = {}
	param['sendNotificationEmails'] = False
	try:
		perm = service.permissions().insert(
					fileId=obj_id, body=new_permission, **param).execute()
		return perm['id']
	except errors.HttpError, error:
		print 'An error occurred: %s' % error

	return None


def switch_email_domain(src_email, new_domain):
	username = src_email.split('@')[0]
	return '%s@%s' % (username, new_domain)



# copy file permissions across domains using service account
def copy_perm(src_service, dest_service, src_user_email, dest_user_email, src_obj_id, dest_obj_id):
	src_perms = retrieve_perms(src_service, src_obj_id)
	for perm in src_perms:
		if 'emailAddress' in perm.keys():
			dest_domain = dest_user_email.split('@')[1]
			value = switch_email_domain(perm['emailAddress'], dest_domain)
			if perm['emailAddress'] != src_user_email:
				perm_type = perm['type']
				role = perm['role']
				insert_perm(dest_service, dest_obj_id, value, perm_type, role)


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
	except errors.HttpError, error:
		print 'An error occurred: %s' % error



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


# make a copy of a file on a same account
def copy_file(service, origin_file_id, copy_title, parentid=None):
	"""Copy an existing file.

	Args:
		service: Drive API service instance.
		origin_file_id: ID of the origin file to copy.
		copy_title: Title of the copy.

	Returns:
		The copied file if successful, None otherwise.
	"""
	copied_file = {'title': copy_title}

	# if the copying file is a child of a folder
	if parentid:
		copied_file['parents'] = [{'id': parentid}]

	try:
		file = service.files().copy(
					fileId=origin_file_id, body=copied_file).execute()
		return file['id']
	except errors.HttpError, error:
		print 'An error occurred: %s' % error

	return None

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
	except errors.HttpError, error:
		print 'An error occurred: %s' % error
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
			new_created_ids += sub_created_ids
		else:
			copied_fileid = copy_file(service, file['id'], file['title'], parentid=new_folderid)
			new_created_ids.append({'src_id': file['id'], 'dest_id': copied_fileid})

	return new_created_ids



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
		except errors.HttpError, error:
			print 'An error occurred: %s' % error
			break

	return result


def retrieve_shared_with_me_files(service):
	query_string = 'sharedWithMe'
	return search_files(service, query_string)



# main operations

# files_map = [ {'src': 'src_email@domain.com', 'dest': 'dest_email@domain.com', 'files': fileslist}, {}, ]

def share_files_with_another(service, files_map=[]):
	perm_type = 'user'
	role = 'reader'

	perms_list = []

	for fm in files_map:
		for file in fm['files']:
			# print "Parent is: %s\n" % file['parents']
			# only share files and folders in root folder
			if file['parents'][0]['isRoot']:
				permid = insert_perm(service, file['id'], fm['dest'], perm_type, role)
				perm_pair = {'fileid': file['id'], 'permid': permid}
				perms_list.append(perm_pair)
			# print "Share file %s of %s with %s" % (file['title'], fm['src'], fm['dest'])

	return perms_list


def make_a_copy_of_shared_files(service, shared_files):
	new_files_map = []
	for file in shared_files:
		if file['parents'][0]['isRoot']:
			if file['mimeType'] == 'application/vnd.google-apps.folder':
				new_folderids = copy_folder(service, file['id'], file['title'])
				new_files_map += new_folderids
			else:
				new_fileid = copy_file(service, file['id'], file['title'])
				new_files_map.append({'src_id': file['id'], 'dest_id': new_fileid})
			# print "Copy file %s from shared with me" % (file['title'])

	return new_files_map


def disable_sharing(service, perms_list):
	for perm in perms_list:
		remove_perm(service, perm['fileid'], perm['permid'])


def copy_perms(src_service, dest_service, src_user_email, dest_user_email, new_files_map):
	for file_map in new_files_map:
		copy_perm(src_service, dest_service, src_user_email,\
					dest_user_email, file_map['src_id'], file_map['dest_id'])


# email_list = [{'src_email': 'genius@olddomain.com', 'dest_email': 'genius@newdomain.com'}]
def google_drive_migrate(email_map_list):
	for email_pair in email_map_list:
		src_service = create_drive_service(SERVICE_ACCOUNT_PKCS12_FILE,\
							SERVICE_ACCOUNT_EMAIL, OAUTH_SCOPE, email_pair['src_email'])
		allfiles = retrieve_all(src_service)
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
