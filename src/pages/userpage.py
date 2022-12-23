# pages/userpage.py


import os
import time
import psycopg2
import pandas as pd
import streamlit as st
from PIL import Image
from configparser import ConfigParser
from streamlit.components.v1 import html


# Set username and uid for future use
# User would only see front end and would not be able to create a temp.txt
# unless they had access to the backend
f = open("temp.txt", "r")
username = f.read()
# set_page_config must be at top of page or Streamlit gets mad for having more than 1 page config
st.set_page_config(page_title=f"Home | {username}", 
                   page_icon="assets/favicon.ico", 
                   initial_sidebar_state="collapsed", layout="wide")


# Setup CSS styles #

# Remove extra Streamlit Elements
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# Prevent iframe from breaking forms
hide_iframe = """
        <style>
        iframe {display:none;}
        iframe {visibility: hidden;}
        </style>
"""
st.markdown(hide_iframe, unsafe_allow_html=True)
# Hide table index column
hide_table_row_index = """
        <style>
        thead tr th:first-child {display:none}
        tbody th {display:none}
        </style>
"""
st.markdown(hide_table_row_index, unsafe_allow_html=True)


# Connect to db (from demo.py)
def get_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


# Query db (from demo.py)
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
def insert_db(sql: str):
    db_info = get_config()
    conn = psycopg2.connect(**db_info)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()


# Reminder, we need 'parent' here as 'html()' is an iframe and we want the parent document elements
def click_button(btn_type):
    time.sleep(2)
    if btn_type == "friends_list":
        html("""<script type="text/javascript">let e = parent.document.evaluate("//button[contains(.,'Refresh Friends List')]", 
            parent.document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; e.click();</script>""")
    elif btn_type == "inventory":
        html("""<script type="text/javascript">let e = parent.document.evaluate("//button[contains(.,'Refresh Inventory')]", 
            parent.document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue; e.click();</script>""")


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


def nav_page(page_name, timeout_secs=0):
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].href.toLowerCase().endsWith("/" + page_name.toLowerCase())) {
                        links[i].click();
                        return;
                    }
                }
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {
                    setTimeout(attempt_nav_page, 100, page_name, start_time, timeout_secs);
                } else {
                    alert("Unable to navigate to page '" + page_name + "' after " + timeout_secs + " second(s).");
                }
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


def get_inventory(global_id):
    user_inv = query_db(f"SELECT G.name, GC.name, G.genre FROM user_inventory UI "
                        f"JOIN games G ON G.gid = UI.game_id "
                        f"JOIN game_dev_companies GC ON GC.cid = G.game_dev_company "
                        f"WHERE UI.owner_id = {global_id};")
    user_inv = user_inv.values.tolist()
    final_data = pd.DataFrame(columns=["Game", "Publisher", "Genre"])
    for i in range(len(user_inv)):
        final_data.loc[i] = [str(user_inv[i][0]), str(user_inv[i][1]), str(user_inv[i][2])]
    return final_data


def get_friends(usr):
    friends = query_db(f"SELECT username FROM users "
                   f"WHERE username IN "
                   f"(SELECT sender_username FROM users_friend "
                   f"WHERE receiver_username = '{usr}' "
                   f"UNION "
                   f"SELECT receiver_username FROM users_friend "
                   f"WHERE sender_username = '{usr}') "
                   f"ORDER BY username;")
    return friends


# More userpage setup
global_uid = int(query_db(f"SELECT uid FROM users WHERE username = '{username}';")["uid"].tolist()[0])
logo = Image.open('assets/SteamDB.png')
col4, col5, col6 = st.columns(3, gap='large')


# Refresh Button, Friends List, Send Friend Request, Remove Friend, Game Dev Websites
with col4:
    st.markdown(f"<h3 style='text-align: left;'>Friends List</h3>", unsafe_allow_html=True)
    with st.form("friends_list"):

        final_data = set_friend_list_df(username)
        friends_table = st.table(final_data)
        refresh = st.form_submit_button("Refresh Friends List")
        if refresh:
            pass

    st.write("")

    # Don't show ourselves and don't show people we've already friended
    st.markdown(f"<h3 style='text-align: left;'>Add Friends</h3>", unsafe_allow_html=True)
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
            click_button("friends_list")

    st.write("")

    st.markdown(f"<h3 style='text-align: left;'>Remove Friends</h3>", unsafe_allow_html=True)
    with st.form("Remove Friends"):
        friends = get_friends(username)["username"].tolist()
        friend_option = st.selectbox("--Remove friends--", tuple(friends), label_visibility="collapsed")
        submitted = st.form_submit_button("Remove Friend")
        if submitted:
            insert_db(f"DELETE FROM users_friend WHERE (sender_username = '{username}' AND receiver_username = '{friend_option}') "
                      f"OR (sender_username = '{friend_option}' AND receiver_username = '{username}');")
            st.info("Friend removed")
            click_button("friends_list")

    st.write("")

    st.markdown(f"<h3 style='text-align: left;'>Game Dev Websites</h3>", unsafe_allow_html=True)
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
            



# Logo, Welcome {username}, Inventory, Trade, Rate, Sell
with col5:
    st.image(logo)
    st.markdown(f"<h1 style='text-align: center;'>Hello, {username}!</h1>", unsafe_allow_html=True)
    st.write("")

    st.markdown(f"<h3 style='text-align: center;'>Inventory</h3>", unsafe_allow_html=True)
    with st.form("inventory"):
        final_data = get_inventory(global_uid)
        st.table(final_data)
        refresh = st.form_submit_button("Refresh Inventory")
        if refresh:
            pass

    st.markdown(f"<h3 style='text-align: center;'>Trade</h3>", unsafe_allow_html=True)
    with st.form("trade"):
        game_options = st.selectbox("Select one of your games", get_inventory(global_uid))
        friends_options = st.selectbox("Chose a friend to trade with", get_friends(username)["username"].tolist())
        friends_game = st.text_input("Type the game you would like to trade for (Case-sensitive)")
        submit = st.form_submit_button("Trade")
        if submit:
            is_game = True
            fid = int(query_db(f"SELECT uid FROM users WHERE username = '{friends_options}';")["uid"].tolist()[0])
            try:
                gid = int(query_db(f"SELECT gid FROM games WHERE name = '{game_options}';")["gid"].tolist()[0])
            except IndexError: 
                is_game = False
                st.warning("You have no games to trade")
            if is_game is not False:
                issue, issue_two, issue_three = False, False, False
                if friends_game == "":
                    st.warning("You must supply the game you would like to trade for")
                    issue = True
                if issue is not True:
                    try:
                        friends_gid = int(query_db(f"SELECT gid FROM games WHERE name = '{friends_game}';")["gid"].tolist()[0])
                    except:
                        st.error("Could not find game in friend's inventory, game names are case sensitive")
                        issue_two = True
                    if issue_two is not True:
                        try:
                            insert_db(f"DELETE FROM user_inventory WHERE owner_id = {global_uid} AND game_id = {gid};")
                            insert_db(f"DELETE FROM user_inventory WHERE owner_id = {fid} AND game_id = {friends_gid};")
                            insert_db(f"INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES ({global_uid}, {friends_gid}, '{friends_game}');")
                            insert_db(f"INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES ({fid}, {gid}, '{game_options}');")
                            insert_db(f"INSERT INTO trade (trader_one, trader_two, game_one, game_two) VALUES ({global_uid}, {fid}, {gid}, {friends_gid});")
                        except psycopg2.errors.UniqueViolation:
                            st.error("Cannot complete trade as either you or the tradee would duplicate "
                                     "a game you/they already own")
                            issue_three = True
                if issue is not True and issue_two is not True and issue_three is not True:
                    st.success("Successfully traded selected game with friend!", icon="✅")
                    click_button("inventory")

    st.markdown(f"<h3 style='text-align: center;'>Sell</h3>", unsafe_allow_html=True)
    with st.form("sell"):
        game_options = st.selectbox("Select one of your games", get_inventory(global_uid))
        friends_options = st.selectbox("Chose a friend to sell to", get_friends(username)["username"].tolist())
        fid = int(query_db(f"SELECT uid FROM users WHERE username = '{friends_options}';")["uid"].tolist()[0])
        submit = st.form_submit_button("Sell")
        if submit:
            is_game = True
            try:
                gid = int(query_db(f"SELECT gid FROM games WHERE name = '{game_options}';")["gid"].tolist()[0])
            except IndexError: 
                is_game = False
                st.warning("You have no games to sell")
            if is_game is not False:
                try:
                    insert_db(f"DELETE FROM user_inventory WHERE owner_id = {global_uid} AND game_name = '{game_options}';")
                    insert_db(f"INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES ({fid}, {gid}, '{game_options}');")
                    insert_db(f"INSERT INTO sell (game_id, seller_id, buyer_id) VALUES ({gid}, {global_uid}, {fid});")
                    st.success("Successfully sold selected game!", icon="✅")
                    click_button("inventory")
                except psycopg2.errors.UniqueViolation:
                    st.error("Game could not be sold to friend because they already own a copy")

    st.markdown(f"<h3 style='text-align: center;'>Rate</h3>", unsafe_allow_html=True)
    with st.form("rate"):
        game_options = st.selectbox("Select one of your games", get_inventory(global_uid))
        score = st.slider("Rating score", min_value=1, max_value=5, value=1)
        submit = st.form_submit_button("Rate")
        if submit:
            is_game = True
            try:
                gid = int(query_db(f"SELECT gid FROM games WHERE name = '{game_options}';")["gid"].tolist()[0])
            except IndexError: 
                is_game = False
                st.warning("You have no games to rate")
            if is_game is not False:
                try:
                    insert_db(f"INSERT INTO rate (score, rating_user, rated_game) VALUES ({int(score)}, {global_uid}, {gid});")
                    st.success("Successfully left rating for selected game!", icon="✅")
                    click_button("inventory")
                except psycopg2.errors.UniqueViolation:
                    st.warning("You have already rated this game")


# Marketplace, Transaction History, Logout
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
        show_success = 0
        if purchase:
            if game_list:
                issue = 0
                for i in game_list:
                    gname = str(i).split(' -', 1)[0]
                    gid = int(query_db(f"SELECT gid FROM games WHERE name = '{gname}';")["gid"].tolist()[0])
                    try:
                        insert_db(f"INSERT INTO user_inventory (owner_id, game_id, game_name) VALUES ({global_uid}, {gid}, '{gname}');")
                        insert_db(f"INSERT INTO buy (buyer_id, game_id, purchase_date) VALUES ({global_uid}, {gid}, NOW());")
                    except psycopg2.errors.UniqueViolation:
                        issue = 1
                        continue
                if issue == 1:
                    st.warning("You already own 1 or more of the selected game(s)")
                else:
                    st.success("Game(s) added to your inventory!", icon="✅")
                    click_button("inventory")
            else:
                st.warning("You must select a game to purchase")

    st.write("")

    st.markdown(f"<h3 style='text-align: right;'>Transaction History</h3>", unsafe_allow_html=True)
    # This is only the history of the trades and purchases that the current user initiated
    with st.form("history"):
        st.markdown(f"<h5 style='text-align: center;'>Purchases</h5>", unsafe_allow_html=True)
        purchases = pd.DataFrame(columns=["Game", "Purchase Date"])
        purchase_data = query_db(f"SELECT G.name, B.purchase_date FROM buy B "
                                 f"JOIN games G ON G.gid = B.game_id "
                                 f"WHERE buyer_id = {global_uid}")
        for i in range(len(purchase_data)):
            purchases.loc[i] = [str(purchase_data["name"].tolist()[i]), str(purchase_data["purchase_date"].tolist()[i])]
        st.table(purchases)

        st.markdown(f"<h5 style='text-align: center;'>Trades</h5>", unsafe_allow_html=True)
        trades = pd.DataFrame(columns=["Traded With", "Game Traded Away", "Game Traded For"])
        trade_data = query_db(f"SELECT U.username, G.name, G2.name AS name_two FROM trade T "
                              f"JOIN games G ON G.gid = T.game_one "
                              f"JOIN games G2 ON G2.gid = T.game_two "
                              f"JOIN users U ON U.uid = T.trader_two "
                              f"WHERE T.trader_one = {global_uid};")
        for i in range(len(trade_data)):
            trades.loc[i] = [str(trade_data["username"].tolist()[i]), str(trade_data["name"].tolist()[i]), 
                            str(trade_data["name_two"].tolist()[i])]
        st.table(trades)

        st.markdown(f"<h5 style='text-align: center;'>Sales</h5>", unsafe_allow_html=True)
        sales = pd.DataFrame(columns=["Buyer", "Game"])
        sale_data = query_db(f"SELECT U.username, G.name FROM sell S "
                             f"JOIN users U ON U.uid = S.buyer_id "
                             f"JOIN games G ON G.gid = S.game_id "
                             f"WHERE seller_id = {global_uid};")
        for i in range(len(sale_data)):
            sales.loc[i] = [str(sale_data["username"].tolist()[i]), str(sale_data["name"].tolist()[i])]
        st.table(sales)

        action = st.radio("Chose action:", ("Refresh History", "Clear History"))
        submit = st.form_submit_button("Submit")
        if submit:
            if action == "Refresh History":
                pass
            elif action == "Clear History":
                insert_db(f"DELETE FROM buy WHERE buyer_id = {global_uid};")
                insert_db(f"DELETE FROM trade WHERE trader_one = {global_uid};")
                insert_db(f"DELETE FROM sell WHERE seller_id = {global_uid};")
                st.info("Transaction history cleared")
                click_button("inventory")

    st.write("")

    st.markdown(f"<h3 style='text-align: right;'>Logout</h3>", unsafe_allow_html=True)
    logout = st.button("Logout", type="primary")
    if logout:
        try:
            os.remove("temp.txt")
        except:
            st.error("An error occurred while trying to logout. Going back to main page regardless.")
            time.sleep(2)
            nav_page("")
        st.success("Logging out...")
        time.sleep(2)
        nav_page("")


# Put logout button on right side
rightside_button = """
<script type="text/javascript">
    function fix_logout_button() {
        let e = parent.document.evaluate("//button[contains(.,'Logout')]", 
        parent.document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        e.style.float = 'right';
    }
    window.addEventListener("load", fix_logout_button);
</script>
"""
html(rightside_button)
