import sqlite3
import datetime

TABLE_PREFIX = "fitbit_lb_"

class fitbit_db:

	def __init__ (self, db_name):
		self.db_name = db_name
		self.db      = sqlite3.connect(db_name)

	# Save the temporary oauth secret in the database
	def store_oauth_secret (self, key, secret):
		q = """INSERT INTO {0}fitbit_oauth
		       VALUES(NULL, ?, ?, NULL)
		    """.format(TABLE_PREFIX)
		self.db.execute(q, ((key, secret)))
		self.db.commit()

	# Retreive the temporary secret that is associated with a given token
	def get_oauth_secret (self, token):
		q = """SELECT oauth_secret
		       FROM {0}fitbit_oauth
		       WHERE oauth_token = ?
		    """.format(TABLE_PREFIX)
		cur = self.db.execute(q, (token,))
		row = cur.fetchone()
		if not row:
			raise Exception('Could not find secret for token')
		return row[0]

	# Add a user after registration to the database. Adds the keys and the
	# meta information.
	def add_user (self, fitbit_id, key, secret, meta=None):
		# Check if user is already in database
		user_id = self.get_user_id(fitbit_id)
		if user_id:
			q = """UPDATE {0}users
			       SET fitbit_user_key=?, fitbit_user_secret=?
			       WHERE id=?
			    """.format(TABLE_PREFIX)
			self.db.execute(q, ((key, secret, user_id)))
		else:
			q = """INSERT INTO {0}users
			       VALUES(NULL, ?, ?, ?)
			    """.format(TABLE_PREFIX)
			cur = self.db.execute(q, ((fitbit_id, key, secret)))
			user_id = cur.lastrowid

		self.add_meta(user_id, meta)
		self.db.commit()

	# Add or update user meta information to the meta table
	def add_meta (self, user_id, meta):
		if meta is None:
			return

		q = """SELECT *
		       FROM {0}user_meta
		       WHERE user_id=?
		    """.format(TABLE_PREFIX)
		cur = self.db.execute(q, (user_id,))
		row = cur.fetchone()

		if row:
			m = (meta.setdefault('username', row[2]),
				 meta.setdefault('displayName', row[3]),
				 meta.setdefault('nickname', row[4]),
				 meta.setdefault('fullName', row[5]),
				 meta.setdefault('avatar', row[6]),
				 row[0]
				)
			q = """UPDATE {0}user_meta
			       SET username=?, display_name=?, nickname=?,
			       full_name=?, avatar=?
			       WHERE id=?
			    """.format(TABLE_PREFIX)
			self.db.execute(q, m)
		else:
			m = (user_id,
				 meta.setdefault('username'),
				 meta.setdefault('displayName'),
				 meta.setdefault('nickname'),
				 meta.setdefault('fullName'),
				 meta.setdefault('avatar'),
				)
			q = """INSERT INTO {0}user_meta
			       VALUES(NULL, ?, ?, ?, ?, ?, ?)
			    """.format(TABLE_PREFIX)
			self.db.execute(q, m)

		self.db.commit()

	# Get our version of the user id from the id that fitbit uses.
	# Returns None if the user is not in our database.
	def get_user_id (self, fitbit_id):
		q = """SELECT id FROM {0}users
		       WHERE fitbit_id = ?
		    """.format(TABLE_PREFIX)
		cur = self.db.execute(q, (fitbit_id,))
		row = cur.fetchone()
		if row:
			return row[0]
		return None

	# Returns a list of dicts of the keys for all users in our database.
	# ret = {'id': our user id for the user
	#        'fitbit_id': fitbit's id for the user
	#        'key': oauth key
	#        'secret': oauth_secret
	#       }
	def get_users (self):
		q = """SELECT * FROM {0}users
		    """.format(TABLE_PREFIX)
		cur = self.db.execute(q)
		rows = cur.fetchall()
		users = [dict(id=row[0],
				fitbit_id=row[1],
				key=row[2],
				secret=row[3]) for row in rows]
		return users

	# Set a new step value in the database.
	# day = 'yyyy-mm-dd'
	def update_steps (self, user_id, day, steps):
		q = """INSERT OR REPLACE INTO {0}steps
		       VALUES(NULL, ?, ?, ?)
		    """.format(TABLE_PREFIX)
		self.db.execute(q, (user_id, day, steps))
		self.db.commit()

	# Get a week's worth of data from the database
	def get_week (self):
		week = datetime.date.today()-datetime.timedelta(days=7)

		q = """SELECT um.user_id, um.display_name, s.day, s.steps, um.avatar
		       FROM {0}users as u
		       LEFT JOIN {0}steps as s
		       ON u.id = s.user_id
		       LEFT JOIN {0}user_meta as um
		       ON u.id = um.user_id
		       WHERE s.day>?
		       ORDER BY s.day ASC
		""".format(TABLE_PREFIX)
		ret = self.db.execute(q, (week,))
		week_data = ret.fetchall()
		return week_data

	# Returns a dict with all users' meta information
	# {<user_id>: {'username':<uname>, ...}}
	def get_users_meta (self):
		q = """SELECT user_id, username, display_name,
		       nickname, full_name, avatar
		       FROM {0}user_meta
		    """.format(TABLE_PREFIX)
		cur = self.db.execute(q)
		raw = cur.fetchall()
		meta = {}
		for u in raw:
			meta[u[0]] = {'username': u[1],
			              'display_name': u[2],
			              'nickname': u[3],
			              'full_name': u[4],
			              'avatar': u[5]}
		return meta

	def close (self):
		self.db.close()
