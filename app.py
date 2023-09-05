import json
import time

import pandas as pd

from utils import *


def start_timer():
    time.sleep(300)
    st.session_state.waiting = False
    st.experimental_rerun()


tab1, tab2 = st.tabs(["Math Assistant", "Load Dialog"])

with tab1:
    if "generated" not in st.session_state:
        st.session_state.generated = []
    if "past" not in st.session_state:
        st.session_state.past = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_text" not in st.session_state:
        st.session_state.user_text = ""
    if "waiting" not in st.session_state:
        st.session_state.waiting = True

    """
    # Technical Task  
    ---
    
    ## Who am I? 
    
    
    Hello, I am Math tutor for 10 years children. You can communicate with me like i am real person. My goal is to help 
    you with your math task, and encourage you to study math. 
     
    --- 
    """

    st.session_state.user_text = st.text_input(label="Input your message")

    get_answer_button = st.button("Get answer")
    stop_conversation = st.button("Stop conversation")

    if not stop_conversation:
        if len(st.session_state.past) < 1:
            if st.session_state.user_text:
                if not st.session_state.waiting:
                    st.session_state.user_text = "QAZ"
                show_conversation()
                st.session_state.user_text = ""
                st.session_state.waiting = True
        else:
            if st.session_state.past[-1] != "QAZ":
                if st.session_state.user_text:
                    if not st.session_state.waiting:
                        st.session_state.user_text = "QAZ"
                    show_conversation()
                    st.session_state.user_text = ""
                    st.session_state.waiting = True

                    start_timer()
            else:
                for i in range(len(st.session_state.generated)):
                    message(st.session_state.past[i], is_user=True, key=f"{i}a")
                    message(st.session_state.generated[i], key=f"{i}b")

    st.divider()
    download_chat_button = st.button("Download chat")
    if download_chat_button:
        chat_log = []
        for i in range(len(st.session_state.generated)):
            chat_log.append(
                {
                    "USER": st.session_state.past[i],
                    "TUTOR": st.session_state.generated[i],
                }
            )
        with open("experiments/" + str(time.time()) + ".json", "w") as json_file:
            json.dump(chat_log, json_file)

with tab2:
    uploaded_file = st.file_uploader("Load Dialog file")

    if uploaded_file:
        bytes_data = uploaded_file.read()
        str_data = bytes_data.decode("utf-8")
        dialog_json = pd.read_json(str_data, orient="records")
        for i in range(len(dialog_json)):
            message(dialog_json.iloc[i]["USER"], is_user=True, key=f"{i}a")
            message(dialog_json.iloc[i]["TUTOR"], key=f"{i}b")
