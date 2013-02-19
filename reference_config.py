"""
With the config file, you are essentially creating a python dictionary which 
your Flask application looks through for it's configuration. 

Only variables in all caps are read in as configuration variables.

For complete documentation and a table of FLask's configuration variables, see 
http://flask.pocoo.org/docs/config/
"""
DATABASE = 'fitbit.db' #make this a full path when in production
DEBUG = False
SECRET_KEY = 'super secret'
USERNAME = 'admin'
PASSWORD = 'super random'


"""
We can also load in our own custom configuration values. Again, only all 
caps variables are read in. 
"""
REQUESTS_PER_DAY = 2000.0	# Fitbit API limits to 2000 requests per day
CONSUMER_KEY = '4f0defd304af44e9a6790b0087070313'
CONSUMER_SECRET = '737d767bf5024fda928ea039d77e1098'