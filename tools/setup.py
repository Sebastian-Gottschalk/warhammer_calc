import streamlit as st

from tools.wh.tools import Default_weapon


def setup_40k():
    st.set_page_config(
        layout="wide", 
        page_title = "40K Test",
        page_icon = ":space_invader:"
    )

    st.session_state.wh_number_of_weapons = 1

    default_weapon = [[0,0,0,1],4,4,4,6,6,[0,0,0,1],False,False,False,False,False,False,0,False,False,False,0,0]
    # start_distr = [0,0,0,1],
    # dice_threshhold_1,dice_threshhold_2,dice_threshhold_3 = 4
    # hit_roll_crit,wound_roll_crit = 6 
    # damage_distr = [0,0,0,1]
    # reroll_ones_hit, reroll_all_hit, reroll_fish_hit = False
    # reroll_ones_wound, reroll_all_wound, reroll_fish_wound = False
    # sustained_hits_nr = 0
    # lethal_hits,dev_wounds, torrent = False
    # feel_no_pain,feel_no_pain_2 = 0

    st.session_state.wh_current_settings = [default_weapon]
    st.session_state.wh_calc_weapon = [default_weapon]
    st.session_state.wh_troops = 0
    st.session_state.wh_default_weapon_values = [None]
    st.session_state.wh_saved_weapons = {}



