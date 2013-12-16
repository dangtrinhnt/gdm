GDM - Google Drive Migration
============================

GDM will help you to migrate your Google Drive documents from one domain to another domain


### Updates


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


### Troubleshooting

+ [Cannot use SignedJwtAssertionCredentials?](http://iambusychangingtheworld.blogspot.com/2013/12/google-drive-api-to-use.html)
+ Error When installing PyOpenSSL:
  + ["openssl/ssl.h: No such file or directory"](http://iambusychangingtheworld.blogspot.com/2013/12/fix-error-opensslsslh-no-such-file-or.html)
  + ["fatal error: Python.h: No such file or directory"](http://iambusychangingtheworld.blogspot.com/2013/12/fix-error-fatal-error-pythonh-no-such.html)
+ [The official guide for setting up Google Drive Domain-wide Service Account didn't work?](http://iambusychangingtheworld.blogspot.com/2013/12/google-drive-api-how-work-with-domain.html)


### References


* [*https://developers.google.com/drive/quickstart-python*](https://developers.google.com/drive/quickstart-python)
* [*https://developers.google.com/drive/v2/reference/*](https://developers.google.com/drive/v2/reference/)


### Contact

Found bugs or have questions?:

+ Email: dangtrinhnt[at]gmail[dot]com - Trinh Nguyen
+ Twitter: [@dangtrinhnt](https://twitter.com/dangtrinhnt)
