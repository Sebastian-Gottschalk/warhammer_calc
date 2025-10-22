import numpy as np
from scipy.stats import  multinomial, binom
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import base64

from tools.wh.plot_tools import *
from tools.wh.roll_tools import *
from tools.wh.complete_roll import *
from tools.wh.tools import *
from tools.setup import setup_40k





### STREAMLIT INTERFACE


# Setup
if "setup_40k" not in st.session_state:
    setup_40k()
    st.session_state.setup_40k = True

_,minus,middle,plus,col_weapon_load = st.columns(5)

minus.button(":heavy_minus_sign:", on_click=remove_weapon, disabled= st.session_state.wh_number_of_weapons == 1)
weapon_to_load = col_weapon_load.selectbox("Select Weapon to add", options = ["default"] + list(st.session_state.wh_saved_weapons.keys()))
plus.button(":heavy_plus_sign:", on_click=add_weapon, args = [weapon_to_load])
middle.write(f"Current Nr of weapons: {st.session_state.wh_number_of_weapons}")


all_settings = []

if "wh_names_of_weapons" not in st.session_state:
    st.session_state.wh_names_of_weapons = ["Weapon Nr 1"]


for i in range(st.session_state.wh_number_of_weapons):
    if st.session_state.wh_default_weapon_values[i]:
        default_values = st.session_state.wh_default_weapon_values[i]
    else:
        default_values = Default_weapon.default_wh_weapon
    
    with st.expander(f"{i+1} - {st.session_state.wh_names_of_weapons[i]}"):
        left,_, col_save = st.columns([7,1,1])
        name = left.text_input("Name",value = st.session_state.wh_names_of_weapons[i], key = f"enter_name_{i}")
        if name != st.session_state.wh_names_of_weapons[i]:
            st.session_state.wh_names_of_weapons[i] = name
            st.rerun()

        main_col_1, main_col_2 = st.columns(2)

        _,col_title_1,_ = main_col_1.columns([0.25,1,0.25])


        with col_title_1:
            st.title("Attack Dice")

        _,coll1,_, coll2,_, coll3,_ = main_col_1.columns([0.25,1,0.125,0.75,0.125,1,0.25])


        with coll1:
            num_dice_att = st.number_input("Dice", min_value=0, value=default_values["num_dice_att"], key=f'num_dice_1_{i}')

        with coll2:
            dice_size_att = int(st.radio("_", ["W3", "W6"], key= f"dice_size_1_{i}", label_visibility = "hidden", index = default_values["dice_size_att"])[1])

        with coll3:
            modifier_att = st.number_input("Modifier", value=default_values["modifier_att"], key=f'modifier_1_{i}', min_value=0)


        start_distr = get_dicesum(num_dice_att, modifier_att, dice_size_att)


        _,col_title_2,_ = main_col_2.columns([0.125,1,0.125])
        with col_title_2:
            st.title("Damage Profile")

        _,colllll1,_, colllll2,_, colllll3,_ = main_col_2.columns([0.25,1,0.125,0.75,0.125,1,0.25])


        with colllll1:
            num_dice_dmg = st.number_input("Dice", min_value=0, value=default_values["num_dice_dmg"], key=f'num_dice_2_{i}')

        with colllll2:
            dice_size_dmg = int(st.radio("_2", ["W3", "W6"], key=f"dice_size_2_{i}",index=default_values["dice_size_dmg"], label_visibility = "hidden")[1])

        with colllll3:
            modifier_dmg = st.number_input("Modifier", value=default_values["modifier_dmg"], key=f'modifier_2_{i}', min_value=0)



            
        damage_distr = get_dicesum(num_dice_dmg, modifier_dmg, dice_size_dmg)



        co1, co2, co3 = st.columns(3)
        with co1:
            dice_threshhold_1 = st.number_input("Hitting on",2,6,key=f"hitting_on_{i}", value=default_values["dice_threshhold_1"])
        with co2:
            dice_threshhold_2 = st.number_input("Wounding on",2,6, value=default_values["dice_threshhold_2"], key=f"wounding_on_{i}")
        with co3:
            dice_threshhold_3 = st.number_input("Saving on",2,7, value=default_values["dice_threshhold_3"], key = f"saving_on_{i}")
            if dice_threshhold_3==7:
                no_save_roll = True
            else:
                no_save_roll=False
        col1,col2,col3,col4,col5,col6,col7 = st.columns(7)
        reroll = col1.checkbox("Rerolls", key = f"rerolls_{i}", value = default_values["reroll"])
        reroll_ones_hit = False
        reroll_all_hit = False
        reroll_fish_hit = False
        reroll_ones_wound = False
        reroll_all_wound = False
        reroll_fish_wound = False
        if reroll:
            rerolls_hit = col1.selectbox("Hit Roll", ["No reroll" , "Reroll 1s", "Reroll all","Fish for crits"], key=f"hit_roll_{i}", index=default_values["reroll_hit"])
            if rerolls_hit == "Reroll 1s":
                reroll_ones_hit = True
            elif rerolls_hit == "Reroll all":
                reroll_all_hit = True
            elif rerolls_hit == "Fish for crits":
                reroll_fish_hit = True
            rerolls_wound = col1.selectbox("Wound Roll", ["No reroll" , "Reroll 1s", "Reroll all","Fish for crits"], key=f"wound_roll_{i}", index = default_values["reroll_wound"])
            if rerolls_wound == "Reroll 1s":
                reroll_ones_wound = True
            elif rerolls_wound == "Reroll all":
                reroll_all_wound = True
            elif rerolls_wound == "Fish for crits":
                reroll_fish_wound = True
        else:
            rerolls_hit = "No reroll" # for saving a weapon
            rerolls_wound = "No reroll"
        sustained_hits = col2.checkbox("Sustained hits", key = f"sustained_hits_{i}", value = default_values["sustained_hits"])
        if sustained_hits:
            sustained_hits_nr = col2.number_input("Sustained Hits",1,10,label_visibility="collapsed", key= f"sustained_hits_nr_{i}", value = default_values["sustained_hits_nr"])
        else:
            sustained_hits_nr = 0
        lethal_hits = col3.checkbox("Lethal Hits", key = f"lethal_hits_{i}", value = default_values["lethal_hits"])
        dev_wounds = col4.checkbox("Dev Wounds", key = f"dev_wounds_{i}", value = default_values["dev_wounds"])
        torrent = col5.checkbox("Torrent", key = f"torrent_{i}", value = default_values["torrent"])

        if torrent: # the combination doesnt make sense and only screws up the plots
            lethal_hits = False

        crit_modifier= col6.checkbox("Crit Modifier", key = f"modify_crit_{i}", value = default_values["crit_modifier"])
        if crit_modifier:
            hit_roll_crit = col6.number_input("Hit roll critting on",dice_threshhold_1,6,value=default_values["hit_roll_crit"], key = f"hit_roll_crit_{i}")
            wound_roll_crit = col6.number_input("Wound roll critting on", dice_threshhold_2,6, value=default_values["wound_roll_crit"], key = f"wound_roll_crit_{i}")
        else:
            hit_roll_crit=6
            wound_roll_crit=6
        fnp_checkbox =  col7.checkbox("Feel No Pain", key = f"feel_no_pain_{i}", value = default_values["feel_no_pain"])
        if fnp_checkbox:
            feel_no_pain = col7.number_input("Normal FnP",2,7,value=default_values["feel_no_pain_1"],label_visibility="collapsed", key = f"normal_fnp_{i}")
            fnp_checkbox_mortals = col7.checkbox("Different FnP on Mortals", key= f"weird_stuff_{i}", value = default_values["fnp_checkbox_mortals"])
            if fnp_checkbox_mortals:
                feel_no_pain_2 = col7.number_input("DevWounds FnP",2,7,value=default_values["feel_no_pain_2"],label_visibility="collapsed")
            else:
                feel_no_pain_2 = feel_no_pain
                
        else:
            feel_no_pain = 0
            feel_no_pain_2 = 0
            fnp_checkbox_mortals = False

        save_weapon_settings = {
            "num_dice_att":num_dice_att,
            "dice_size_att":[3,6].index(dice_size_att),
            "modifier_att":modifier_att,
            "num_dice_dmg":num_dice_dmg,
            "dice_size_dmg":[3,6].index(dice_size_dmg),
            "modifier_dmg":modifier_dmg,
            "dice_threshhold_1":dice_threshhold_1,
            "dice_threshhold_2":dice_threshhold_2,
            "dice_threshhold_3":dice_threshhold_3,
            "reroll":reroll,
            "reroll_hit":["No reroll" , "Reroll 1s", "Reroll all","Fish for crits"].index(rerolls_hit),
            "reroll_wound":["No reroll" , "Reroll 1s", "Reroll all","Fish for crits"].index(rerolls_wound),
            "sustained_hits":sustained_hits,
            "sustained_hits_nr":sustained_hits_nr,
            "lethal_hits":lethal_hits,
            "dev_wounds":dev_wounds,
            "torrent": torrent,
            "crit_modifier":crit_modifier,
            "hit_roll_crit": hit_roll_crit,
            "wound_roll_crit": wound_roll_crit,
            "feel_no_pain": fnp_checkbox,
            "feel_no_pain_1": feel_no_pain,
            "fnp_checkbox_mortals": fnp_checkbox_mortals,
            "feel_no_pain_2": feel_no_pain_2
        }
        col_save.button("Save Weapon", on_click = save_weapon, args = [name, save_weapon_settings], key=f"save_button_{i}")
    all_settings.append([
        start_distr,
        dice_threshhold_1,dice_threshhold_2,dice_threshhold_3,
        hit_roll_crit,wound_roll_crit, damage_distr,
        reroll_ones_hit, reroll_all_hit, reroll_fish_hit, 
        reroll_ones_wound, reroll_all_wound, reroll_fish_wound,
        sustained_hits_nr, lethal_hits,dev_wounds, torrent,
        feel_no_pain,feel_no_pain_2
    ])


with st.sidebar:

    fight_troop = st.checkbox("Shoot on dudes")

    if fight_troop:
        co1, co2 = st.columns(2)
        with co1:
            amount_of_troops = st.number_input("Units",1,100,value=10)
        with co2:
            wounds_per_troop = st.number_input("Wounds",1,20,value=3)
        troops = np.zeros((wounds_per_troop+1,amount_of_troops))
        troops[wounds_per_troop,0] = 1
    else:
        troops = 0

    
    plot_results = st.checkbox("Plot Results", value = True)
    if plot_results:
        plot_all_results = st.checkbox("Plot all results")

    show_distr = st.checkbox("Show distribution")

    st.write("")
    st.write("")
    show_kroot = st.radio("show_kroot",["Kroot, das ist kroot", "Halp, im a tiny space marine and scared of pictures"],label_visibility="collapsed")
    if show_kroot == "Kroot, das ist kroot":
        show_kroot = True
    else:
        show_kroot = False
    st.write("Additional ressources:")
    st.page_link("http://wahapedia.ru/", label = "Wahapedia")
    st.page_link("https://www.amazon.de/My-First-Math-Book-Introduction/dp/197596490X", label = "Help, I dont know math")
    st.page_link("https://www.linkedin.com/in/josua-keil-10546a311/", label = "Show me some Orc pictures")

    if show_kroot:
        side_bg = "img/kroot.png"
        side_bg_ext = "png"
        with open(side_bg, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <style>
            [data-testid="stSidebar"] > div:first-child {{
                background: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), 
                        url(data:image/{side_bg_ext};base64,{encoded_string});
                background-size : contain;
                background-repeat: no-repeat;
                background-position: center 75%;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

if show_kroot:
    side_bg = "img/kroot_2.png"
    side_bg_ext = "png"
    with open(side_bg, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), 
                    url(data:image/{side_bg_ext};base64,{encoded_string});
            background-size : 70%;
            background-repeat: no-repeat;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


if sustained_hits_nr>=2 and lethal_hits and dev_wounds:
    st.write("The plots and future calculations are wrong. To-do: fix")

_,middle,_ = st.columns([3,1,3])
if middle.button("Calculate"):
    st.session_state.wh_current_settings = all_settings
    st.session_state.wh_troops = troops
    st.session_state.wh_current_troops = [troops]

for i in range(len(st.session_state.wh_current_settings)):
    start_distr,dice_threshhold_1, dice_threshhold_2, dice_threshhold_3,hit_roll_crit,wound_roll_crit,damage_distr,reroll_ones_hit,reroll_all_hit,reroll_fish_hit,reroll_ones_wound,reroll_all_wound,reroll_fish_wound,sustained_hits_nr,lethal_hits,dev_wounds,torrent,feel_no_pain, feel_no_pain_2 = st.session_state.wh_current_settings[i]
    current_plot_result = (plot_results and i==len(st.session_state.wh_current_settings)-1) or plot_all_results
    if current_plot_result:
        st.write(f"Result for {st.session_state.wh_names_of_weapons[i]}")
    if np.sum(st.session_state.wh_troops):
        new_troops = complete_roll(
        start_distr,dice_threshhold_1, dice_threshhold_2, dice_threshhold_3,
        hit_roll_crit,wound_roll_crit,damage_distr,
        reroll_ones_hit,reroll_all_hit,reroll_fish_hit,
        reroll_ones_wound,reroll_all_wound,reroll_fish_wound,
        sustained_hits_nr,lethal_hits,dev_wounds,torrent,feel_no_pain, feel_no_pain_2,
        current_plot_result, show_distr, st.session_state.wh_current_troops[i]
        )
        if len(st.session_state.wh_current_troops) < len(st.session_state.wh_current_settings):
            st.session_state.wh_current_troops.append(new_troops)
    else:        
        complete_roll(
            start_distr,dice_threshhold_1, dice_threshhold_2, dice_threshhold_3,
            hit_roll_crit,wound_roll_crit,damage_distr,
            reroll_ones_hit,reroll_all_hit,reroll_fish_hit,
            reroll_ones_wound,reroll_all_wound,reroll_fish_wound,
            sustained_hits_nr,lethal_hits,dev_wounds,torrent,feel_no_pain, feel_no_pain_2,
            current_plot_result, show_distr, st.session_state.wh_troops
        )