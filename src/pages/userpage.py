'''
Kyle Timmermans
userpage.py
'''

import os
import time
import psycopg2
import pandas as pd
import streamlit as st
from PIL import Image
from configparser import ConfigParser
from streamlit.components.v1 import html


# Connect to db (from demo.py)
@st.cache
def get_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


# Query db (from demo.py)
@st.cache
def query_db(sql: str):
    db_info = get_config()
    conn = psycopg2.connect(**db_info)
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    conn.commit()
    cur.close()
    conn.close()
    df = pd.DataFrame(data=data, columns=column_names)
    return df


# Insert into db
@st.cache
def insert_db(sql: str):
    db_info = get_config()
    conn = psycopg2.connect(**db_info)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# Set username and uid for future use
# User would only see front end and would not be able to create a temp.txt
# unless they had access to the backend
f = open("temp.txt", "r")
username = f.read()
global_uid = int(query_db(f"SELECT uid FROM users WHERE username = '{username}';")["uid"].tolist()[0])


# For changing pages, no built-in option in Streamlit
# https://github.com/streamlit/streamlit/issues/4832#issuecomment-1201938174
# Modified for urls opening in new tab
def nav_page_external(page_name, timeout_secs=0):
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {
                window.open(page_name, "_blank");
            }
            window.addEventListener("load", function() {
                attempt_nav_page("%s", new Date(), %d);
            });
        </script>
    """ % (page_name, timeout_secs)
    html(nav_script)


def set_friend_list_df(usr):
    friends_data = query_db(f"SELECT DISTINCT username, game_name FROM users as U "
                            f"FULL OUTER JOIN user_inventory AS UI ON UI.owner_id = U.uid "
                            f"WHERE username IN "
                            f"(SELECT sender_username FROM users_friend "
                            f"WHERE receiver_username = '{username}' "
                            f"UNION "
                            f"SELECT receiver_username FROM users_friend "
                            f"WHERE sender_username = '{username}') "
                            f"ORDER BY username;")

    friends_data = friends_data.values.tolist()
    final_data = pd.DataFrame(columns=["Friend", "Game(s) Owned"])
    # Following for-loop logic: Get all games of one friend until we hit the next friend,
    # then do that friend's games, and so on...
   
    # For each list of user and game
    for i in range(len(friends_data)):
        # Until new friend
        temp_friend = friends_data[i][0]
        # For each friend's games
        games = []
        j = i
        while friends_data[j][0] == temp_friend:
            games.append(friends_data[j][1])
            j = j + 1
            # If we get to the end, don't go further
            if j == len(friends_data):
                break
        if temp_friend in final_data.Friend.values:
            continue
        else:
            if games[0] is None:
                final_data.loc[i] = [str(temp_friend), '-']
            else:
                final_data.loc[i] = [str(temp_friend), ', '.join(games)]

    return final_data

st.set_page_config(page_title=f"Home | {username}", page_icon="../assets/favicon.ico", initial_sidebar_state="collapsed", layout="wide")
logo = Image.open('../assets/SteamDB.png')
col4, col5, col6 = st.columns(3, gap='large')
# Refresh Button, Friends List, Send Friend Request
with col4:
    st.markdown(f"<h3 style='text-align: left;'>Refresh Page</h3>", unsafe_allow_html=True)
    with st.form("refresh_page"):
        refresh = st.form_submit_button("Refresh Page!", type="primary", help="Use this button to reflect new queries! "
                                                                              "Not your browser's refresh button.")
        if refresh:
            pass

    st.markdown(f"<h3 style='text-align: left;'>Friends List</h3>", unsafe_allow_html=True)
    with st.form("friends_list"):

        final_data = set_friend_list_df(username)
        friends_table = st.table(final_data)

        hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """

        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        refresh = st.form_submit_button("Refresh Friends List")
        if refresh:
            pass


    st.write("")


    # Don't show ourselves and don't show people we've already friended
    with st.form("add_friends"):
        possible_friends = []
        try:
            get_users = query_db(f"SELECT S.* FROM "
                                 f"(SELECT a.sender_username, COALESCE(COALESCE(A.cnt + B.cnt, A.cnt), A.cnt + B.cnt, B.cnt) AS total "
                                 f"FROM (SELECT sender_username, COUNT(*) AS cnt "
                                    f"FROM users_friend "
                                    f"GROUP BY sender_username) A "
                                 f"FULL OUTER JOIN (SELECT receiver_username, COUNT(*) AS cnt "
                                    f"FROM users_friend "
                                    f"GROUP BY receiver_username) B "
                                 f"ON A.sender_username = B.receiver_username "
                                 f"WHERE a.sender_username != '{username}' "
                                 f"ORDER BY total DESC, a.sender_username) S "
                                 f"WHERE S.sender_username NOT IN "
                                 f"(SELECT sender_username FROM users_friend "
                                 f"WHERE receiver_username = '{username}' "
                                 f"UNION "
                                 f"SELECT receiver_username FROM users_friend "
                                 f"WHERE sender_username = '{username}');")

            for i in range(len(get_users["sender_username"].tolist())):
                possible_friends.append(str(get_users["sender_username"][i]) + " - " + str(get_users["total"][i]) + " friend(s)")
        except:
            # No friends in DB yet
            pass

        try:
            zero_friends = query_db(f"SELECT username FROM users "
                                    f"WHERE username != '{username}' "
                                    f"EXCEPT "
                                    f"SELECT sender_username FROM users_friend "
                                    f"EXCEPT "
                                    f"SELECT receiver_username FROM users_friend "
                                    f"ORDER BY username;")

            for j in range(len(zero_friends["username"].tolist())):
                possible_friends.append(str(zero_friends["username"][j]) + " - 0 friend(s)")
        except:
            pass

        st.markdown(f"<h3 style='text-align: left;'>Add Friends</h3>", unsafe_allow_html=True)
        option = st.selectbox("--Find friends--", tuple(possible_friends), label_visibility="collapsed")
        submitted = st.form_submit_button("Send Friend Request")
        if submitted:
            option = option.split(' ', 1)[0]
            get_uids = query_db(f"SELECT U1.uid AS num1, U2.uid AS num2 "
                                f"FROM users U1, users U2 WHERE U1.username = '{username}' "
                                f"AND U2.username = '{option}';")
            uid_sender, uid_receiver = get_uids["num1"].tolist()[0], get_uids["num2"].tolist()[0]
            insert_db(f"INSERT INTO users_friend (sender_uid, receiver_uid, sender_username, receiver_username) "
                      f"VALUES ('{uid_sender}', '{uid_receiver}', '{username}', '{option}');")
            st.success(f"{option} added as a friend!", icon="🎉")


# Logo, Welcome, Inventory
with col5:
    st.image(logo)
    st.markdown(f"<h1 style='text-align: center;'>Hello, {username}!</h1>", unsafe_allow_html=True)
    st.write("")
    st.markdown(f"<h1 style='text-align: center;'>Inventory</h1>", unsafe_allow_html=True)

    with st.form("inventory"):
        user_inv = query_db(f"SELECT G.name, GC.name, G.genre FROM user_inventory UI "
                            f"JOIN games G ON G.gid = UI.game_id "
                            f"JOIN game_dev_companies GC ON GC.cid = G.game_dev_company "
                            f"WHERE UI.owner_id = {global_uid};")
        user_inv = user_inv.values.tolist()
        final_data = pd.DataFrame(columns=["Game", "Publisher", "Genre"])

        for i in range(len(user_inv)):
            final_data.loc[i] = [str(user_inv[i][0]), str(user_inv[i][1]), str(user_inv[i][2])]

        st.table(final_data)

        game_options = st.selectbox("Select one of your games", final_data)
        action = st.selectbox("Chose an action for selected game", ["Trade", "Rate", "Sell"])
        friends = query_db(f"SELECT username FROM users "
                           f"WHERE username IN "
                           f"(SELECT sender_username FROM users_friend "
                           f"WHERE receiver_username = '{username}' "
                           f"UNION "
                           f"SELECT receiver_username FROM users_friend "
                           f"WHERE sender_username = '{username}') "
                           f"ORDER BY username;")
        friends_options = st.selectbox("Chose a friend to trade with or sell to", friends["username"].tolist())
        friends_game = st.text_input("Type the game you would like to trade for (Case-sensitive)")
        score = st.slider("Rating score", min_value=1, max_value=5, value=1)
        submit = st.form_submit_button("Submit")
        if submit:
            is_game = 1
            fid = int(query_db(f"SELECT uid FROM users WHERE username = '{friends_options}';")["uid"].tolist()[0])
            try:
                gid = int(query_db(f"SELECT gid FROM games WHERE name = '{game_options}';")["gid"].tolist()[0])
            except IndexError: 
                is_game = 0
                st.warning("You have no games to Trade, Rate, or Sell")
            if is_game == 1:
                if action == "Trade":
                    issue, issue_two, issue_three = 0, 0, 0
                    if friends_game == "":
                        st.warning("You must supply the game you would like to trade for")
                        issue = 1
                    if issue != 1:
                        try:
                            friends_gid = int(query_db(f"SELECT gid FROM games WHERE name = '{friends_game}';")["gid"].tolist()[0])
                        except:
                            st.error("Could not find game in friend's inventory, game names are case sensitive")
                            issue_two = 1
                        if issue_two != 1:
                            try:
                                insert_db(f"DELETE FROM user_inventory WHERE owner_id = {global_uid} AND game_id = {gid};")
                                insert_db(f"DELETE FROM user_inventory WHERE owner_id = {fid} AND game_id = {friends_gid};")
                                insert_db(f"INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES ({global_uid}, {friends_gid}, '{friends_game}');")
                                insert_db(f"INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES ({fid}, {gid}, '{game_options}');")
                            except psycopg2.errors.UniqueViolation:
                                st.error("Cannot complete trade as either you or the tradee would duplicate "
                                         "a game you/they already own")
                                issue_three = 1
                    if issue != 1 and issue_two != 1 and issue_three != 1:
                        st.success("Successfully traded selected game with friend!", icon="✅")


                elif action == "Rate":
                    try:
                        insert_db(f"INSERT INTO rate (score, rating_user, rated_game) VALUES ({int(score)}, {global_uid}, {gid});")
                        st.success("Successfully left rating for selected game!", icon="✅")
                    except psycopg2.errors.UniqueViolation:
                        st.warning("You have already rated this game")

                elif action == "Sell":
                    try:
                        insert_db(f"DELETE FROM user_inventory WHERE owner_id = {global_uid} AND game_name = '{game_options}';")
                        insert_db(f"INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES ({fid}, {gid}, '{game_options}');")
                        st.success("Successfully sold selected game!", icon="✅")
                    except psycopg2.errors.UniqueViolation:
                        st.error("Game could not be sold to friend because they already own a copy")


# Marketplace, List of Websites
with col6:
    st.markdown(f"<h3 style='text-align: right;'>Marketplace</h3>", unsafe_allow_html=True)
    with st.form("marketplace"):
        game_scores = query_db("SELECT S.name, COALESCE(ROUND(AVG(S.score)), 0) as score FROM "
                               "(SELECT * FROM rate "
                               "FULL OUTER JOIN games ON gid = rated_game) S "
                               "GROUP BY S.name; ")
        game_scores = game_scores.values.tolist()
        final_data = []
        for i in range(len(game_scores)):
            if int(game_scores[i][1]) == 0:
                final_data.append(f"{game_scores[i][0]} - Not Rated")
            else:   
                final_data.append(f"{game_scores[i][0]} - {int(game_scores[i][1])*u'⭐'}")
        game_list = st.multiselect("Choose games to buy", options=final_data)

        purchase = st.form_submit_button("Purchase")
        if purchase:
            issue = 0
            for i in game_list:
                gname = str(i).split(' -', 1)[0]
                gid = int(query_db(f"SELECT gid FROM games WHERE name = '{gname}';")["gid"].tolist()[0])
                try:
                    insert_db(f"INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES ({global_uid}, {gid}, '{gname}');")
                except psycopg2.errors.UniqueViolation:
                    issue = 1
                    continue
            if issue == 1:
                st.warning("You already own 1 or more of the selected game(s)")
            else:
                st.success("Game(s) added to your inventory!", icon="✅")

    st.write("")

    st.markdown(f"<h3 style='text-align: right;'>Game Dev Websites</h3>", unsafe_allow_html=True)

    hide_iframe = """
            <style>
            iframe {display:none;}
            iframe {visibility: hidden;}
            </style>
    """
    st.markdown(hide_iframe, unsafe_allow_html=True)

    with st.form("game_dev_websites"):

        website_info = query_db("SELECT S1.name, S1.est, S2.mode, S1.url FROM "
                                "(SELECT GC.cid, GC.name, date_part('year', GC.year_established) AS est, W.url "
                                "FROM websites W "
                                "JOIN game_dev_companies GC ON "
                                "W.wid = GC.wid "
                                "JOIN games G ON "
                                "G.game_dev_company = GC.cid) S1 "
                                "JOIN "
                                "(SELECT G.game_dev_company, MODE() WITHIN GROUP (ORDER BY G.genre) "
                                "FROM games G "
                                "JOIN game_dev_companies GC ON G.game_dev_company = GC.cid "
                                "GROUP BY G.game_dev_company) S2 "
                                "ON S1.cid = S2.game_dev_company "
                                "ORDER BY S1.est DESC;")
        website_options = st.radio("Chose a game dev company's website to visit", tuple(website_info["name"].tolist()))
        submit = st.form_submit_button("Visit Website")
        if submit:
            url = 0
            for i in website_info.values.tolist():
                if i[0] == website_options:
                    url = i[3]
            st.success("Opening website in new tab!", icon="✅")
            time.sleep(2)
            nav_page_external(f"{str(url)}")


# Remove extra Streamlit Elements
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)