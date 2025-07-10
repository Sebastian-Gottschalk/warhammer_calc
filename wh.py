import numpy as np
from scipy.stats import  multinomial
import streamlit as st
import matplotlib.pyplot as plt


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


def get_amount_of_hits(distr):
    '''
    calculates a 1-d distribution of the amount of successes given the matrix of hits and crits
    here hits and crits are treated the same, so no extra rules implemented yet
    '''
    n = distr.shape[0]
    resulting_distr = [0]*n
    for i in range(n):
        for j in range(i+1):
            resulting_distr[i] += distr[j,i-j]
    return resulting_distr



### STREAMLIT INTERFACE

num_dice = st.number_input("Amount of dices used",1,100)
dice_threshhold_1 = st.number_input("Hitting on",2,6)
dice_threshhold_2 = st.number_input("Wounding on",2,6)
dice_threshhold_3 = st.number_input("Saving on",2,6)

with st.sidebar:
    reroll_ones = st.checkbox("Reroll ones")
    if reroll_ones:
        reroll_ones_hit = st.checkbox("Hitroll")
        reroll_ones_wound = st.checkbox("Wound")
    else:
        reroll_ones_hit = False
        reroll_ones_wound = False

col1, col2, col3 = st.columns(3)

### HIT ROLL

start_distr = [0]*num_dice + [1]
hit_roll = roll(start_distr, dice_threshhold_1, reroll_ones_hit)
hit_roll_hits = get_amount_of_hits(hit_roll)

fig, ax = plt.subplots()
ax.bar(range(num_dice+1),hit_roll_hits)
ax.set_xticks(range(num_dice+1))
ax.set_title("Amount of hits")
col1.pyplot(fig)
expected_1 = 0
for i in range(len(hit_roll_hits)):
    expected_1 += i*hit_roll_hits[i]
f"Expected number of hits: {np.round(expected_1,3)}"


### WOUND ROLL

wound_roll = roll(hit_roll_hits, dice_threshhold_2, reroll_ones_wound)
wound_roll_hits = get_amount_of_hits(wound_roll)

fig, ax = plt.subplots()
# num_dice might need to be changed once sustained hits appear
ax.bar(range(num_dice+1),wound_roll_hits)
ax.set_xticks(range(num_dice+1))
ax.set_title("Amount of successful wound rolls")
col2.pyplot(fig)
expected_2 = 0
for i in range(len(wound_roll_hits)):
    expected_2 += i*wound_roll_hits[i]
f"Expected number of hits: {np.round(expected_2,3)}"


### SAVE ROLL
# save roll of 2 (removing a hit on 2+) is equivalent to hitting on 6

save_roll = roll(wound_roll_hits, 8-dice_threshhold_3)
save_roll_hits = get_amount_of_hits(save_roll)

fig, ax = plt.subplots()
# num_dice might need to be changed once sustained hits appear
ax.bar(range(num_dice+1),save_roll_hits)
ax.set_xticks(range(num_dice+1))
ax.set_title("Amount of successful wound rolls")
col3.pyplot(fig)
expected_3 = 0
for i in range(len(save_roll_hits)):
    expected_3 += i*save_roll_hits[i]
f"Expected number of wounds: {np.round(expected_3,3)}"

