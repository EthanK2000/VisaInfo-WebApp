import streamlit as st
import requests
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import dotenv
import os
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx

dotenv.load_dotenv()

def get_remote_ip() -> str:
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None
        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return None
    except Exception as e:
        return None
    return session_info.request.remote_ip

st.title("VisaInfo.chat")

user_id = "IP-" + get_remote_ip()
client = MongoClient(os.environ['MONGODB_ATLAS_URI'], server_api=ServerApi('1'))
database = client["VisaInfo-Database"]
collection = database["User"]
query_filter = {'user_id': user_id}
user = collection.find_one(query_filter)

if not user:
    user = query_filter
    user["messages"] = [{"role": "assistant", "content": "*🛫 Welcome to VisaInfo.chat*\n\nI'm here to assist you in quickly finding out information about the visa you need.\nWhere do you plan on traveling to?\n\nT&Cs -> https://visainfo.chat/tcs\nFeedback -> https://visainfo.chat/fdb"}]
    collection.insert_one(user)

for msg in user["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="What visa information would you like to know?"):
    user["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    msg = get_remote_ip()
    user["messages"].append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
    collection.replace_one(query_filter,  user)
