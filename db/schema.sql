PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS fitbit_lb_users;
CREATE TABLE fitbit_lb_users (
	id                 INTEGER PRIMARY KEY AUTOINCREMENT,
	fitbit_id          STRING UNIQUE NOT NULL,
	fitbit_user_key    STRING NOT NULL,
	fitbit_user_secret STRING NOT NULL
);

DROP TABLE IF EXISTS fitbit_lb_fitbit_oauth;
CREATE TABLE fitbit_lb_fitbit_oauth (
	id           INTEGER PRIMARY KEY AUTOINCREMENT,
	oauth_token  STRING NOT NULL,
	oauth_secret STRING NOT NULL,
	time         DATE
);

CREATE TRIGGER fitbit_oauth_time AFTER INSERT ON fitbit_lb_fitbit_oauth
BEGIN
	UPDATE fitbit_lb_fitbit_oauth
	SET time = DATETIME('NOW')
	WHERE id = new.id;
END;

DROP TABLE IF EXISTS fitbit_lb_group_types;
CREATE TABLE fitbit_lb_group_types (
	id            INTEGER PRIMARY KEY AUTOINCREMENT,
	name          STRING NOT NULL
);

DROP TABLE IF EXISTS fitbit_lb_groups;
CREATE TABLE fitbit_lb_groups (
	id            INTEGER PRIMARY KEY AUTOINCREMENT,
	name          STRING NOT NULL,
	parent_id     INTEGER,
	group_type_id INTEGER,
	FOREIGN KEY(group_type_id) REFERENCES fitbit_lb_group_types(id)
);

DROP TABLE IF EXISTS fitbit_lb_user_meta;
CREATE TABLE fitbit_lb_user_meta (
	id             INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id        INTEGER UNIQUE NOT NULL,
	username       STRING,    -- for classification
	display_name   STRING,    -- from fitbit
	nickname       STRING,    -- "
	full_name      STRING,    -- "
	avatar         STRING,    -- "
	FOREIGN KEY(user_id) REFERENCES fitbit_lb_users(id)
);

DROP TABLE IF EXISTS fitbit_lb_user_groups;
CREATE TABLE fitbit_lb_user_groups (
	id       INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id  INTEGER NOT NULL,
	group_id INTEGER NOT NULL,
	FOREIGN KEY(user_id) REFERENCES fitbit_lb_users(id),
	FOREIGN KEY(group_id) REFERENCES fitbit_lb_groups(id)
);

DROP TABLE IF EXISTS fitbit_lb_steps;
CREATE TABLE fitbit_lb_steps (
	id      INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL,
	day     DATE NOT NULL,
	steps   INTEGER NOT NULL,
	FOREIGN KEY(user_id) REFERENCES fitbit_lb_users(id)
);
CREATE UNIQUE INDEX day_steps ON fitbit_lb_steps(user_id, day);

