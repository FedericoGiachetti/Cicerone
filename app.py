import streamlit as st
from core import get_user_data, setup_llm_chain, get_context_data, USER_FILE
import os

st.set_page_config(page_title="Cicerone Milano", layout="centered")
st.title("Cicerone – il tuo local a Milano")

# --- Setup iniziale ---
if "chain" not in st.session_state:
    st.session_state.chain = setup_llm_chain()
if "profile" not in st.session_state:
    name, age, prefs = get_user_data()
    st.session_state.profile = {"name": name, "age": age, "preferences": prefs}
if "context" not in st.session_state:
    w, e, c = get_context_data()
    st.session_state.context = {"weather": w, "events": e, "calendar": c}
if "chat" not in st.session_state:
    st.session_state.chat = []

# --- Mostra messaggi precedenti ---
for m in st.session_state.chat:
    st.chat_message(m["role"]).markdown(m["content"])

# --- Input utente ---
user_input = st.chat_input("Cosa ti va di fare oggi a Milano?")
if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.chat.append({"role": "user", "content": user_input})

    # Recupera info e genera risposta
    prof = st.session_state.profile
    ctx = st.session_state.context
    llm = st.session_state.chain

    res = llm.invoke(
        {
            "input": user_input,
            "weather": ctx["weather"],
            "events": ctx["events"],
            "calendar": ctx["calendar"],
            "preferences": prof["preferences"],
            "name": prof["name"],
            "age": prof["age"],
            "query": user_input
        },
        config={"configurable": {"session_id": "default"}}
    )

    reply = res["text"]
    st.chat_message("assistant").markdown(reply)
    st.session_state.chat.append({"role": "assistant", "content": reply})

# --- Sidebar ---
with st.sidebar:
    st.header("Profilo utente")
    p = st.session_state.profile
    st.write(f"**Nome:** {p['name']}")
    st.write(f"**Età:** {p['age']}")
    st.write(f"**Preferenze:** {p['preferences']}")

    if st.button("Aggiorna contesto"):
        w, e, c = get_context_data()
        st.session_state.context = {"weather": w, "events": e, "calendar": c}
        st.success("Contesto aggiornato!")

    if st.button("Reimposta profilo"):
        if os.path.exists(USER_FILE):
            os.remove(USER_FILE)
            st.session_state.clear()
            st.warning("Profilo reimpostato. Ricarica la pagina.")
