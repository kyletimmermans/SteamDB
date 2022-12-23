# login.py (entrypoint)


import time
import hashlib
import psycopg2
import pandas as pd
import streamlit as st
from PIL import Image
from configparser import ConfigParser
from streamlit.components.v1 import html


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


# For changing pages, no built-in option in Streamlit
# https://github.com/streamlit/streamlit/issues/4832#issuecomment-1201938174
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


# Create page elements
st.set_page_config(page_title="Login", page_icon="assets/favicon.ico", initial_sidebar_state="collapsed")
logo = Image.open('assets/SteamDB.png')
temp = st.empty()
col1, col2, col3 = temp.columns([1, 3, 1])
page_empty = 0
with col2:
    st.image(logo)
    st.subheader("Login")
    username = st.text_input("Username", help="Hint: user, user")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if any(not c.isalnum() for c in username) == False:
            hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            check = query_db(f"SELECT username, password FROM users WHERE username = '{username}' AND password = '{hashed_password}';")
            if check['username'].any():
                st.success("Success! Logging you in now...", icon="✅")
                time.sleep(2)
                page_empty = 1
            else:
                st.error("Username not found or incorrect password. Please try again.")
        else:
            st.warning("Usernames cannot contain any special characters or whitespace")

    st.markdown("""<a href="/register" target = "_self">Create an account</a>""", unsafe_allow_html=True)


# Remove extra Streamlit Elements
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# On correct login
if page_empty == 1:
    # Session state not working between pages
    # User would not be able to see this bc its in the backend
    # They would only have access to the website and not the file system
    f = open("temp.txt", "w")
    f.write(username)
    f.close()
    # Redirect to userpage
    nav_page("userpage")
