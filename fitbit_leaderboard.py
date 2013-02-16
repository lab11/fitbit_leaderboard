from __future__ import with_statement
from contextlib import closing
from datetime import datetime, date
import oauth2 as oauth
import json
from threading import Timer
import time
from math import ceil

from flask import Flask, render_template, request, g, make_response, jsonify

from db import fitbit_db
import fitbit_manager

#config
DATABASE = 'fitbit.db'
DEBUG = True
SECRET_KEY = 'dev key'
USERNAME = 'admin'
PASSWORD = 'sharedspace'
REQUESTS_PER_DAY = 2000	# Fitbit API limits to 2000 requests per day

app = Flask(__name__)
app.config.from_object(__name__)

db = fitbit_db.fitbit_db(DATABASE)
fm = fitbit_manager.fitbit_manager(db)

# Do an initial update to get a weeks worth of data at the least
fm.update(db=db, number_of_days=7)

# Start the periodic event to query fitbit
def update_fitbit ():
	while True:
		db = fitbit_db.fitbit_db('fitbit.db')
		uffm = fitbit_manager.fitbit_manager()
		uffm.update(db=db)

		MINUTES = 24 * 60.
		rate = ceil((REQUESTS_PER_DAY / MINUTES) * len(db.get_users()))
		rate *= 2	# Halve request rate as a saftey margin
		time.sleep(rate * 60)	# Sleep operates in seconds, not minutes

t = Timer(1, update_fitbit)
t.start()


@app.before_request
def before_request():
	g.db = fitbit_db.fitbit_db('fitbit.db')

@app.teardown_request
def teardown_request(exception):
	if hasattr(g, 'db'):
		g.db.close()

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/register')
def register():
	request_token = uauth_client.client.fetch_request_token()
	fitbit_auth_url = uauth_client.client.authorize_token_url(request_token)
	response = make_response( render_template('register.html', fitbit_auth_url=fitbit_auth_url) )
	response.set_cookie('request_token_key', request_token.key)
	response.set_cookie('request_token_secret', request_token.secret)
	return response

@app.route("/registered", methods=["GET", "POST"])
def registered():
	if request.method == "POST":
		if not request.form['username']:
			return 'You must enter a username'
		elif not request.form['fitbit_verifier']:
			return 'You must enter a fitbit verifier'
		elif not request.cookies.get('request_token_key'):
			return "No request token key"
		elif not request.cookies.get('request_token_secret'):
			return "No request token secret"
		else:
			request_token = oauth.Token(request.cookies.get('request_token_key'), request.cookies.get('request_token_secret'))
			user_token = uauth_client.client.fetch_access_token(request_token, request.form['fitbit_verifier'])
			g.db.execute('insert into user (username, fitbit_verifier, fitbit_user_key, fitbit_user_secret) values (?, ?, ?, ?)', [request.form['username'], request.form['fitbit_verifier'], user_token.key, user_token.secret])
			g.db.commit()
		return render_template('registered.html')
	else:
		return "Method error"

@app.route("/show_users")
def show_users():
	users = g.db.get_users()
	return render_template('show_users.html', users=users)

@app.route("/group_info")
def group_info():
	data = fm.retrieve(db=g.db)
	return json.dumps(data)

@app.route("/leaderboard")
def leaderboard():
	data = fm.retrieve(db=g.db)
	return render_template('leaderboard.html', data=data)

if __name__ == '__main__':
	app.run(debug=True)
