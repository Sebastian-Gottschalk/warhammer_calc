import numpy as np
from scipy.stats import  multinomial, binom
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import base64

from tools.plot_tools import *
from tools.roll_tools import *
from tools.complete_roll import *
from tools.buttons import *





### STREAMLIT INTERFACE

# st.set_page_config(initial_sidebar_state = "collapsed")
st.set_page_config(
    layout="wide", 
    page_title = "40K Test",
    page_icon = ":space_invader:"
)

if "number_of_weapons" not in st.session_state:
    st.session_state.number_of_weapons = 1

_,minus,middle,plus,_ = st.columns(5)

minus.button(":heavy_minus_sign:", on_click=remove_weapon, disabled= st.session_state.number_of_weapons == 1)
plus.button(":heavy_plus_sign:", on_click=add_weapon)
middle.write(f"Current Nr of weapons: {st.session_state.number_of_weapons}")

all_settings = []

if "names_of_weapons" not in st.session_state:
    st.session_state.names_of_weapons = ["Weapon Nr 1"]


for i in range(st.session_state.number_of_weapons):
    with st.expander(f"{i+1} - {st.session_state.names_of_weapons[i]}"):
        name = st.text_input("Name",value = st.session_state.names_of_weapons[i], key = f"enter_name_{i}")
        if name != st.session_state.names_of_weapons[i]:
            st.session_state.names_of_weapons[i] = name
            st.rerun()

        main_col_1, main_col_2 = st.columns(2)

        _,col_title_1,_ = main_col_1.columns([0.25,1,0.25])


        with col_title_1:
            st.title("Attack Dice")

        _,coll1,_, coll2,_, coll3,_ = main_col_1.columns([0.25,1,0.125,0.75,0.125,1,0.25])


        with coll1:
            num_dice = st.number_input("Dice", min_value=0, value=0, key=f'num_dice_1_{i}')

        with coll2:
            dice_size = int(st.radio("_", ["W3", "W6"], key= f"dice_size_1_{i}", index=1, label_visibility = "hidden")[1])

        with coll3:
            modifier = st.number_input("Modifier", value=3, key=f'modifier_1_{i}', min_value=0)


        start_distr = get_dicesum(num_dice, modifier, dice_size)


        _,col_title_2,_ = main_col_2.columns([0.125,1,0.125])
        with col_title_2:
            st.title("Damage Profile")

        _,colllll1,_, colllll2,_, colllll3,_ = main_col_2.columns([0.25,1,0.125,0.75,0.125,1,0.25])


        with colllll1:
            num_dice = st.number_input("Dice", min_value=0, value=0, key=f'num_dice_2_{i}')

        with colllll2:
            dice_size = int(st.radio("_2", ["W3", "W6"], key=f"dice_size_2_{i}",index=1, label_visibility = "hidden")[1])

        with colllll3:
            modifier = st.number_input("Modifier", value=3, key=f'modifier_2_{i}', min_value=0)



            
        damage_distr = get_dicesum(num_dice, modifier, dice_size)



        co1, co2, co3 = st.columns(3)
        with co1:
            dice_threshhold_1 = st.number_input("Hitting on",2,6,key=f"hitting_on_{i}", value=4)
        with co2:
            dice_threshhold_2 = st.number_input("Wounding on",2,6, value=4, key=f"wounding_on_{i}")
        with co3:
            dice_threshhold_3 = st.number_input("Saving on",2,7, value=4, key = f"saving_on_{i}")
            if dice_threshhold_3==7:
                no_save_roll = True
            else:
                no_save_roll=False
        col1,col2,col3,col4,col5,col6,col7 = st.columns(7)
        reroll = col1.checkbox("Rerolls", key = f"rerolls_{i}")
        reroll_ones_hit = False
        reroll_all_hit = False
        reroll_ones_wound = False
        reroll_all_wound = False
        if reroll:
            rerolls_hit = col1.selectbox("Hit Roll", ["No reroll" , "Reroll 1s", "Reroll all"], key=f"hit_roll_{i}")
            if rerolls_hit == "Reroll 1s":
                reroll_ones_hit = True
            elif rerolls_hit == "Reroll all":
                reroll_all_hit = True
            rerolls_wound = col1.selectbox("Wound Roll", ["No reroll" , "Reroll 1s", "Reroll all"], key=f"wound_roll_{i}")
            if rerolls_wound == "Reroll 1s":
                reroll_ones_wound = True
            elif rerolls_wound == "Reroll all":
                reroll_all_wound = True
        if col2.checkbox("Sustained hits", key = f"sustained_hits_{i}"):
            sustained_hits_nr = col2.number_input("Sustained Hits",1,10,label_visibility="collapsed", key= f"sustained_hits_nr_{i}")
        else:
            sustained_hits_nr = 0
        lethal_hits = col3.checkbox("Lethal Hits", key = f"lethal_hits_{i}")
        dev_wounds = col4.checkbox("Dev Wounds", key = f"dev_wounds_{i}")
        torrent = col5.checkbox("Torrent", key = f"torrent_{i}")

        if torrent: # the combination doesnt make sense and only screws up the plots
            lethal_hits = False

        if col6.checkbox("Crit", key = f"modify_crit_{i}"):
            hit_roll_crit = col6.number_input("Hit roll critting on",dice_threshhold_1,6,value=6, key = f"hit_roll_crit_{i}")
            wound_roll_crit = col6.number_input("Wound roll critting on", dice_threshhold_2,6, value=6, key = f"wound_roll_crit_{i}")
        else:
            hit_roll_crit=6
            wound_roll_crit=6
        if col7.checkbox("Feel No Pain", key = f"feel_no_pain_{i}"):
            feel_no_pain = col7.number_input("Normal FnP",2,7,value=6,label_visibility="collapsed", key = f"normal_fnp_{i}")
            if col7.checkbox("Weird stuff", key= f"weird_stuff_{i}"):
                feel_no_pain_2 = col7.number_input("DevWounds FnP",2,7,value=6,label_visibility="collapsed")
            else:
                feel_no_pain_2 = feel_no_pain
                
        else:
            feel_no_pain = 0
            feel_no_pain_2 = 0
    all_settings.append([
        start_distr,
        dice_threshhold_1,dice_threshhold_2,dice_threshhold_3,
        hit_roll_crit,wound_roll_crit, damage_distr,
        reroll_ones_hit, reroll_all_hit, reroll_ones_wound, reroll_all_wound,
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

for i in range(len(all_settings)):
    start_distr,dice_threshhold_1, dice_threshhold_2, dice_threshhold_3,hit_roll_crit,wound_roll_crit,damage_distr,reroll_ones_hit,reroll_all_hit,reroll_ones_wound,reroll_all_wound,sustained_hits_nr,lethal_hits,dev_wounds,torrent,feel_no_pain, feel_no_pain_2 = all_settings[i]
    current_plot_result = (plot_results and i==len(all_settings)-1) or plot_all_results
    if current_plot_result:
        st.write(f"Result for {st.session_state.names_of_weapons[i]}")
    if np.sum(troops):
        troops = complete_roll(
        start_distr,dice_threshhold_1, dice_threshhold_2, dice_threshhold_3,
        hit_roll_crit,wound_roll_crit,damage_distr,
        reroll_ones_hit,reroll_all_hit,reroll_ones_wound,reroll_all_wound,
        sustained_hits_nr,lethal_hits,dev_wounds,torrent,feel_no_pain, feel_no_pain_2,
        current_plot_result, show_distr, troops
        )
    else:
        complete_roll(
            start_distr,dice_threshhold_1, dice_threshhold_2, dice_threshhold_3,
            hit_roll_crit,wound_roll_crit,damage_distr,
            reroll_ones_hit,reroll_all_hit,reroll_ones_wound,reroll_all_wound,
            sustained_hits_nr,lethal_hits,dev_wounds,torrent,feel_no_pain, feel_no_pain_2,
            current_plot_result, show_distr, troops
        )