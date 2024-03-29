# pages/register.py


import os
import re
import psycopg2
import hashlib
import pandas as pd
import streamlit as st
from PIL import Image
from configparser import ConfigParser


# set_page_config must be at top of code or Streamlit gets mad
st.set_page_config(page_title="Register", page_icon="assets/favicon.ico", initial_sidebar_state="collapsed")


# Connect to DB
def get_config(filename="database.ini", section="postgresql"):
	parser = ConfigParser()
	parser.read(filename)
	return {k: v for k, v in parser.items(section)}


# Query DB
def query_db(sql: str, data: tuple):
    db_info = get_config()
    conn = psycopg2.connect(**db_info)
    cur = conn.cursor()
    cur.execute(sql, data)
    results = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    conn.commit()
    cur.close()
    conn.close()
    df = pd.DataFrame(data=results, columns=column_names)
    return df


# Insert into DB
def insert_db(sql: str, data: tuple):
	db_info = get_config()
	conn = psycopg2.connect(**db_info)
	cur = conn.cursor()
	cur.execute(sql, data)
	conn.commit()
	cur.close()
	conn.close()


# Create page elements
logo = Image.open('assets/SteamDB.png')
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
	st.image(logo)
	st.subheader("Register")
	email = st.text_input("Email")
	username = st.text_input("Username")
	password = st.text_input("Password", type="password")

	# On Register Account button clicked
	if st.button("Register Account"):
		email_check = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
		if re.fullmatch(email_check, email):
			if any(not c.isalnum() for c in username) == False:
				check = query_db("SELECT uid, username, email FROM users;", (0,))
				# Get next uid in line
				try:
					uid_check = int(check["uid"].tolist()[-1]) + 1
				except IndexError:
					uid_check = 0
				# Ensure no email or username duplicates
				if (email not in check["email"].tolist()) and (username not in check["username"].tolist()):
					hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
					# Add account to users table
					insert_db("INSERT INTO users (uid, username, email, password) "
							  "VALUES (%s, %s, %s, %s);", (uid_check, username, email, hashed_password))
					st.success("Acccount successfully created", icon="✅")
					st.balloons()
				else:
					st.error("Username or Email already used/taken. Please try again.")
			else:
				st.warning("Usernames cannot contain any special characters or whitespace")
		else:
			st.warning("Please use a valid email address")

	st.markdown("""<a href="/login" target = "_self">Login</a>""", unsafe_allow_html=True)

# Remove extra Streamlit Elements
hide_streamlit_style = """
			<style>
			#MainMenu {visibility: hidden;}
			footer {visibility: hidden;}
			</style>
			"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
