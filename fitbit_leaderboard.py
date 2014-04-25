#!/usr/bin/env python3

import argparse
import datetime
import json
import threading
import time
import math

#from flask import Flask, render_template, request, g, make_response, redirect
import flask
import fitbit

from db import fitbit_db
import fitbit_manager

# Update steps for all users
def update_fitbit ():
	while True:
		print("Fitbit Online Update")
		db = fitbit_db.fitbit_db(app.config['DATABASE'])
		uffm = fitbit_manager.fitbit_manager(
			consumer_key=app.config['CONSUMER_KEY'],
			consumer_secret=app.config['CONSUMER_SECRET'],
			user_img_location=app.config['USER_IMG_LOCATION'],
			user_img_web_prefix=app.config['USER_IMG_WEB_PREFIX'])
		uffm.update(db=db, number_of_days=7)

		minutes = 60.0
		rate = math.ceil((minutes / app.config['REQUESTS_PER_HOUR']) * \
		            len(db.get_users()))
		rate += 1	# Reduce request rate as a safety margin
		db.close()
		print("Sleep Info. rate: {0}, current time: {1}".format(rate,
			datetime.datetime.now()))
		time.sleep(rate * 60)	# Sleep operates in seconds, not minutes

# Update meta information once an hour
def update_user_meta ():
	while True:
		print("Fitbit Online Meta Update")
		db = fitbit_db.fitbit_db(app.config['DATABASE'])
		uffm = fitbit_manager.fitbit_manager(
			consumer_key=app.config['CONSUMER_KEY'],
			consumer_secret=app.config['CONSUMER_SECRET'],
			user_img_location=app.config['USER_IMG_LOCATION'],
			user_img_web_prefix=app.config['USER_IMG_WEB_PREFIX'])
		uffm.update_all_meta(db)
		db.close()
		# Sleep for an hour
		time.sleep(3600)	# Sleep operates in seconds, not minutes


parser = argparse.ArgumentParser()
parser.add_argument('--no-update',
                    action='store_true',
                    help="Do not retrieve information from Fitbit")
args = parser.parse_args()

# Create objects that we need for the application

app = flask.Flask(__name__)
app.config.from_object('fl_config')

db = fitbit_db.fitbit_db(app.config['DATABASE'])
fm = fitbit_manager.fitbit_manager(
	consumer_key=app.config['CONSUMER_KEY'],
	consumer_secret=app.config['CONSUMER_SECRET'],
	user_img_location=app.config['USER_IMG_LOCATION'],
	user_img_web_prefix=app.config['USER_IMG_WEB_PREFIX'])

fm.cache_images(db=db)


# Check if the user does not want to update from Fitbit
if not args.no_update:
	# Do an initial update to get a weeks worth of data at the least
	fm.update(db=db, number_of_days=7)
	fm.update_all_meta(db=db)
	fm.cache_images(db=db)

	# Run functions to update from fitbit periodically
	t1 = threading.Timer(1, update_fitbit)
	t1.daemon = True
	t1.start()

	t2 = threading.Timer(1, update_user_meta)
	t2.daemon = True
	t2.start()


@app.before_request
def before_request():
	flask.g.db = fitbit_db.fitbit_db(app.config['DATABASE'])
	flask.g.host = flask.request.headers['Host'] or 'localhost'

	flask.g.site_root = ''
	if 'X-Script-Name' in flask.request.headers:
		flask.g.site_root = flask.request.headers['X-Script-Name']

	flask.g.host = 'localhost'
	if 'Host' in flask.request.headers:
		flask.g.host = flask.request.headers['Host']

	flask.g.meta = {'root': flask.g.site_root}

@app.teardown_request
def teardown_request(exception):
	if hasattr(flask.g, 'db'):
		flask.g.db.close()

@app.route('/')
def home():
	return flask.render_template('home.html', meta=flask.g.meta)

@app.route('/register')
def register():
	response = flask.make_response(flask.render_template('register.html', meta=flask.g.meta))
	return response

@app.route('/fitbit_register', methods=["POST", "GET"])
def fitbit_register():
	if flask.request.method == "POST":
		auth_url = fm.get_auth_url(db=flask.g.db,
		  callback_url='http://' + flask.g.host + flask.g.site_root + app.config['CALLBACK_URL'])
		response = flask.make_response(flask.redirect(auth_url))
		response.set_cookie('register_info', json.dumps(flask.request.form))
		return response
	else:
		return "Method error. Need Post"

@app.route("/registered_data", methods=["GET", "POST"])
def registered_data():
	reg_info = flask.request.cookies.get('register_info')
	if reg_info != None:
		reg_info = json.loads(reg_info)

	try:
		fm.add_user(db=flask.g.db,
		            token=flask.request.args.get('oauth_token'),
		            verifier=flask.request.args.get('oauth_verifier'),
		            meta=reg_info)
	except Exception as e:
		print('EXCEPTION')
		print(e)
		return flask.make_response(flask.redirect(flask.g.site_root + '/registered_fail'))


	return flask.make_response(flask.redirect(flask.g.site_root + '/registered'))

@app.route("/registered")
def registered():
	return flask.render_template('registered.html', meta=flask.g.meta)

@app.route("/group_info")
def group_info():
	data = fm.retrieve(db=flask.g.db)
	return json.dumps(data)

@app.route("/leaderboard")
def leaderboard():
	data = fm.retrieve(db=flask.g.db)
	return flask.render_template('leaderboard.html', data=data, meta=flask.g.meta)

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
