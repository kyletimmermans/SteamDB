/*
	Kyle Timmermans
	load.sql
*/

/* Insert Test Data */

INSERT INTO users (uid, username, email, password) VALUES (0, 'user', 'hi@gmail.com', '04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c85b9df8fb');
INSERT INTO users (uid, username, email, password) VALUES (1, 'user1', 'hi1@gmail.com', '0a041b9462caa4a31bac3567e0b6e6fd9100787db2ab433d96f6d178cabfce90');
INSERT INTO users (uid, username, email, password) VALUES (2, 'user2', 'hi2@gmail.com', '6025d18fe48abd45168528f18a82e265dd98d421a7084aa09f61b341703901a3');
INSERT INTO users (uid, username, email, password) VALUES (3, 'user3', 'hi3@gmail.com', '5860faf02b6bc6222ba5aca523560f0e364ccd8b67bee486fe8bf7c01d492ccb');
INSERT INTO users (uid, username, email, password) VALUES (4, 'user4', 'hi4@gmail.com', '5269ef980de47819ba3d14340f4665262c41e933dc92c1a27dd5d01b047ac80e');
INSERT INTO users (uid, username, email, password) VALUES (5, 'user5', 'hi5@gmail.com', '5a39bead318f306939acb1d016647be2e38c6501c58367fdb3e9f52542aa2442');

INSERT INTO users_friend (sender_uid, receiver_uid, sender_username, receiver_username) VALUES (0, 1, 'user', 'user1');
INSERT INTO users_friend (sender_uid, receiver_uid, sender_username, receiver_username) VALUES (4, 0, 'user4', 'user');
INSERT INTO users_friend (sender_uid, receiver_uid, sender_username, receiver_username) VALUES (1, 2, 'user1', 'user2');
INSERT INTO users_friend (sender_uid, receiver_uid, sender_username, receiver_username) VALUES (3, 1, 'user3', 'user1');
INSERT INTO users_friend (sender_uid, receiver_uid, sender_username, receiver_username) VALUES (2, 3, 'user2', 'user3');
INSERT INTO users_friend (sender_uid, receiver_uid, sender_username, receiver_username) VALUES (4, 3, 'user4', 'user3');

INSERT INTO websites (wid, name, url) VALUES (1, 'Bungie Website', 'https://www.bungie.net/');
INSERT INTO websites (wid, name, url) VALUES (2, 'Activision Website', 'https://www.activision.com/');
INSERT INTO websites (wid, name, url) VALUES (3, 'Nintendo Website', 'https://www.nintendo.com/');

INSERT INTO game_dev_companies (cid, name, year_established, wid) VALUES (1, 'Bungie', '1991-01-01 11:00:00', 1);
INSERT INTO game_dev_companies (cid, name, year_established, wid) VALUES (2, 'Activision', '1979-01-01 11:00:00', 2);
INSERT INTO game_dev_companies (cid, name, year_established, wid) VALUES (3, 'Nintendo', '1889-01-01 11:00:00', 3);

INSERT INTO games (gid, name, game_dev_company, genre) VALUES (1, 'Halo', 1, 'FPS');
INSERT INTO games (gid, name, game_dev_company, genre) VALUES (2, 'CoD', 2, 'FPS');
INSERT INTO games (gid, name, game_dev_company, genre) VALUES (3, 'Smash Bros', 3, 'Fighter');

INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES (2, 1, 'Halo');
INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES (2, 3, 'Smash Bros');
INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES (3, 3, 'Smash Bros');
INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES (3, 2, 'CoD');
INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES (4, 1, 'Halo');
INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES (4, 2, 'CoD');
INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES (4, 3, 'Smash Bros');
INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES (1, 1, 'Halo');
INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES (1, 3, 'Smash Bros');

INSERT INTO rate (score, rating_user, rated_game) VALUES (5, 0, 3);
INSERT INTO rate (score, rating_user, rated_game) VALUES (4, 1, 3);
INSERT INTO rate (score, rating_user, rated_game) VALUES (4, 2, 3);
INSERT INTO rate (score, rating_user, rated_game) VALUES (3, 3, 2);
INSERT INTO rate (score, rating_user, rated_game) VALUES (3, 4, 2);
INSERT INTO rate (score, rating_user, rated_game) VALUES (2, 5, 2);
