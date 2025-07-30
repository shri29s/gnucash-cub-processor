import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv(".env")

# --- Init client -----------------------------------------------------------
client = Groq(api_key=os.environ["GROQ_API_KEY"])

# --- Streamlit page setup --------------------------------------------------
st.set_page_config(page_title="ChatGroq Demo", page_icon="🤖")
st.title("💬 Chat with Groq LLMs")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system",
         "content": "You are ChatGroq, a concise assistant."}
    ]

# --- Message input ---------------------------------------------------------
user_msg = st.chat_input("Ask me anything…")
if user_msg:
    st.session_state.messages.append({"role": "user", "content": user_msg})

# --- Display the chat ------------------------------------------------------
for m in st.session_state.messages[1:]:
    st.chat_message(m["role"]).markdown(m["content"])

# --- Call Groq only when the last msg is from user -------------------------
if len(st.session_state.messages) and \
   st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama3-70b-8192",
            stream=True,
            messages=st.session_state.messages,
            temperature=0.5,
            max_completion_tokens=512,
        )
        response = st.empty()
        full = ""
        for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            full += token
            response.markdown(full + "▌")
        response.markdown(full)          # final render
        st.session_state.messages.append(
            {"role": "assistant", "content": full}
        )
