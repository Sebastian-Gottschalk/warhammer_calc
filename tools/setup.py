import streamlit as st
from tools.wh.tools import Default_weapon

def setup_40k():
    st.set_page_config(
        layout="wide", 
        page_title = "40K",
        page_icon = ":space_invader:"
    )

    st.session_state.wh_number_of_weapons = 1

    default_weapon = [Default_weapon.default_wh_weapon]
    st.session_state.wh_current_settings = default_weapon
    st.session_state.wh_troops = 0
    st.session_state.wh_default_weapon_values = [None]
    st.session_state.wh_saved_weapons = {}
    st.session_state.wh_enabled_weapons = [True]
    st.session_state.wh_names_of_weapons = ["Weapon Nr. 1"]
    st.session_state.wh_current_names_of_weapons = st.session_state.wh_names_of_weapons.copy()
    st.session_state.wh_current_settings_wo_calc = st.session_state.wh_current_settings.copy()