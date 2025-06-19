import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

@st.cache_resource
def get_mongo_collection():
    client = MongoClient(os.getenv('MONGO_DB_URL_KEY'))
    db=client["milk_app"]
    return db

# --- Session State ---
for key, default in {
    "logged_in": False,
    "user": None,
    "extra_milk": 0,
    "naga": 0,
    "today_milk":0
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Now connect DB only if needed
if "db" not in st.session_state:
    st.session_state["db"] = get_mongo_collection()


# --- Login Page ---
def login():
    st.title("Milk Tracker Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if st.session_state.db["users"].find_one({"user": username,"password":password}):
            st.session_state.logged_in= True
            st.session_state.user = st.session_state.db.milk_log.find_one({"username": username})
            st.session_state.naga = 0
            st.session_state.extra_milk =0 
            st.success(f"Welcome {st.session_state.user['username']}!")
            return
        else:
            st.error("Invalid credentials. Try again.")

def milk_entry():
    today_milk = st.number_input("Enter today's milk (kg)",value=1.5,icon="🔥")
    today_date = datetime.now().strftime("%Y-%m-%d")
    

    if st.button("Submit"):   
        
        if today_milk == 0:
            st.session_state.user['naga'] = 1 + st.session_state.user.get("naga",0)
        else:
            st.session_state.extra_milk = today_milk - 1.5
            st.session_state.user['extra_milk'] = st.session_state.user.get("extra_milk",0) + st.session_state.extra_milk
        
        if today_date not in st.session_state.user.get("milk_log", {}):
            st.session_state.db.milk_log.update_one(
                {"username": st.session_state.user['username']},
                {
                    "$set": {f"milk_log.{today_date}": today_milk},
                    "$inc": {
                        "extra_milk": st.session_state.extra_milk,
                        "naga": st.session_state.naga,
                        "total_days": 1
                    }
                },
                upsert=True
            )
            st.session_state.user = st.session_state.db.milk_log.find_one({"username": st.session_state.user["username"]})

        st.write("Milk entry logged successfully.")

        # # Optionally reset to default
        st.rerun()

    st.write("Extra milk (total) : {}".format(st.session_state.extra_milk))
    st.write("Total nagas : {}".format(st.session_state.naga))
    st.header("🥛 Daily Milk Tracker")
    
    st.subheader("Your milk summary for today")

    st.markdown("### 🔢 Milk Details")
    st.markdown("- **Date:** {}".format(today_date))
    st.markdown("- **Quantity:** `{} kg`".format(today_milk))
    st.markdown("- **Rate:** ₹ 40/litre")
    st.markdown("- **Total:** ₹ `{}`".format(today_milk*40))

    st.caption("Note: Please enter your milk by 10 PM each day.")

   


# --- Main App (after login) ---
def main_app():
    st.title(f"Welcome, {st.session_state.user['username']} 👋")
    st.write("This is the milk management dashboard.")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Milk Entry", "Bill Generator"],index=0)

    if page == "Milk Entry":
        milk_entry()

    if page == "Bill Generator":
        bill_gen()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

def bill_gen():
    st.session_state.user = st.session_state.db.milk_log.find_one({"username": st.session_state.user["username"]})
    st.header("🧾 Monthly Bill Summary")
    st.write()
    total_milk = 1.5*(st.session_state.user['total_days']-st.session_state.user['naga']) + st.session_state.user['extra_milk']
    st.markdown("- **Total Milk:** `{} kg`".format(total_milk))
    st.markdown("- **Extra Milk:** `{}`".format(st.session_state.user['extra_milk']))
    st.markdown("- **Total Nagas:** `{}`".format(st.session_state.user['naga']))
    st.markdown("- **Amount Payable:** ₹ `{}`".format(40*total_milk))
    st.caption("This is an estimated amount. Please verify with the dairy.")

# --- App Flow ---
if st.session_state.logged_in:
    main_app()
else:
    login()
