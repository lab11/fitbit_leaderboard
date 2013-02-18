PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  username           STRING NOT NULL,
  fitbit_verifier    STRING NOT NULL,
  fitbit_user_key    STRING NOT NULL,
  fitbit_user_secret STRING NOT NULL
);
CREATE UNIQUE INDEX fitbit_user ON users(fitbit_verifier, fitbit_user_key, fitbit_user_secret);

DROP TABLE IF EXISTS fitbit_steps;
CREATE TABLE fitbit_steps (
	id      INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL,
	day     DATE NOT NULL,
	steps   INTEGER NOT NULL,
	FOREIGN KEY(user_id) REFERENCES user(id)
);
CREATE UNIQUE INDEX day_steps ON fitbit_steps(user_id, day);

