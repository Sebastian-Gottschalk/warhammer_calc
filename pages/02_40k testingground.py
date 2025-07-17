import numpy as np
from scipy.stats import  multinomial, binom
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import base64

from tools.plot_tools import *
from tools.roll_tools import *
from tools.complete_roll import *





### STREAMLIT INTERFACE

# st.set_page_config(initial_sidebar_state = "collapsed")
st.set_page_config(
    layout="wide", 
    page_title = "40K Test",
    page_icon = ":space_invader:"
)


_,col_title_1,_ = st.columns([1.25,1,1])


with col_title_1:
    st.title("Attack Dice")

_,coll1, coll2, coll3,_ = st.columns(5)


with coll1:
    num_dice = st.number_input("Dice", min_value=0, value=0, key='num_dice')

with coll2:
    collll1, collll2, collll3 = st.columns([2,3,1])
    with collll2:
        dice_size = rerolls_hit = int(st.radio("", ["W3", "W6"], key= "dice_size", index=1)[1])

with coll3:
    modifier = st.number_input("Modifier", value=3, key='modifier', min_value=0)


start_distr = get_dicesum(num_dice, modifier, dice_size)
_,col_title_2,_ = st.columns([1.15,1,1])
with col_title_2:
    st.title("Damage Profile")

_,colllll1, colllll2, colllll3,_ = st.columns(5)


with colllll1:
    num_dice = st.number_input("", min_value=0, value=0, key='num_dice_2')

with colllll2:
    colllllll1, colllllll2, colllllll3 = st.columns([2,3,1])
    with colllllll2:
        dice_size = rerolls_hit = int(st.radio("", ["W3", "W6"], key="dice_size_2",index=1)[1])

with colllll3:
    modifier = st.number_input("", value=3, key='modifier_2', min_value=0)



    
damage_distr = get_dicesum(num_dice, modifier, dice_size)



co1, co2, co3 = st.columns(3)
with co1:
    dice_threshhold_1 = st.number_input("Hitting on",2,6, value=4)
with co2:
    dice_threshhold_2 = st.number_input("Wounding on",2,6, value=4)
with co3:
    dice_threshhold_3 = st.number_input("Saving on",2,7, value=4)
    if dice_threshhold_3==7:
        no_save_roll = True
    else:
        no_save_roll=False



with st.sidebar:
    
    reroll = st.checkbox("Rerolls")
    reroll_ones_hit = False
    reroll_all_hit = False
    reroll_ones_wound = False
    reroll_all_wound = False
    if reroll:
        reroll_col1, reroll_col2 = st.columns(2)
        with reroll_col1:
            rerolls_hit = st.radio("Hit Roll", ["No reroll" , "Reroll 1s", "Reroll all"])
            if rerolls_hit == "Reroll 1s":
                reroll_ones_hit = True
            elif rerolls_hit == "Reroll all":
                reroll_all_hit = True
        with reroll_col2:
            rerolls_wound = st.radio("Wound Roll", ["No reroll" , "Reroll 1s", "Reroll all"])
            if rerolls_wound == "Reroll 1s":
                reroll_ones_wound = True
            elif rerolls_wound == "Reroll all":
                reroll_all_wound = True
    if st.checkbox("Sustained hits"):
        sustained_hits_nr = st.number_input("Sustained Hits",1,10,label_visibility="collapsed")
    else:
        sustained_hits_nr = 0
    lethal_hits = st.checkbox("Lethal Hits")
    dev_wounds = st.checkbox("Dev Wounds")
    torrent = st.checkbox("Torrent")

    if torrent: # the combination doesnt make sense and only screws up the plots
        lethal_hits = False

    if st.checkbox("Modify Crit threshholds"):
        hit_roll_crit = st.number_input("Hit roll critting on",dice_threshhold_1,6,value=6)
        wound_roll_crit = st.number_input("Wound roll critting on", dice_threshhold_2,6, value=6)
    else:
        hit_roll_crit=6
        wound_roll_crit=6
    if st.checkbox("Feel No Pain"):
        feel_no_pain = st.number_input("",2,6,value=6,label_visibility="collapsed")
    else:
        feel_no_pain = 0

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



complete_roll(
    start_distr,dice_threshhold_1, dice_threshhold_2, dice_threshhold_3,
    hit_roll_crit,wound_roll_crit,damage_distr,
    reroll_ones_hit,reroll_all_hit,reroll_ones_wound,reroll_all_wound,
    sustained_hits_nr,lethal_hits,dev_wounds,torrent,feel_no_pain,
    plot_results, show_distr, troops
)