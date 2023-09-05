import os
from dotenv import load_dotenv
import streamlit as st
import openai
from typing import List

from openai import OpenAIError, InvalidRequestError
from streamlit_chat import message

load_dotenv(dotenv_path="config.env")
GPT_MODEL = os.getenv("GPT_MODEL")
API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = API_KEY


def get_student_prompt(personality):
    student_prompt_template = f"""
    I want you to act as a 4 grade school student, who ask question about math. 
    At the beginning I want you to introduce yourself then ask questions. 
    Your personality: {personality}, 
    After you got an explanation ask for examples to self study the topic. And then ask tutor is your answers correct. 
    While solving tasks use step-by-step approach, to minimise error probability. 
    In the end finish the conversation.
    """
    return student_prompt_template


ai_roles = {
    "math_tutor": "I want you to act as a math teacher for 4 grade school student. "
    "User will provide some mathematical equations or concepts, "
    "and it will be your job to explain them in easy-to-understand terms. "
    "This could include providing step-by-step instructions for solving a problem, "
    "demonstrating various techniques with visuals or suggesting online resources for further study. "
    "If possible give examples to solve for your student."
    "If user sends you 'QAZ' means that he stacked, ask him, is everything clear"
    "You need to adapt depending on type of student you have.",
    "quick_learn_student": get_student_prompt("you are motivated fast learner student"),
    "slow_learn_student": get_student_prompt(
        "you are struggle with math, often don't get concepts from first try, "
        "so may ask for another approach to explain the topic."
    ),
    "unmotivated_student": get_student_prompt(
        "You are unmotivated student, you don't see point at learning math. "
        "You ask your tutor to motivate you, and if his words convinced you. But you are hard to convince. And question you struggled to answer at school"
    ),
    "unaware_student": "I want you to act as 4 grade child. You have no idea who you are talking with. "
    "You don't have particular questions to conversation partner, but if he introduced himself, you want him to tell you about topic he is professional in",
}


def create_gpt_completion(messages: List[dict]) -> dict:
    completion = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=messages,
    )
    return completion


def show_conversation() -> None:
    if st.session_state.messages:
        st.session_state.messages.append(
            {"role": "user", "content": st.session_state.user_text}
        )
    else:
        st.session_state.messages = [
            {"role": "system", "content": ai_roles["math_tutor"]},
            {"role": "user", "content": st.session_state.user_text},
        ]
    show_gpt_conversation()


def show_gpt_conversation() -> None:
    try:
        completion = create_gpt_completion(st.session_state.messages)
        ai_content = completion.get("choices")[0].get("message").get("content")
        st.session_state.messages.append({"role": "assistant", "content": ai_content})
        if ai_content:
            show_chat(ai_content, st.session_state.user_text)
            st.divider()
    except InvalidRequestError as err:
        if err.code == "context_length_exceeded":
            st.session_state.messages.pop(1)
            if len(st.session_state.messages) == 1:
                st.session_state.user_text = ""
            show_conversation()
        else:
            st.error(err)
    except (OpenAIError, UnboundLocalError) as err:
        st.error(err)


def show_chat(ai_content: str, user_text: str) -> None:
    if ai_content not in st.session_state.generated:
        st.session_state.past.append(user_text)
        st.session_state.generated.append(ai_content)
    if st.session_state.generated:
        for i in range(len(st.session_state.generated)):
            message(st.session_state.past[i], is_user=True, key=f"{i}aa")
            message(st.session_state.generated[i], key=f"{i}bb")
