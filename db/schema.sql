PRAGMA foreign_keys = ON;

drop table if exists user;
create table user (
  user_id integer primary key autoincrement,
  username string unique not null,
  fitbit_verifier string not null, 
  fitbit_user_key string not null, 
  fitbit_user_secret string not null
);

drop table if exists fitbit_steps;
create table fitbit_steps (
	pkey integer primary key autoincrement,
	fitbit_user integer,
	steps integer not null, 
	mtime datetime not null,
	foreign key(fitbit_user) references user(user_id)
);