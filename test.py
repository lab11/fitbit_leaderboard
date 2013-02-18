from threading import Timer
import time

from db import fitbit_db
import fitbit_manager

db = fitbit_db.fitbit_db('fitbit.db')
fm = fitbit_manager.fitbit_manager(db)

fm.update(7)
fm.retrieve()

def update_fitbit ():
	while True:
		ufdb = fitbit_db.fitbit_db('fitbit.db')
		uffm = fitbit_manager.fitbit_manager(ufdb)
		uffm.update()
		time.sleep(5)


t = Timer(3, update_fitbit)
t.start()
