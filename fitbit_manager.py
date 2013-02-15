from datetime import datetime
import fitbit

CONSUMER_KEY = '4f0defd304af44e9a6790b0087070313'
CONSUMER_SECRET = '737d767bf5024fda928ea039d77e1098'

day_converter = {
	0: 'm',
	1: 't',
	2: 'w',
	3: 'th',
	4: 'f',
	5: 's',
	6: 'sun'
}

class fitbit_manager:
	def __init__ (self, db):
		self.db = db
		pass

	def update (self, number_of_days=1):
		users = self.db.get_users()

		for user in users:
			try:
				oauth_fitbit = fitbit.Fitbit(CONSUMER_KEY,
					                         CONSUMER_SECRET,
					                         user_key=user['key'],
					                         user_secret=user['secret'])
				res = oauth_fitbit.time_series('activities/steps',
					                           period='{0}d'.format(number_of_days))
				print res
				userid = int(user['id'])
				for item in res['activities-steps']:
					day = item['dateTime']
					steps = int(item['value'])

					self.db.update_steps(userid, day, steps)
			except fitbit.exceptions.HTTPUnauthorized as e:
				print e

	def retrieve (self):
		week_data = self.db.get_week()

		users = {}

		for item in week_data:
			username = item[0]
			mdate    = datetime.strptime(item[1], "%Y-%m-%d")
			day      = day_converter[mdate.weekday()]
			steps    = item[2]

			users.setdefault(username, {})
			users[username].setdefault('total', 0)
			users[username]['total'] += steps

			users[username].setdefault('step_counts', [])
			users[username]['step_counts'].append({'day':day, 'steps':steps})

		print users

		data = []
		for k,v in users.iteritems():
			data.append({'username':k, 'total':v['total'], 'step_counts':v['step_counts']})

		print data

		data = sorted(data, key=lambda user_info: user_info['total'], reverse=True)
		print data





