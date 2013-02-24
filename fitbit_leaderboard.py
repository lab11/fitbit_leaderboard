from __future__ import with_statement
from contextlib import closing
from datetime import datetime, date, timedelta
import json
from threading import Timer
import threading
import time
from math import ceil

from flask import Flask, render_template, request, g, make_response, redirect
import fitbit

from db import fitbit_db
import fitbit_manager

app = Flask(__name__)
app.config.from_object('fl_config')

db = fitbit_db.fitbit_db(app.config['DATABASE'])
fm = fitbit_manager.fitbit_manager(
	consumer_key=app.config['CONSUMER_KEY'],
	consumer_secret=app.config['CONSUMER_SECRET'],
	callback_url=app.config['CALLBACK_URL'],
	user_img_location=app.config['USER_IMG_LOCATION'],
	user_img_web_prefix=app.config['USER_IMG_WEB_PREFIX'])

# Do an initial update to get a weeks worth of data at the least
fm.update(db=db, number_of_days=7)
fm.update_all_meta(db=db)
fm.cache_images(db=db)


def update_fitbit ():
	while True:
		print "Fitbit Online Update"
		db = fitbit_db.fitbit_db(app.config['DATABASE'])
		uffm = fitbit_manager.fitbit_manager(
			consumer_key=app.config['CONSUMER_KEY'],
			consumer_secret=app.config['CONSUMER_SECRET'],
			callback_url=app.config['CALLBACK_URL'],
			user_img_location=app.config['USER_IMG_LOCATION'],
			user_img_web_prefix=app.config['USER_IMG_WEB_PREFIX'])
		uffm.update(db=db, number_of_days=7)

		minutes = 60.0
		rate = ceil((minutes / app.config['REQUESTS_PER_HOUR']) * len(db.get_users()))
		rate += 1	# Reduce request rate as a saftey margin
		db.close()
		print "Sleep Info. rate: {0}, current time: {1}".format(rate, datetime.now())
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
	response = make_response(render_template('register.html'))
	return response

@app.route('/fitbit_register', methods=["POST", "GET"])
def fitbit_register():
	if request.method == "POST":
		response = make_response(redirect(fm.get_auth_url(db=g.db)))
		response.set_cookie('register_info', json.dumps(request.form))
		return response
	else:
		return "Method error. Need Post"

@app.route("/registered_data", methods=["GET", "POST"])
def registered_data():
	reg_info = request.cookies.get('register_info')
	if reg_info != None:
		reg_info = json.loads(reg_info)

	print reg_info

	fm.add_user(db=g.db,
	            token=request.args.get('oauth_token'),
	            verifier=request.args.get('oauth_verifier'),
	            meta=reg_info)

	return make_response(redirect('/fitbit/registered'))

@app.route("/registered")
def registered():
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
	app.run(debug=True)
