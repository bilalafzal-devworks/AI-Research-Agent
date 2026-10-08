"""
app.py

The Streamlit web page. It collects the topic from the user, calls the
research agent in research_agent.py, and displays the report.

Run locally with:   streamlit run app.py
"""

import os

import streamlit as st
from dotenv import load_dotenv

from research_agent import run_research

# Reads a local .env file (if it exists) and puts its values into environment variables.
# On Streamlit Community Cloud there is no .env file, so this simply does nothing there.
load_dotenv()


def get_groq_api_key():
    """Find the Groq API key.
    - On Streamlit Community Cloud: read it from the app's Secrets.
    - On your computer: read it from the .env file (via os.getenv).
    """
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.getenv("GROQ_API_KEY")


# ----- Page layout -----
st.set_page_config(page_title="AI Research Agent", page_icon="🔎")
st.title("🔎 AI Research Agent")
st.write("Type a topic. The agent will search the web, analyze what it finds, and write a report.")

topic = st.text_input("Research topic", placeholder="e.g. Solar energy adoption in Pakistan in 2026")

# st.button returns True only on the run where the button was clicked.
if st.button("Start research", type="primary"):
    api_key = get_groq_api_key()

    if not topic.strip():
        st.warning("Please enter a topic first.")
    elif not api_key:
        st.error("No GROQ_API_KEY found. Add it to your .env file (local) or Streamlit Secrets (cloud).")
    else:
        # st.spinner shows a loading message while the agent works.
        with st.spinner("The agent is searching and writing. This can take a minute..."):
            try:
                report = run_research(topic.strip(), api_key)
            except Exception as error:
                st.error(f"Something went wrong: {error}")
            else:
                st.success("Report ready!")
                st.markdown(report)
                st.download_button(
                    label="Download report (.md)",
                    data=report,
                    file_name="research_report.md",
                    mime="text/markdown",
                )
