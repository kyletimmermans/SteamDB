/*
	Kyle Timmermans
	schema.sql
*/


/* Drop ALL tables if they already exist */

DROP TABLE IF EXISTS users, websites, games, game_dev_companies;
DROP TABLE IF EXISTS rate, buy, trade, sell, users_friend, user_inventory;



/* Entities */

CREATE TABLE users (
	uid INTEGER PRIMARY KEY,
	username VARCHAR(32) NOT NULL,
	email VARCHAR(32) NOT NULL,
	password VARCHAR(64) NOT NULL,
	UNIQUE(username, email)
);

CREATE TABLE websites (
	wid INTEGER PRIMARY KEY,
	name VARCHAR(32) NOT NULL,
	url VARCHAR(64)
);

CREATE TABLE games (
	gid INTEGER PRIMARY KEY,
	name VARCHAR(32) NOT NULL,
	game_dev_company INTEGER NOT NULL,
	genre VARCHAR(32),
	UNIQUE(name, genre)
);

CREATE TABLE game_dev_companies (
	cid INTEGER PRIMARY KEY,
	name VARCHAR(32) NOT NULL,
	year_established DATE,
	wid INTEGER NOT NULL,
	FOREIGN KEY (wid) REFERENCES websites (wid)
);



/* Entity Relationships */

CREATE TABLE rate (
	score INTEGER,
	rating_user INTEGER,
	rated_game INTEGER,
	FOREIGN KEY (rating_user) REFERENCES users (uid),
	FOREIGN KEY (rated_game) REFERENCES games (gid),
	PRIMARY KEY(rating_user, rated_game)
);

CREATE TABLE buy (
	buyer_id INTEGER,
	game_id INTEGER,
	purchase_date DATE,
	FOREIGN KEY (buyer_id) REFERENCES users (uid),
	FOREIGN KEY (game_id) REFERENCES games (gid),
	PRIMARY KEY(buyer_id, game_id)
);

CREATE TABLE trade (
	trader_one INTEGER,
	trader_two INTEGER,
	game_one INTEGER,
	game_two INTEGER,
	FOREIGN KEY (trader_one) REFERENCES users (uid),
	FOREIGN KEY (trader_two) REFERENCES users (uid),
	FOREIGN KEY (game_one) REFERENCES games (gid),
	FOREIGN KEY (game_two) REFERENCES games (gid),
	PRIMARY KEY(trader_one, trader_two, game_one, game_two)
);

CREATE TABLE sell (
	seller_id INTEGER,
	buyer_id INTEGER,
	game_id INTEGER,
	FOREIGN KEY (seller_id) REFERENCES users (uid),
	FOREIGN KEY (buyer_id) REFERENCES users (uid),
	FOREIGN KEY (game_id) REFERENCES games (gid),
	PRIMARY KEY(seller_id, buyer_id, game_id)
);

CREATE TABLE users_friend (
	sender_uid INTEGER,
	receiver_uid INTEGER,
	sender_username VARCHAR(32),
	receiver_username VARCHAR(32),
	FOREIGN KEY (sender_uid) REFERENCES users (uid),
	FOREIGN KEY (receiver_uid) REFERENCES users (uid),	
	PRIMARY KEY(sender_uid, receiver_uid) 
);

CREATE TABLE user_inventory (
	owner_id INTEGER,
	game_id INTEGER,
	game_name VARCHAR(32),
	FOREIGN KEY (owner_id) REFERENCES users (uid),
	FOREIGN KEY (game_id) REFERENCES games (gid),
	PRIMARY KEY(owner_id, game_id)
);
