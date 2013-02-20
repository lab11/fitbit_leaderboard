from __future__ import with_statement
from contextlib import closing
from datetime import datetime, date
import oauth2 as oauth
import json
from threading import Timer
import time
from math import ceil

from flask import Flask, render_template, request, g, make_response, redirect
import fitbit

from db import fitbit_db
import fitbit_manager

app = Flask(__name__)
app.config.from_envvar('FL_CONFIG')

db = fitbit_db.fitbit_db(app.config['DATABASE'])
fm = fitbit_manager.fitbit_manager()

# Do an initial update to get a weeks worth of data at the least
fm.update(db=db, number_of_days=7)

# Start the periodic event to query fitbit
def update_fitbit ():
	while True:
		print "Fitbit Online Update"
		db = fitbit_db.fitbit_db(app.config['DATABASE'])
		uffm = fitbit_manager.fitbit_manager()
		uffm.update(db=db)

		minutes = 24.0 * 60.0
		rate = ceil((app.config['REQUESTS_PER_DAY'] / minutes) * len(db.get_users()))
		rate *= 2	# Halve request rate as a saftey margin
		db.close()
		print "Sleep Info"
		print rate
		print "Current Time"
		print str(datetime.now())
		time.sleep(rate * 60)	# Sleep operates in seconds, not minutes

t = Timer(1, update_fitbit)
t.daemon = True
t.start()

@app.before_request
def before_request():
	g.db = fitbit_db.fitbit_db(app.config['DATABASE'])

@app.teardown_request
def teardown_request(exception):
	if hasattr(g, 'db'):
		g.db.close()

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/register')
def register():
	oauth_fitbit = fitbit.Fitbit(CONSUMER_KEY, CONSUMER_SECRET)
	request_token = oauth_fitbit.client.fetch_request_token(parameters={'oauth_callback':'http://nuclear.eecs.umich.edu/fitbit/registered'})
	fitbit_auth_url = oauth_fitbit.client.authorize_token_url(request_token)
	response = make_response( render_template('register.html', fitbit_auth_url=fitbit_auth_url) )
	response.set_cookie('fitbit_auth_url', fitbit_auth_url)
	response.set_cookie('oauth_secret', request_token.secret)
	return response

@app.route('/fitbit_register', methods=["POST", "GET"])
def fitbit_register(): 
	if request.method == "POST":
		response = make_response(redirect(request.cookies.get('fitbit_auth_url')))
		response.set_cookie('username', request.form['username'])
		return response
	else: 
		return "Method error. Need Post"

@app.route("/registered", methods=["GET", "POST"])
def registered():
	if not request.cookies.get('username'):
		return 'You must enter a username'
	elif not request.cookies.get('oauth_secret'):
		return 'No request secret found' 
	elif not request.args.get('oauth_token'):
		return "No request token"
	elif not request.args.get('oauth_verifier'):
		return "No verifier"
	else:
		oauth_fitbit = fitbit.Fitbit(CONSUMER_KEY, CONSUMER_SECRET)
		request_token = oauth.Token(request.args.get('oauth_token'), request.cookies.get('oauth_secret'))
		user_token = oauth_fitbit.client.fetch_access_token(request_token, request.args.get('oauth_verifier'))
		g.db.add_user(request.cookies.get('username'), request.args.get('oauth_verifier'), user_token.key, user_token.secret)
	return render_template('registered.html')

@app.route("/group_info")
def group_info():
	data = fm.retrieve(db=g.db)
	return json.dumps(data)

@app.route("/leaderboard")
def leaderboard():
	data = fm.retrieve(db=g.db)
	return render_template('leaderboard.html', data=data)

if __name__ == '__main__':
	app.run()
