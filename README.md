![Version 1.0](https://img.shields.io/badge/Version-v1.0-limegreen.svg)
![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)
![Streamlit 1.16.0](https://img.shields.io/badge/Streamlit-1.16.0-BD4043.svg)
![PostgreSQL 14.5](https://img.shields.io/badge/PostgreSQL-14.5-336791.svg)
![Last Commit](https://img.shields.io/github/last-commit/kyletimmermans/SteamDB?color=success)
[![kyletimmermans Twitter](http://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Follow)](https://twitter.com/kyletimmermans)


<p align="center"><img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/final_title.svg?raw=true" alt="SteamDB Logo"/></p>
SteamDB is a platform for buying, trading, selling, and raring different video games. There is functionality for adding / removing friends and keeping track of what games they have. Once friending another user, you can trade and sell games with / to them, and keep track of the history of your transactions. The UI handles for a number of various user input errors and misuse cases. The point of this project is to better understand SQL, specifically PostgreSQL and SQL injection attacks.

</br></br>

## Installation / Setup
1. cd into top level folder
2. Run `pip install -r requirements.txt`
3. cd into `src` folder
4. Start PostgreSQL and run `psql -U postgres -c 'CREATE DATABASE steamdb;'`
5. Run `psql -U postgres -d steamdb -f schema.sql`
6. Optionally, fill the app w/ test data by running `psql -U postgres -d steamdb -f load.sql`
7. Run `streamlit run login.py --server.headless=true`
8. Open your browser and visit [http://localhost:8501/](http://localhost:8501/)

</br></br>

## Screenshots

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/userpage_1.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/userpage_2.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/userpage_3.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/login_blank.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/login_failed.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/register_blank.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/register_balloons.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/register_special_chars.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/register_failed.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/friend_added.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/removed_friend.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/failed_trade.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/sold_game.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/rated_game.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/register_failed.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/bought_game.png?raw=true" alt="Login Page"/>
</p>

<p align="center">
  <img src="https://github.com/kyletimmermans/SteamDB/blob/main/media/screenshots/register_failed.png?raw=true" alt="Login Page"/>
</p>
