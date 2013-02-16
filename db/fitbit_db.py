import sqlite3
from datetime import date, timedelta



class fitbit_db:

	def __init__ (self, db_name):
		self.db_name = db_name
		self.db      = sqlite3.connect(db_name)

	def add_user (self, username, verify_str, user_key, user_secret):
		user = ((username, verify_str, user_key, user_secret))
		self.db.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?)", user)

	def get_users (self):
		cur = self.db.execute("SELECT * FROM users")
		rows = cur.fetchall()
		users = [dict(id=row[0],
				name=row[1],
				key=row[3],
				secret=row[4]) for row in rows]
		print users
		return users


	def update_steps (self, user_id, day, steps):
		update_str = """ INSERT OR REPLACE INTO fitbit_steps
		                 VALUES(NULL, ?, ?, ?)"""
		self.db.execute(update_str, (user_id, day, steps))
		self.db.commit()

	def get_week (self):
		week = date.today()-timedelta(days=7)
		print week

		q = """SELECT users.username, fitbit_steps.day, fitbit_steps.steps
		       FROM users
		       LEFT JOIN fitbit_steps
		       ON users.id = fitbit_steps.user_id
		       WHERE fitbit_steps.day>'{0}'
		       ORDER BY day DESC
		""".format(week)
		ret = self.db.execute(q)
		week_data = ret.fetchall()
		print week_data

		return week_data

	def close (self):
		self.db.close()
