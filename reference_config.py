"""
With the config file, you are essentially creating a python dictionary which
your Flask application looks through for it's configuration.

Only variables in all caps are read in as configuration variables.

For complete documentation and a table of FLask's configuration variables, see
http://flask.pocoo.org/docs/config/
"""
DATABASE = 'fitbit.db' #make this a full path when in production
DEBUG = False

"""
We can also load in our own custom configuration values. Again, only all
caps variables are read in.
"""
REQUESTS_PER_HOUR = 150.0	# Fitbit API limits to 150 requests per hour

CONSUMER_KEY = '' # From your fitbit api dev account
CONSUMER_SECRET = ''

"""
The page to send the user after he/she allows your app on fitbit's website.
"""
CALLBACK_URL='/registered_data'

"""
Information on where to store the user profile images.
"""
USER_IMG_LOCATION='/<path to app>/fitbit_leaderboard/static/img/users'
USER_IMG_WEB_PREFIX='/static/img/users' # relative to document root
