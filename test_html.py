from __future__ import with_statement
from contextlib import closing
from datetime import datetime, date, timedelta
import json
from threading import Timer
import threading
import time
from math import ceil

from flask import Flask, render_template, request, g, make_response, redirect


app = Flask(__name__)



@app.before_request
def before_request():
	g.meta = {'root':'http://nuclear.eecs.umich.edu/fitbit'}


@app.route('/')
def home():
	return render_template('home.html', meta=g.meta)


@app.route("/registered")
def registered():
	return render_template('registered.html', meta=g.meta)


@app.route("/leaderboard")
def leaderboard():
	return render_template('leaderboard.html', meta=g.meta)

if __name__ == '__main__':
	app.run(debug=True)
