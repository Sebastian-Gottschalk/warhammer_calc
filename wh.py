import numpy as np
from scipy.stats import  multinomial
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D

@st.cache_data
def single_roll(n, thresh, reroll_ones = False):
    '''
    calculates the distribution of a single roll with n dice, with everything >= thresh being a sucess and every 6 being a crit
    the resulting matrix has the form
    [p_00 p_01 p_02...
     p_10 p_11 p_12...
     ... 
    ]
    where p_ij is the probability of i hits and j crits
    (where of course p_ij = 0 if i+j>n)
    '''
    results = np.zeros((n+1,n+1))
    p_crit = 1/6
    p_hit = (6-thresh)/6
    if not reroll_ones:
        p = [p_hit,p_crit,1-p_hit-p_crit]
        for i in range(n+1):
            for j in range(n+1-i):
                if i+j<=n:
                    results[i,j] = multinomial.pmf([i,j,n-i-j], n=n, p=p)
    else:
        # Get the probability distribution after the first roll
        results_roll_1 = np.zeros((n+1,n+1,n+1))
        p_one = 1/6
        p = [p_one, p_hit, p_crit, 1-p_hit-p_one-p_crit]
        for i in range(n+1): #ones
            for j in range(n+1): #hits
                for l in range(n+1): #crits
                    if i+j+l<=n:
                        results_roll_1[i,j,l] = multinomial.pmf([i,j,l,n-i-j-l], n=n, p=p)
        
        # Use the first distribution to reroll ones
        for i in range(n+1): #ones
            new_roll = single_roll(i,thresh)
            for j in range(n+1): #hits
                for l in range(n+1): #crits
                    if i+j+l<=n:
                        results[j:j+i+1, l:l+i+1] += results_roll_1[i,j,l]*new_roll
    return results

@st.cache_data
def roll(distr, thresh, reroll_ones = False):
    '''
    distr is a list e.g. [0.25,0.5,0.25] meaning
    25% chance of n=0
    50% chance of n=1
    25% chance of n=2
    For each possible n-value we calculate the probability distribution of a roll with n dice, padding the result to a uniform size and taking the weighted average of all of them
    using the values from distr as weights
    '''
    max_n = len(distr)
    resulting_distr = np.zeros((max_n,max_n))
    for n, prob in enumerate(distr):
        n_distr = single_roll(n,thresh, reroll_ones)
        n_distr = np.pad(n_distr,(0,max_n-n-1), mode="constant", constant_values=0)
        resulting_distr += prob * n_distr
    return resulting_distr

@st.cache_data
def get_amount_of_hits(distr, sustained_hits = 0):
    '''
    calculates a 1-d distribution of the amount of successes given the matrix of hits and crits
    here hits and crits are treated the same, so no extra rules implemented yet
    '''
    n = distr.shape[0]
    if not sustained_hits:
        resulting_distr = [0]*n
        for i in range(n):
            for j in range(i+1):
                resulting_distr[i] += distr[j,i-j]
    else:
        resulting_distr = [0]*((n-1)*(1+sustained_hits)+1)
        for i in range(n):
            for j in range(n):
                if i+j<=n-1:
                    resulting_distr[i+(sustained_hits+1)*j] += distr[i,j]
    return resulting_distr

def get_dicesum(nr_dice, bias, dice_size):
    single_die = np.ones(dice_size) / dice_size
    distr = single_die
    for _ in range(nr_dice-1):
        distr = np.convolve(distr, single_die)
    possible_sum = np.arange(nr_dice + bias, dice_size*nr_dice+bias+1)
    resulting_distr = [0]*(dice_size*nr_dice+bias+1)
    for i in possible_sum:
        resulting_distr[i] = distr[i-min(possible_sum)]
    return resulting_distr



### STREAMLIT INTERFACE

st.set_page_config(initial_sidebar_state = "collapsed")
if st.checkbox("Additional stuff:"):
    coll1, coll2, coll3 = st.columns(3)
    with coll1:
        num_dice = st.number_input("Dice", min_value=1, value=5, key='num_dice')

    with coll2:
        dice_size = st.number_input("Dice Size", value = 6, min_value=2)

    with coll3:
        modifier = st.number_input("Modifier", value=3, key='modifier', min_value=0)
    
    start_distr = get_dicesum(num_dice, modifier, dice_size)
else:
    num_dice = st.number_input("Amount of dices used",1,100, value=5)
    start_distr = [0]*num_dice + [1]

co1, co2, co3 = st.columns(3)
with co1:
    dice_threshhold_1 = st.number_input("Hitting on",2,6, value=4)
with co2:
    dice_threshhold_2 = st.number_input("Wounding on",2,6, value=4)
with co3:
    dice_threshhold_3 = st.number_input("Saving on",2,6, value=4)

with st.sidebar:
    reroll_ones = st.checkbox("Reroll ones")
    if reroll_ones:
        reroll_ones_hit = st.checkbox("Hitroll")
        reroll_ones_wound = st.checkbox("Wound")
    else:
        reroll_ones_hit = False
        reroll_ones_wound = False
    sustained_hits_nr = st.number_input("Sustained Hits",0,10)
    lethal_hits = st.checkbox("Lethal Hits")
    torrent = st.checkbox("Torrent")
    st.write("============================")
    st.write("Additional ressources:")
    st.page_link("http://wahapedia.ru/", label = "Wahapedia")
    st.page_link("https://www.amazon.de/My-First-Math-Book-Introduction/dp/197596490X", label = "Help, I dont know math")
    st.page_link("https://www.linkedin.com/in/josua-keil-10546a311/", label = "Show me some Orc pictures")

col1, col2, col3 = st.columns(3)

### HIT ROLL

with col1:
    hit_roll = roll(start_distr, dice_threshhold_1, reroll_ones_hit)
    hit_roll_hits = get_amount_of_hits(hit_roll, sustained_hits=sustained_hits_nr)
    fig, ax = plt.subplots()
    ax.bar(range(len(hit_roll_hits)),hit_roll_hits)
    ax.set_xticks(range(0,len(hit_roll_hits)+1,np.max([1,len(hit_roll_hits)//10])))
    ax.set_title("Amount of hits")
    ax.set_ylabel("Density")
    ax2 = ax.twinx()
    ax2.plot(range(len(hit_roll_hits)), np.cumsum(hit_roll_hits), color='red', marker='o', linestyle='-', label='Probability')
    ax2.set_ylabel('Distribution')
    st.pyplot(fig)
    expected_1 = 0
    for i in range(len(hit_roll_hits)):
        expected_1 += i*hit_roll_hits[i]
    f"Expected number of hits: {np.round(expected_1,3)}"


### WOUND ROLL
with col2:
    if not lethal_hits and not torrent:
        wound_roll = roll(hit_roll_hits, dice_threshhold_2, reroll_ones_wound)
        wound_roll_hits = get_amount_of_hits(wound_roll)
    elif torrent:
        # Torrent rules skip the Hit roll
        wound_roll_hits = hit_roll_hits
    elif lethal_hits:
        # Lethal Hits
        pass

    fig, ax = plt.subplots()
    # num_dice might need to be changed once sustained hits appear
    ax.bar(range(len(wound_roll_hits)),wound_roll_hits)
    ax.set_xticks(range(0,len(wound_roll_hits),np.max([1,len(wound_roll_hits)//10])))
    ax.set_title("Amount of successful wound rolls")
    ax.set_ylabel("Density")
    ax2 = ax.twinx()
    ax2.plot(range(len(wound_roll_hits)), np.cumsum(wound_roll_hits), color='red', marker='o', linestyle='-', label='Probability')
    ax2.set_ylabel('Distribution')
    col2.pyplot(fig)
    expected_2 = 0
    for i in range(len(wound_roll_hits)):
        expected_2 += i*wound_roll_hits[i]
    f"Expected number of hits: {np.round(expected_2,3)}"


### SAVE ROLL
# save roll of 2 (removing a hit on 2+) is equivalent to hitting on 6

with col3:
    save_roll = roll(wound_roll_hits, 8-dice_threshhold_3)
    save_roll_hits = get_amount_of_hits(save_roll)

    fig, ax = plt.subplots()
    # num_dice might need to be changed once sustained hits appear
    ax.bar(range(len(save_roll_hits)),save_roll_hits)
    ax.set_xticks(range(0,len(save_roll_hits),np.max([1,len(wound_roll_hits)//10])))
    ax.set_title("Amount of successful wound rolls")
    ax.set_ylabel("Density")
    ax2 = ax.twinx()
    ax2.plot(range(len(save_roll_hits)), np.cumsum(save_roll_hits), color='red', marker='o', linestyle='-', label='Probability')
    ax2.set_ylabel('Distribution')
    col3.pyplot(fig)
    expected_3 = 0
    for i in range(len(save_roll_hits)):
        expected_3 += i*save_roll_hits[i]
    f"Expected number of wounds: {np.round(expected_3,3)}"

if st.checkbox("Show distribution"):
    data = [
        hit_roll_hits,
        list(pd.Series(hit_roll_hits).cumsum()),
        wound_roll_hits,
        list(pd.Series(wound_roll_hits).cumsum()),
        save_roll_hits,
        list(pd.Series(save_roll_hits).cumsum()),
    ]
    index = pd.MultiIndex.from_tuples([
        ('Hit', 'P(X=x)'),
        ('Hit', 'P(X<=x)'),
        ('Wound', 'P(X=x)'),
        ('Wound', 'P(X<=x)'),
        ('Save', 'P(X=x)'),
        ('Save', 'P(X<=x)'),
    ])
    st.dataframe(pd.DataFrame(data, index=index))

if st.checkbox("Show cool plotz"):
    colll1, colll2 = st.columns(2)
    with colll1:
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