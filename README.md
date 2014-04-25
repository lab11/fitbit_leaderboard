Fitbit Leaderboard
==================

Web application to display a graph of users' weekly steps based on fitbit.com.

Dependencies
------------

The Fitbit Leaderboard runs on Python 3 and requires a few extra packages
to be installed.

    sudo pip3 install flask fitbit



Running a Test Instance
-----------------------

The first thing you must configure are the options to the fitbit leaderboard.
Copy `reference_config.py` to `fl_config.py` and update the entries.

Once you have done that, there are a couple ways to test the fitbit leaderboard:

### Test, Fake Data

The fitbit leaderboard can be run with fake data to test the operation. To
create a test database with fake data run:

    ./create_test_db.py

Then the actual leaderboard webserver can be run with:

    ./fitbit_leaderboard.py --no-update

Browse to http://127.0.0.1:5000 to view the site.

### Test, Real Data

To use the fitbit leaderboard properly you need to register with fitbit.com
to get API keys. Then `fl_config.py` with the correct API values.

Then simply:

    ./fitbit_leaderboard.py

### Real Webserver, Real Data

Register with fitbit.com and update `fl_config.py`. Then use nginx and uwsgi.


Run With nginx and uWsgi
------------------------

nginx needs to be recompiled with the `more_set_input_headers` extension
to use the following config script. This lets the python code know what
prefix to use (for example '/fitbit') in the URLs in the HTML. The actual
/fitbit is not included in the python paths so that the code is agnostic
and could be used with any prefix (like '/fb') without changing any code.

### Example nginx conf file:

	server {
		listen   80; ## listen for ipv4; this line is default and implied

		server_name <your hostname, ex: fitbit.yourserver.com>;

		location /static {
			alias	/<path to static>/static;
		}

		location /fitbit {
			more_set_input_headers 'X-Script-Name: /fitbit';

			# Checks if the 'Host' header is set, and if not applies it.
			if ($http_host = '') {
				more_set_input_headers 'Host: <your hostname>';
			}

			include         uwsgi_params;
			uwsgi_pass      unix:/tmp/fitbit_leaderboard.sock;

			# This strips the /fitbit prefix from the url
			uwsgi_param	SCRIPT_NAME /fitbit;
			uwsgi_modifier1 30;
		}
	}

This conf file allows you to put the application with a prefix (this example
uses `/fitbit`) without changing any of the python or html code in the
leaderboard app itself. Using the `more_set_input_headers` directive does
require http://wiki.nginx.org/HttpHeadersMoreModule to be compiled in with
nginx, however.

### uWsgi conf:

	[uwsgi]
	plugins=python
	vhost=true
	gid=www-data
	uid=www-data
	master=true
	processes=5
	chdir=/<path to app>/fitbit_leaderboard
	home=/<path to app>/fitbit_leaderboard/venv
	socket=/tmp/fitbit_leaderboard.sock
	callable=app
	module=fitbit_leaderboard
	chmod-socket=666
	enable-threads=true
