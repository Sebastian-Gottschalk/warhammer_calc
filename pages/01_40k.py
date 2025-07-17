import numpy as np
from scipy.stats import  multinomial, binom
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
from roll_tools import *
import base64





### STREAMLIT INTERFACE

# st.set_page_config(initial_sidebar_state = "collapsed")
st.set_page_config(
    layout="wide", 
    page_title = "40K",
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

if feel_no_pain:
    col1, col2,col3,col4, col5= st.columns(5)
else:
    col1, col2,col3,col4= st.columns(4)

### HIT ROLL

with col1:
    if not torrent: 
        hit_roll = roll(start_distr, dice_threshhold_1, reroll_ones=reroll_ones_hit, critting_on=hit_roll_crit, reroll_all=reroll_all_hit)
        hit_roll_hits = get_amount_of_hits(hit_roll, sustained_hits=sustained_hits_nr, crit_auto_hit=lethal_hits)
    else:
        hit_roll_hits = start_distr
    
    hit_roll_plot = get_threshhold_plot(hit_roll_hits)

    if not lethal_hits or torrent:
        fig, ax = plt.subplots()
        ax.bar(range(len(hit_roll_plot)),hit_roll_plot)
        ax.set_xticks(range(0,len(hit_roll_plot)+1,np.max([1,len(hit_roll_plot)//10])))
        ax.set_title("Amount of hits")
        ax.set_ylabel("Density")
        ax2 = ax.twinx()
        ax2.plot(range(len(hit_roll_plot)), np.cumsum(hit_roll_plot), color='blue', marker='o', linestyle='-', label='Probability')
        ax2.set_ylabel('Distribution')
        st.pyplot(fig)
        expected_1 = 0
        for i in range(len(hit_roll_hits)):
            expected_1 += i*hit_roll_hits[i]
        f"Expected nr of hits: {np.round(expected_1,3)}"
    else:
        hits = hit_roll_hits.sum(axis=1)
        crits = hit_roll_hits.sum(axis=0)
        if len(hits)>len(crits):
            crits = np.pad(crits, (0, len(hits)-len(crits)), mode="constant")
        
        [hits_plot, crits_plot] = get_threshhold_plot([hits,crits], multi_list=True)
        
        width = 0.35
        fig, ax = plt.subplots()
        ax.bar(np.arange(len(hits_plot))-width/2,hits_plot,width, label = "Hits", color = "blue")
        ax.bar(np.arange(len(hits_plot))+width/2,crits_plot,width, label = "Crits", color = "red")
        ax.set_xticks(range(0,len(hits_plot)+1,np.max([1,len(hits_plot)//10])))
        ax.set_title("Hit roll")
        ax.set_ylabel("Density")
        ax2 = ax.twinx()
        ax2.plot(range(len(hits_plot)), np.cumsum(hits_plot), color='blue', marker='o', linestyle='-', label='Hits')
        ax2.plot(range(len(crits_plot)), np.cumsum(crits_plot), color='red', marker='o', linestyle='-', label='Crits')
        ax2.set_ylabel('Distribution')
        ax2.set_ylim([0,1])
        ax.legend(loc = "upper left")
        st.pyplot(fig)
        expected_1 = 0
        expected_1_2 = 0
        for i in range(len(hits)):
            expected_1 += i*hits[i]
            expected_1_2 += i*crits[i]
        f"Expected nr of hits / crits: {np.round(expected_1,3)} / {np.round(expected_1_2,3)}"


### WOUND ROLL

with col2:
    if lethal_hits and not torrent:
        if not dev_wounds:
            wound_roll_hits = [0]*(hit_roll_hits.shape[0]+hit_roll_hits.shape[1]-1)
            for i in range(hit_roll_hits.shape[1]):
                wound_roll = roll(hit_roll_hits[:,i], dice_threshhold_2, reroll_ones=reroll_ones_wound, critting_on=wound_roll_crit, reroll_all=reroll_all_wound)
                wound_roll_hits[i:i+hit_roll_hits.shape[0]] += np.array(get_amount_of_hits(wound_roll))
            if not sustained_hits_nr:
                wound_roll_hits=wound_roll_hits[0:hit_roll_hits.shape[0]]
        else: # Devestating wounds + Lethal Hits
            wound_roll_hits = np.zeros((hit_roll_hits.shape[0]+hit_roll_hits.shape[1]-1,hit_roll_hits.shape[0]+hit_roll_hits.shape[1]-1))
            for i in range(hit_roll_hits.shape[1]):
                new_roll = single_roll(i, dice_threshhold_2, reroll_ones=reroll_all_wound, critting_on=wound_roll_crit,reroll_all=reroll_all_wound)
                for k in range(hit_roll_hits.shape[1]):
                    wound_roll_hits[k:k+i+1,0:i+1]+=hit_roll_hits[i,k] * new_roll
        
            
    else:
        wound_roll = roll(hit_roll_hits, dice_threshhold_2, reroll_ones=reroll_ones_wound, critting_on= wound_roll_crit, reroll_all=reroll_all_wound)
        wound_roll_hits = get_amount_of_hits(wound_roll, crit_auto_hit=dev_wounds)

    wound_roll_plot = get_threshhold_plot(wound_roll_hits)

    if not dev_wounds:

        fig, ax = plt.subplots()
        ax.bar(range(len(wound_roll_plot)),wound_roll_plot)
        ax.set_xticks(range(0,len(wound_roll_plot),np.max([1,len(wound_roll_plot)//10])))
        ax.set_title("Wound roll")
        ax.set_ylabel("Density")
        ax2 = ax.twinx()
        ax2.plot(range(len(wound_roll_plot)), np.cumsum(wound_roll_plot), color='blue', marker='o', linestyle='-', label='Probability')
        ax2.set_ylabel('Distribution')
        ax2.set_ylim([0,1])
        col2.pyplot(fig)
        expected_2 = 0
        for i in range(len(wound_roll_hits)):
            expected_2 += i*wound_roll_hits[i]
        f"Expected nr of wounds: {np.round(expected_2,3)}"
    else:
        hits = wound_roll_hits.sum(axis=1)
        crits = wound_roll_hits.sum(axis=0)
        if len(hits)>len(crits):
            crits = np.pad(crits, (0, len(hits)-len(crits)), mode="constant")
        
        [hits_plot, crits_plot] = get_threshhold_plot([hits,crits], multi_list=True)
        
        width = 0.35
        fig, ax = plt.subplots()
        ax.bar(np.arange(len(hits_plot))-width/2,hits_plot,width, label = "Hits", color = "blue")
        ax.bar(np.arange(len(hits_plot))+width/2,crits_plot,width, label = "Crits", color = "red")
        ax.set_xticks(range(0,len(hits_plot)+1,np.max([1,len(hits_plot)//10])))
        ax.set_title("Hit roll")
        ax.set_ylabel("Density")
        ax2 = ax.twinx()
        ax2.plot(range(len(hits_plot)), np.cumsum(hits_plot), color='blue', marker='o', linestyle='-', label='Hits')
        ax2.plot(range(len(crits_plot)), np.cumsum(crits_plot), color='red', marker='o', linestyle='-', label='Crits')
        ax2.set_ylabel('Distribution')
        ax2.set_ylim([0,1])
        ax.legend(loc = "upper left")
        st.pyplot(fig)
        expected_1 = 0
        expected_1_2 = 0
        for i in range(len(hits)):
            expected_1 += i*hits[i]
            expected_1_2 += i*crits[i]
        f"Expected nr of wounds / crits: {np.round(expected_1,3)} / {np.round(expected_1_2,3)}"


### SAVE ROLL
# save roll of 2 (removing a hit on 2+) is equivalent to hitting on 6

with col3:

    if no_save_roll:
        save_roll = wound_roll
        save_roll_hits = wound_roll_hits
    elif dev_wounds:
        save_roll_hits = [0]*(wound_roll_hits.shape[0]+wound_roll_hits.shape[1]-1)
        for i in range(wound_roll_hits.shape[1]):
            save_roll = roll(wound_roll_hits[:,i], 8-dice_threshhold_3)
            save_roll_hits[i:i+wound_roll_hits.shape[0]] += np.array(get_amount_of_hits(save_roll))
        save_roll_hits=save_roll_hits[0:wound_roll_hits.shape[0]]
    else:
        save_roll = roll(wound_roll_hits, 8-dice_threshhold_3)
        save_roll_hits = get_amount_of_hits(save_roll)

    save_roll_plot = get_threshhold_plot(save_roll_hits)

    fig, ax = plt.subplots()
    ax.bar(range(len(save_roll_plot)),save_roll_plot)
    ax.set_xticks(range(0,len(save_roll_plot),np.max([1,len(save_roll_plot)//10])))
    ax.set_title("Save roll")
    ax.set_ylabel("Density")
    ax2 = ax.twinx()
    ax2.plot(range(len(save_roll_plot)), np.cumsum(save_roll_plot), color='blue', marker='o', linestyle='-', label='Probability')
    ax2.set_ylabel('Distribution')
    ax2.set_ylim([0,1])
    col3.pyplot(fig)
    expected_3 = 0
    for i in range(len(save_roll_hits)):
        expected_3 += i*save_roll_hits[i]
    f"Expected nr of failed saves: {np.round(expected_3,3)}"

### DAMAGE ROLL

with col4:
    damage_roll = np.zeros((len(save_roll_hits)-1)*(len(damage_distr)-1)+1)
    damage_distr_cur = np.array([1])
    for i, prob in enumerate(save_roll_hits):
        damage_roll+=np.pad(prob*damage_distr_cur,(0,len(damage_roll)-len(damage_distr_cur)))
        damage_distr_cur = np.convolve(damage_distr_cur,damage_distr)

    damage_roll_plot = get_threshhold_plot(damage_roll)

    fig, ax = plt.subplots()
    ax.bar(range(len(damage_roll_plot)),damage_roll_plot)
    ax.set_xticks(range(0,len(damage_roll_plot),np.max([1,len(damage_roll_plot)//10])))
    ax.set_title("Damage roll")
    ax.set_ylabel("Density")
    ax2 = ax.twinx()
    ax2.plot(range(len(damage_roll_plot)), np.cumsum(damage_roll_plot), color='blue', marker='o', linestyle='-', label='Probability')
    ax2.set_ylabel('Distribution')
    ax2.set_ylim([0,1])
    col4.pyplot(fig)
    expected_4 = 0
    for i in range(len(damage_roll)):
        expected_4 += i*damage_roll[i]
    f"Expected nr of damage: {np.round(expected_4,3)}"

if feel_no_pain:
    with col5:
        damage_fnp = [0]*len(damage_roll)
        prob_fnp = (feel_no_pain-1)/6 # probability that the feel no pain roll missese
        for n in range(len(damage_roll)):
            for k in range(i):
                prob = binom.pmf(k,n,prob_fnp)
                damage_fnp[k]+=prob*damage_roll[n]

        damage_fnp_plot = get_threshhold_plot(damage_fnp)

        fig, ax = plt.subplots()
        ax.bar(range(len(damage_fnp_plot)),damage_fnp_plot)
        ax.set_xticks(range(0,len(damage_fnp_plot),np.max([1,len(damage_fnp_plot)//10])))
        ax.set_title("Feel no Pain roll")
        ax.set_ylabel("Density")
        ax2 = ax.twinx()
        ax2.plot(range(len(damage_fnp_plot)), np.cumsum(damage_fnp_plot), color='blue', marker='o', linestyle='-', label='Probability')
        ax2.set_ylabel('Distribution')
        ax2.set_ylim([0,1])
        col5.pyplot(fig)
        expected_5 = 0
        for i in range(len(damage_fnp)):
            expected_5 += i*damage_fnp[i]
        f"Expected nr of damage after FnP: {np.round(expected_5,3)}"

if show_distr:
    col_distr_1, col_distr_2 = st.columns([1,3])

# TO- DO:
# The dataframe currently has too many columns with 0s when displaying Lethal Hits AND Dev Wounds at the same time

    with col_distr_1:
        data = []
        idx_tuple = []

        idx_tuple += [
                ("Hit", "P(X=x)"),
                ("Hit", "P(X<=x)")
        ]
        if lethal_hits:        
            hits = hit_roll_hits.sum(axis=1)
            crits = hit_roll_hits.sum(axis=0)
            data += [
                hits,
                list(pd.Series(hits).cumsum()),
                crits,
                list(pd.Series(crits).cumsum()),
            ]
            idx_tuple += [
                ("Hit - Crit", "P(X=x)"),
                ("Hit - Crit", "P(X<=x)")
            ]
        else:
            data += [
                hit_roll_hits,
                list(pd.Series(hit_roll_hits).cumsum()),
            ]

        idx_tuple +=[
                ("Wound", "P(X=x)"),
                ("Wound", "P(X<=x)")
        ]
        if dev_wounds:
            hits = wound_roll_hits.sum(axis=1)
            crits = wound_roll_hits.sum(axis=0)
            data += [
                hits,
                list(pd.Series(hits).cumsum()),
                crits,
                list(pd.Series(crits).cumsum()),
            ]
            idx_tuple += [
                ("Wound - Crit", "P(X=x)"),
                ("Wound - Crit", "P(X<=x)")
            ]
        else:
            data +=[
                wound_roll_hits,
                list(pd.Series(wound_roll_hits).cumsum()),
            ]
            
        data +=[
            save_roll_hits,
            list(pd.Series(save_roll_hits).cumsum())
            ]
        idx_tuple += [
            ('Save', 'P(X=x)'),
            ('Save', 'P(X<=x)')
        ]

        index = pd.MultiIndex.from_tuples(idx_tuple)
        st.dataframe(pd.DataFrame(data, index=index))

    with col_distr_2:
        data = [
            damage_roll,
            list(pd.Series(damage_roll).cumsum())
        ]
        index = pd.MultiIndex.from_tuples([
            ('Damage', 'P(X=x)'),
            ('Damage', 'P(X<=x)'),
        ])
        st.dataframe(pd.DataFrame(data, index=index))


#this is easier than commenting it out
def comment_1():
    if st.checkbox("Show cool plotz"):
        colll1, colll2 = st.columns(2)
        with colll1:
            if not torrent: #and not lethal_hits:
                fig = plt.figure()
                ax = fig.add_subplot(111, projection = "3d")
                x = np.arange(hit_roll.shape[1])
                y = np.arange(hit_roll.shape[0])
                X,Y = np.meshgrid(x,y)
                Z = hit_roll
                surf = ax.plot_surface(X, Y, Z, cmap='viridis')
                ax.set_title('Hitroll')
                ax.set_xlabel('Crits')
                ax.set_ylabel('Hits')
                ax.set_zlabel('Value')
                fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
                st.pyplot(fig)
            else:
                st.write("No Hitroll plot when torrent is active")
        with colll2:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection = "3d")
            x = np.arange(wound_roll.shape[1])
            y = np.arange(wound_roll.shape[0])
            X,Y = np.meshgrid(x,y)
            Z = wound_roll
            surf = ax.plot_surface(X, Y, Z, cmap='viridis')
            ax.set_title('Woundroll')
            ax.set_xlabel('Crits')
            ax.set_ylabel('Hits')
            ax.set_zlabel('Value')
            fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
            st.pyplot(fig)
    