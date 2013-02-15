

import db.fitbit_db
import fitbit_manager

db = db.fitbit_db.fitbit_db('fitbit.db')
fm = fitbit_manager.fitbit_manager(db)

fm.update()
fm.retrieve()
