import streamlit as st
import os

st.set_page_config(
    page_title="Work in Progress",
    page_icon="🐗",
)

st.write("Welcome to the multipage streamlit app. Theres nothing on this page yet.")
st.write("Other pages:")

other_pages = [f for f in os.listdir("pages") if f.endswith('.py')]

cols = st.columns(len(other_pages))

for i,page in enumerate(other_pages):
    page_name = page.split("_")[1].split(".")[0]
    if cols[i].button(page_name, icon = "🐗"):
        st.switch_page(f"pages/{page}")

if st.checkbox("Debug Session state"):
    st.session_state