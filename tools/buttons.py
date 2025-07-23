import streamlit as st

def add_weapon():
    st.session_state.number_of_weapons +=1

def remove_weapon():
    if st.session_state.number_of_weapons >1:
        st.session_state.number_of_weapons -=1