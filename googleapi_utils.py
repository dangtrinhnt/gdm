#! /usr/bin/python

import httplib2
import pprint

from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from apiclient import errors

import socket
if socket.gethostname() in ['trinh-pc',]: # add your hostname here
	from settings_local import *
else:
	from settings import *





def authorize_app(client_id, client_secrect, oauth_scope, redirect_uri):
	# Run through the OAuth flow and retrieve credentials
	flow = OAuth2WebServerFlow(client_id, client_secrect, oauth_scope, redirect_uri)
	authorize_url = flow.step1_get_authorize_url()
	print 'Go to the following link in your browser: ' + authorize_url
	code = raw_input('Enter verification code: ').strip()
	credentials = flow.step2_exchange(code)

	# Create an httplib2.Http object and authorize it with our credentials
	http = httplib2.Http()
	http = credentials.authorize(http)

	drive_service = build('drive', 'v2', http=http)
	return drive_service



###################### File ###########################################

# Folder: mimeType = 'application/vnd.google-apps.folder'
# Text file: mimeType = 'text/plain'


def insert_a_file(service, filename, title, desc):
	# Insert a file
	media_body = MediaFileUpload(filename, mimetype='text/plain', resumable=True)
	body = {
		'title': title,
		'description': desc,
		'mimeType': 'text/plain'
	}

	file = service.files().insert(body=body, media_body=media_body).execute()
	pprint.pprint(file)



def retrieve_all_files_and_folders(service):
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


def retrieve_perms(service, file_id):
	"""Retrieve a list of permissions.
	Args:
		service: Drive API service instance.
		file_id: ID of the file to retrieve permissions for.
	Returns:
		List of permissions.
	"""
	try:
		permissions = service.permissions().list(fileId=file_id).execute()
		return permissions.get('items', [])
	except errors.HttpError, error:
		print 'An error occurred: %s' % error

	return None


def insert_file_perm(service, file_id, value, perm_type, role):
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
	try:
		return service.permissions().insert(
				fileId=file_id, body=new_permission).execute()
	except errors.HttpError, error:
		print 'An error occurred: %s' % error

	return None


def remove_perm(service, file_id, permission_id):
	"""Remove a permission.

	Args:
		service: Drive API service instance.
		file_id: ID of the file to remove the permission for.
		permission_id: ID of the permission to remove.
	"""
	try:
		service.permissions().delete(
			fileId=file_id, permissionId=permission_id).execute()
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



def copy_file(service, origin_file_id, copy_title):
	"""Copy an existing file.

	Args:
		service: Drive API service instance.
		origin_file_id: ID of the origin file to copy.
		copy_title: Title of the copy.

	Returns:
		The copied file if successful, None otherwise.
	"""
	copied_file = {'title': copy_title}
	try:
		return service.files().copy(
			fileId=origin_file_id, body=copied_file).execute()
	except errors.HttpError, error:
		print 'An error occurred: %s' % error

	return None

#########################################################################


###################### Folder ###########################################


def create_a_folder(service, title, desc, parentid=None):
	body = {
		'title': title,
		'description': desc,
		'mimeType': 'application/vnd.google-apps.folder'
	}
	if parentid:
		body['parents'] = [{'id': parentid}]

	folder = service.files().insert(body=body).execute()
	pprint.pprint(folder)
	return folder['id']


def copy_folder(service, folder_id, folder_title):
	pass

def insert_folder_perm(service, folder_id, value, perm_type, role):
	pass


#########################################################################


if __name__ == "__main__":

	drive_service = authorize_app(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)

	# filename = 'doc2.txt'
	# title = 'Super genius document'
	# desc = 'This is a genius document'

	# insert_a_file(drive_service, filename, title, desc)
	# allfiles = retrieve_all_files_and_folders(drive_service)
	# print allfiles
	# for myfile in allfiles:
	# 	if 'mimeType' in myfile.keys():
	# 		print "Mimetype of %s is: %s\n" % (myfile['title'], myfile['mimeType'])
	# 		print "Id is: %s" % (myfile['id'])
	# 		if myfile['mimeType'] == 'application/vnd.google-apps.folder':
	# 			print "Copying folder %s" % (myfile['title'])
	new_folderid = create_a_folder(drive_service, 'Home folder', 'Holy genius folder!!!!')


	# 	# perms = retrieve_perms(drive_service, myfile['id'])
	# 	# print "Permission of %s (%s) is: %s" % (myfile['title'], myfile['id'], perms)
	# 	print "File id of %s is: %s" % (myfile['title'], myfile['id'])


	# copy_file(drive_service, '0B_mF99vmvWTEWmZObEpuUTF1ZU0', 'Copy of genius document')

	# mypermid = get_perm_id_for_email(drive_service, 'genius@ssis.edu.vn')
	# print "Permission ID for genius@ssis.edu.vn: %s" % (mypermid)

	# org_fileid = '0B_mF99vmvWTEcDZzc3hVVmRoOUU'
	# copy_fileid = '0B_mF99vmvWTEM0lvVXhJWUw5blk'
	# org_perms = retrieve_perms(drive_service, org_fileid)
	# for perm in org_perms:
	# 	if 'emailAddress' in perm.keys():
	# 		value = perm['emailAddress']
	# 		if value != 'nguyentrongdangtrinh@gmail.com':
	# 			perm_type = perm['type']
	# 			role = perm['role']
	# 			insert_file_perm(drive_service, copy_fileid, value, perm_type, role)

	# permid = get_perm_id_for_email(drive_service, 'trnguyen@ssis.edu.vn')
	# remove_perm(drive_service, copy_fileid, permid)