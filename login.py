import streamlit as st
import streamlit_authenticator as stauth
from pathlib import Path
import pickle


st.set_page_config(page_title="Multipage Scanner", page_icon=":bar_chart:", layout="wide")

# --- USER AUTHENTICATION ---
names = ["CKST", "admin"]
usernames = ["CKST", "admin"]

file_path = Path(__file__).parent/"hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,"Scanner", "ttyyuu", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("login","sidebar")

if authentication_status == False:
    st.error("Username/Password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status == True:
    st.write("You have made it!!!")

authenticator.logout("Logout","sidebar")