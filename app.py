import streamlit as st
import datetime
import webbrowser
import pyjokes
import wikipedia
from assistant import listen, speak, ask_ai

st.set_page_config(page_title="AI Assistant", page_icon="🤖")

st.markdown("""
<style>
body {
    background-color: #0e1117;
    color: white;
}
.stButton>button {
    background-color: #1f77b4;
    color: white;
    border-radius: 12px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

st.title("AI Assistant")


if "history" not in st.session_state:
    st.session_state.history = []

if st.button("🎤 Speak"):
    with st.spinner("Listening..."):
        query = listen()

    if query == "none":
        st.warning("Couldn't understand")
    else:
        st.success(f"You said: {query}")

        if 'time' in query:
            response = datetime.datetime.now().strftime("It is %I:%M %p")

        elif 'hello' in query:
            response = "Hello, I am Jarvis"

        elif 'open youtube' in query:
            webbrowser.open("https://youtube.com")
            response = "Opening YouTube"

        elif 'joke' in query:
            response = pyjokes.get_joke()

        elif 'wikipedia' in query:
            search = query.replace("wikipedia", "").strip()
            try:
                response = wikipedia.summary(search, sentences=2)
            except:
                response = "Not found on Wikipedia"

        else:
            response = ask_ai(query)

        st.session_state.history.append(("You", query))
        st.session_state.history.append(("Jarvis", response))

        speak(response)

for role, msg in st.session_state.history:
    st.write(f"**{role}:** {msg}")