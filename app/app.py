import streamlit as st
import requests
import dotenv
import os
import time

dotenv.load_dotenv()

st.set_page_config(page_title='VisaInfo.chat', page_icon='app/VisaInfo-chat-logo.png')

st.markdown("""
<style>
    [data-testid="stDecoration"] {
        background-image: none;
        background-color: rgb(255, 189, 69);
    }
    [data-testid="stButtonGroup"] {
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

if 'countryData' not in st.session_state:
    res = requests.get(os.environ["VISAINFO_API_ENDPOINT"]+"getcountries")
    countryData = res.json()
    st.session_state['countryData'] = requests.get(os.environ["VISAINFO_API_ENDPOINT"]+"getcountries").json()

def restart():
    for key in st.session_state.keys():
        del st.session_state[key]

def generate_visa_info():
    st.markdown("""
    <style>
        [data-testid="baseButton-primary"] {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True)
    st.session_state['state'] = 1
    generic_message = f"I am travelling to {st.session_state['destination']} with a {st.session_state['passport']} passport, do I need to get a visa?"
    st.session_state['user']["messages"].append({"role": "user", "content": generic_message})
    print(os.environ["VISAINFO_API_ENDPOINT"]+"queryvisainfo")
    res = requests.post(os.environ["VISAINFO_API_ENDPOINT"]+"queryvisainfo", json = {
        "query": generic_message,
        "destination": st.session_state['destination'],
        "passport": st.session_state['passport'],
        "specific": False,
        "sess_id": st.session_state['user']["user_id"]
    })
    response = res.json()
    st.session_state['user']["messages"].append({"role": "assistant", "content": response["response"], "feedback_id": response["feedback_id"]})

def prompt_visa_info():
    st.session_state['user']["messages"].append({"role": "user", "content": st.session_state['prompt']})
    st.chat_message("user").write(st.session_state['prompt'])
    res = requests.post(os.environ["VISAINFO_API_ENDPOINT"]+"queryvisainfo", json = {
        "query": st.session_state['prompt'],
        "destination": st.session_state['destination'],
        "passport": st.session_state['passport'],
        "specific": True,
        "sess_id": st.session_state['user']["user_id"]
    })
    msg = res.json()["response"]
    st.session_state['user']["messages"].append({"role": "assistant", "content": msg})

if 'user' not in st.session_state:
    st.session_state['user'] = requests.get(os.environ["VISAINFO_API_ENDPOINT"]+"getuser").json()
if 'state' not in st.session_state:
    st.session_state['state'] = 0
if 'prompt' not in st.session_state:
    st.session_state['prompt'] = None

if st.session_state['state'] > 0:
    st.button("Restart", on_click=restart)

for idx, msg in enumerate(st.session_state['user']["messages"]):
    if idx == 0:
        st.chat_message(msg["role"], avatar="app/VisaInfo-chat-logo.png").write(msg["content"])

if st.session_state['state'] == 1:
    st.session_state['prompt'] = st.chat_input(placeholder="Would you like to know anything else?", disabled=False)
    if st.session_state['prompt']:
        prompt_visa_info()

for idx, msg in enumerate(st.session_state['user']["messages"]):
    if idx > 0:
        messages_length = len(st.session_state['user']["messages"])
        if msg["role"] == "assistant":
            if idx < messages_length - 1 or idx == 0:
                st.chat_message(msg["role"], avatar="app/VisaInfo-chat-logo.png").write(msg["content"])
            else:
                if idx == 2:
                    time.sleep(1.69)
                def stream_data():
                    for letter in list(msg["content"]):
                        yield letter
                        time.sleep(0.0069)
                with st.chat_message(msg["role"], avatar="app/VisaInfo-chat-logo.png"):
                    st.write_stream(stream_data)
            if idx == 2:
                @st.fragment
                def thumbs_up():
                    thumbs_up = st.feedback("thumbs")
                    if thumbs_up != None:
                        if thumbs_up:
                            st.toast("Thanks for the positive feedback, we hope VisaInfo.chat has made it easier for you to find your visa!")
                        else:
                            st.toast("Thank you for the negative feedback and actively making VisaInfo.chat more accurate.")
                        requests.post(os.environ["VISAINFO_API_ENDPOINT"]+"feedback", json = {
                            "feedback_id": st.session_state['user']["messages"][idx]["feedback_id"],
                            "thumbs_up": thumbs_up,
                            "sess_id": st.session_state['user']["user_id"]
                        })
                thumbs_up()
        else:
                st.chat_message(msg["role"]).write(msg["content"])

if st.session_state['state'] == 0:
    st.session_state['destination'] = st.selectbox("Destination", index=None, placeholder="Pick a country", options=sorted([entry["country"] for entry in st.session_state['countryData']["countries"]]))
    st.session_state['passport'] = st.selectbox("Passport", index=None, placeholder="Pick a passport", options=sorted([entry["passport"] for entry in st.session_state['countryData']["countries"] if entry["country"] != st.session_state['destination']]))
    if st.session_state['destination'] == None or st.session_state['passport'] == None:
        st.button("Generate Visa Info", on_click=generate_visa_info, disabled=True, type="secondary")
    else:
        st.button("Generate Visa Info", on_click=generate_visa_info, disabled=False, type="primary", key="Generate")
    st.markdown("""
    <style>
        [data-testid="stChatInput"] {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True)
    st.session_state['prompt'] = st.chat_input(placeholder="Would you like to know anything else?", disabled=True)