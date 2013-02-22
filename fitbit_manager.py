from datetime import datetime
import fitbit
import oauth2 as oauth
import os
import urllib2

day_converter = {
	0: 'm',
	1: 't',
	2: 'w',
	3: 'th',
	4: 'f',
	5: 's',
	6: 'sun'
}

preffered_img_suffixes = ['_profile_125_square.jpg']

class fitbit_manager:
	def __init__ (self,
	              consumer_key,
	              consumer_secret,
	              callback_url,
	              user_img_location,
	              user_img_web_prefix):
		self.CONSUMER_KEY    = consumer_key
		self.CONSUMER_SECRET = consumer_secret
		self.CALLBACK_URL    = callback_url
		self.IMG_LOC         = user_img_location
		self.IMG_WEB_PREFIX  = user_img_web_prefix

	# Start the process of connecting to fitbit
	def get_auth_url (self, db):
		parameters = {'oauth_callback': self.CALLBACK_URL}
		oa = fitbit.Fitbit(self.CONSUMER_KEY, self.CONSUMER_SECRET)
		req_token = oa.client.fetch_request_token(parameters=parameters)
		db.store_oauth_secret(key=req_token.key, secret=req_token.secret)
		fitbit_auth_url = oa.client.authorize_token_url(req_token)
		return fitbit_auth_url

	# After the user has approved this application to connect to their account
	# run this to add the user to the database
	def add_user (self, db, token, verifier, meta=None):
		oa = fitbit.Fitbit(self.CONSUMER_KEY, self.CONSUMER_SECRET)
		print "next token {0}".format(token)
		secret = db.get_oauth_secret(token)
		request_token = oauth.Token(token, secret)
		user_token = oa.client.fetch_access_token(request_token, verifier)

		u_info = self.get_user_fitbit_info(user_token.key, user_token.secret)
		if 'encodedId' not in u_info:
			printf("Not a valid user info dict")
			return
		fitbit_id = u_info['encodedId']

		u_info['username'] = meta.setdefault('username')
		db.add_user(fitbit_id, user_token.key, user_token.secret, u_info)

		self.update(db, number_of_days=7, fitbit_id=fitbit_id)
		self.cache_images(db)

	# Get the user profile info from fitbit
	def get_user_fitbit_info (self, key, secret):
		try:
			oauth_fitbit = fitbit.Fitbit(self.CONSUMER_KEY,
				                         self.CONSUMER_SECRET,
				                         user_key=key,
				                         user_secret=secret)
			res = oauth_fitbit.user_profile_get()['user']
		except fitbit.exceptions.HTTPUnauthorized as e:
			print "User keys invalid: {0} {1}".format(key, secret)
			res = None

		return res

	# Retreive recent step information from fitbit and insert it into the
	# database.
	def update (self, db, number_of_days=1, fitbit_id=None):
		users = db.get_users()

		for user in users:
			if fitbit_id != None and user['fitbit_id'] != fitbit_id:
				continue
			try:
				oauth_fitbit = fitbit.Fitbit(self.CONSUMER_KEY,
					                         self.CONSUMER_SECRET,
					                         user_key=user['key'],
					                         user_secret=user['secret'])
				res = oauth_fitbit.time_series('activities/steps',
					                       period='{0}d'.format(number_of_days))
				userid = int(user['id'])
				for item in res['activities-steps']:
					day = item['dateTime']
					steps = int(item['value'])

					db.update_steps(userid, day, steps)
			except fitbit.exceptions.HTTPUnauthorized as e:
				print e
			except fitbit.exceptions.HTTPBadRequest as ex:
				print ex

	# Returns the url for the image offset from the root of the application.
	# avatar_url is the fitbit image url passed with the user profile data.
	def get_avatar_relative_url (self, avatar_url):
		avatar_filen = os.path.basename(avatar_url)
		avatar_id    = avatar_filen.split('_')[0]

		img_names = []
		for p in preffered_img_suffixes:
			img_names.append(avatar_id + p)
		img_names.append(avatar_filen)

		img_name = None
		for i in img_names:
			if os.path.isfile(self.IMG_LOC + '/' + i):
				img_name = i
				break

		if img_name:
			return self.IMG_WEB_PREFIX + img_name
		return ""


	# Get a week's worth of data from the database with everyone's step counts.
	def retrieve (self, db):
		week_data = db.get_week()

		users = {}

		for item in week_data:
			username = item[0]
			mdate    = datetime.strptime(item[1], "%Y-%m-%d")
			day      = day_converter[mdate.weekday()]
			steps    = item[2]
			avatar   = self.get_avatar_relative_url(item[3])

			if not username:
				continue

			users.setdefault(username, {})
			users[username].setdefault('total', 0)
			users[username]['total'] += steps
			users[username]['image'] = avatar

			users[username].setdefault('step_counts', [])
			users[username]['step_counts'].append({'day':day, 'steps':steps})

		data = []
		for k,v in users.iteritems():
			data.append({'username': k,
			             'image': v['image'],
				         'total_steps': v['total'],
				         'step_counts': v['step_counts']})

		data = sorted(data, key=lambda user_info: user_info['total_steps'],
			reverse=True)
		return data

	# Query fitbit for information about each user and store it to the meta
	# table
	def update_all_meta (self, db):
		users = db.get_users()

		for user in users:
			meta = self.get_user_fitbit_info(user['key'], user['secret'])
			if meta == None:
				continue
			db.add_meta(user['id'], meta)

	# Locally download all user images. Does not re-download images.
	def cache_images (self, db):
		meta = db.get_users_meta()
		for uid, props in meta.items():

			avatar_url     = props['avatar']
			avatar_url_dir = os.path.dirname(avatar_url)
			avatar_filen   = os.path.basename(avatar_url)
			avatar_id      = avatar_filen.split('_')[0]

			img_names = []
			for p in preffered_img_suffixes:
				img_names.append(avatar_id + p)
			img_names.append(avatar_filen)

			for i in img_names:
				if os.path.isfile(i):
					break

				try:
					u = urllib2.urlopen(avatar_url_dir + '/' + i)
					img = open(self.IMG_LOC + '/' + i, 'w')
					img.write(u.read())
					img.close()
					break
				except:
					pass

