/* 

SQL queries used in userpage.py

Replace 'user' or '1' when necessary 

*/


-- Get list of friends who've not been friended yet and list by number of friends they have
SELECT S.* FROM
(SELECT a.sender_username, COALESCE(COALESCE(A.cnt + B.cnt, A.cnt), A.cnt + B.cnt, B.cnt) AS total
FROM (SELECT sender_username, COUNT(*) AS cnt
      FROM users_friend 
      GROUP BY sender_username) A
FULL OUTER JOIN (SELECT receiver_username, COUNT(*) AS cnt
      FROM users_friend 
      GROUP BY receiver_username) B 
ON A.sender_username = B.receiver_username
WHERE a.sender_username != 'user'
ORDER BY total DESC, a.sender_username) S
WHERE S.sender_username NOT IN
(SELECT sender_username FROM users_friend
WHERE receiver_username = 'user'
UNION
SELECT receiver_username FROM users_friend
WHERE sender_username = 'user');


-- Get all friends and the games they have
SELECT DISTINCT username, game_name FROM users as U
FULL OUTER JOIN user_inventory AS UI ON UI.owner_id = U.uid
WHERE username IN
(SELECT sender_username FROM users_friend
WHERE receiver_username = 'user'
UNION
SELECT receiver_username FROM users_friend
WHERE sender_username = 'user')
ORDER BY username;


-- Get all games and their ratings
SELECT S.name, COALESCE(ROUND(AVG(S.score)), 0) as score FROM
(SELECT * FROM rate
FULL OUTER JOIN games ON gid = rated_game) S
GROUP BY S.name;


-- Get all current user's owned games and their information
SELECT G.name, GC.name, G.genre FROM user_inventory UI
JOIN games G ON G.gid = UI.game_id
JOIN game_dev_companies GC ON GC.cid = G.game_dev_company
WHERE UI.owner_id = 1;


-- Get all game_devs websites and some of their company info
SELECT S1.name, S1.est, S2.mode, S1.url FROM
(SELECT GC.cid, GC.name, date_part('year', GC.year_established) AS est, W.url
FROM websites W
JOIN game_dev_companies GC ON
W.wid = GC.wid
JOIN games G ON
G.game_dev_company = GC.cid) S1
JOIN 
(SELECT G.game_dev_company, MODE() WITHIN GROUP (ORDER BY G.genre)
FROM games G
JOIN game_dev_companies GC ON G.game_dev_company = GC.cid
GROUP BY G.game_dev_company) S2
ON S1.cid = S2.game_dev_company
ORDER BY S1.est DESC;
