GDM - Google Drive Migration
============================

GDM will help you to migrate your Google Drive documents from one domain to another domain


### Updates


##### + 12/19/2013:

+ Not use "'me' in owners" query when searching for children files of shared folders


##### + 12/18/2013:

+ Get user's own files by query:

	> **"'me' in owners"**

+ Add **"'me' in owners"** to query when searching files
+ Simplify functions's name
+ **share_files** function returns permission id list and shared files list
+ Pass shared files list to make_a_copy instead of all files.


##### + 12/17/2013:

+ Get files in which the processing user is the owners with query:

	> **"'username@mydomain.com' in owners and trashed = false"**

+ Do not start renaming files process if length of the unique file names is equal the number of files, which mean there is no duplicate file:

	> **len(filename_list) < len(files)**

+ Get parents of a file by fileId


##### + 12/15/2013:

+ Test with 876 users and finish migrating in > 2 days


##### + 12/12/2013:

+ Catch httplib.BadStatusLine exception on all query functionalities (insert, update, delete...)
+ Still return the file['id'] if the file existed and newer when copying (for copy permissions)
+ encode('utf8') when printing out info to console


##### + 12/11/2013:

+ Tested with multiple accounts:
    * Got error 500 when copying file error.csv. OK after re-running the script.
    * Got error "httplib.BadStatusLine: ''" when copying permissions. Fixed by catch BadStatusLine exception in "search_files".


##### + 12/10/2013:

+ Copy unique files and folders (including children files and folders)
   * skip copying newer existed files / folders
+ Copy permissions with additionalRoles (commenter)
+ More console output for debugging


##### + 12/09/2013:

+ Rename duplicate files/folders of all users by modified date
+ Delete file by id
+ Copy unique file
+ Processing gdm with condition parameters


##### + 12/05/2013:

+ Get accounts which have duplicate files/folders


##### + 12/04/2013: Added functionalities:

+ Copy permissions
+ Copy all permissions of all files
+ Create drive service with service account
+ Share files and folders
+ Disable sharing
+ Migrate files and folders


##### + 12/01/2013: Just add some utilities to manipulate google drive api, such as:

+ authorize app
+ insert file
+ retreive files and folders
+ retreive permissions
+ insert permission
+ remove permission
+ get permission id from email
+ copy file
+ create a folder


### Requirements


+ google-api-python-client==1.2
+ httplib2==0.8
+ pyOpenSSL==0.13.1
+ python-dateutil==2.2


### Usage


##### 1/ Create a virtualenv environment and install requirements:

> **username@user-host**:/path/to/gdm$ virtualenv /home/.venv/your_env

> **username@user-host**:/path/to/gdm$ source /home/.venv/your_env/bin/activate

> **(your_env)username@user-host**:/path/to/gdm$ pip install -r requirements.txt


##### 2/ Run the migration script to start the emails migrations:

> **(your_env)username@user-host**:/path/to/gdm$ python gdm.py /path/to/email_mapping_list.csv <condition number>

* email_mapping_list.csv (2 columns: src - old domain email address, dest - new domain email address):

| src                     | dest                    |
| ----------------------- | ----------------------- |
| username1@olddomain.com | username1@newdomain.com |
| username2@olddomain.com | username2@newdomain.com |
| username3@olddomain.com | username3@newdomain.com |


* condition number: all posible numbers are: 

> 0,1,2,3,4,5,6,7,8,9 or 'all'


### Troubleshooting

+ [Cannot use SignedJwtAssertionCredentials?](http://iambusychangingtheworld.blogspot.com/2013/12/google-drive-api-to-use.html)
+ Error When installing PyOpenSSL:
  + ["openssl/ssl.h: No such file or directory"](http://iambusychangingtheworld.blogspot.com/2013/12/fix-error-opensslsslh-no-such-file-or.html)
  + ["fatal error: Python.h: No such file or directory"](http://iambusychangingtheworld.blogspot.com/2013/12/fix-error-fatal-error-pythonh-no-such.html)
+ [The official guide for setting up Google Drive Domain-wide Service Account didn't work?](http://iambusychangingtheworld.blogspot.com/2013/12/google-drive-api-how-work-with-domain.html)
+ [_csv.Error: Could not determine delimiter](http://iambusychangingtheworld.blogspot.com/2013/12/python-csv-error-when-read-data-from.html)


### Notes

+ I used only one Service Account because I migrated users's documents from sub.mydomain.com to mydomain.com. So, you need to create 2 Service Accounts, one for your old domain, one for your new domain. Then, you have to modify the gdm.py file to use the correct Service Account for each domain.


### References


* [*https://developers.google.com/drive/quickstart-python*](https://developers.google.com/drive/quickstart-python)
* [*https://developers.google.com/drive/v2/reference/*](https://developers.google.com/drive/v2/reference/)


### Contact

Found bugs or have questions?:

+ Email: dangtrinhnt[at]gmail[dot]com - Trinh Nguyen
+ Twitter: [@dangtrinhnt](https://twitter.com/dangtrinhnt)
