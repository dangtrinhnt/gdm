# Copy your credentials from the console
CLIENT_ID = '[[YOUR CLIENT ID]]'
CLIENT_SECRET = '[[YOUR CLIENT SECRET]]'

"""Email of the Service Account"""
SERVICE_ACCOUNT_EMAIL = '<some-id>@developer.gserviceaccount.com'

"""Path to the Service Account's Private Key file"""
SERVICE_ACCOUNT_PKCS12_FILE_PATH = '/path/to/<public_key_fingerprint>-privatekey.p12'

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'