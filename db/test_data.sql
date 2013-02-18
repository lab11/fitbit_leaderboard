INSERT INTO users VALUES (NULL, 'user1', 'a', 'b', 'c');
INSERT INTO users VALUES (NULL, 'user2', 'd', 'e', 'f');

INSERT INTO fitbit_steps VALUES (NULL, 1, Date('2012-01-15'), 100);
INSERT INTO fitbit_steps VALUES (NULL, 1, Date('2013-03-15'), 100);

INSERT OR REPLACE INTO fitbit_steps VALUES(NULL, 1, Date('2013-03-15'), 212);
INSERT OR REPLACE INTO fitbit_steps VALUES(NULL, 1, Date('2013-03-16'), 213);
INSERT OR REPLACE INTO fitbit_steps VALUES(NULL, 2, Date('2013-03-12'), 40000);
