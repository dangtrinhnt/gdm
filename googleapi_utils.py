#! /usr/bin/python

import httplib2
import pprint
import sys

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
	try:
		perm = service.permissions().insert(
					fileId=obj_id, body=new_permission).execute()
		return perm['id']
	except errors.HttpError, error:
		print 'An error occurred: %s' % error

	return None


# copy file permissions across domains using service account
def copy_perm(src_service, dest_service, src_user_email, dest_user_email, src_obj_id, dest_obj_id):
	src_perms = retrieve_perms(src_service, src_obj_id)
	for perm in src_perms:
		if 'emailAddress' in perm.keys():
			value = perm['emailAddress']
			if value != src_user_email and value != dest_user_email:
				perm_type = perm['type']
				role = perm['role']
				# return inserted permission id
				return insert_perm(dest_service, dest_obj_id, value, perm_type, role)


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


# make a copy of a file/folder on a same account
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
		file = service.files().copy(
					fileId=origin_file_id, body=copied_file).execute()

		# copy permission
		# if copy_perms:
		# 	copy_perm(service, service, src_user_email, dest_user_email, origin_file_id, file['id'])

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
		pprint.pprint(folder)
		return folder['id']
	except errors.HttpError, error:
		print 'An error occurred: %s' % error
	return None


def copy_folder(service, folder_id, folder_title):
	# 1. copy
	pass




#########################################################################


if __name__ == "__main__":

	#drive_service = create_drive_service_web_2_steps(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)

	test_useremail = 'umasse@student.ssis.edu.vn'
	service = create_drive_service(SERVICE_ACCOUNT_PKCS12_FILE, SERVICE_ACCOUNT_EMAIL, OAUTH_SCOPE, test_useremail)