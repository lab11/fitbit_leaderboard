Fitbit Leaderboard
==================

Web application to display a graph of users' weekly steps based on fitbit.com.

Dependencies
------------

Fitbit Leaderboard requires a few dependencies to be installed.

```
pip install oauth2
pip install flask
pip install fitbit
```

Running Locally
---------------

To run the server on your localhost you need to update fl_config.py with your
specific settings. This means getting api keys and setting the paths.

Then simply:

    python fitbit_leaderboard.py


Run With nginx and uWsgi
------------------------

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
