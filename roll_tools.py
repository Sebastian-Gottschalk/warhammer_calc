import streamlit as st
import numpy as np
from scipy.stats import  multinomial

@st.cache_data
def single_roll(n, thresh, reroll_ones = False,critting_on = 6, reroll_all = False):
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
    p_crit = (7-critting_on)/6
    p_hit = (critting_on-thresh)/6
    if not reroll_ones and not reroll_all:
        p = [p_hit,p_crit,1-p_hit-p_crit]
        for i in range(n+1):
            for j in range(n+1-i):
                if i+j<=n:
                    results[i,j] = multinomial.pmf([i,j,n-i-j], n=n, p=p)
    else:
        # Get the probability distribution after the first roll
        if reroll_ones:
            results_roll_1 = np.zeros((n+1,n+1,n+1))
            p_one = 1/6
            p = [p_one, p_hit, p_crit, 1-p_hit-p_one-p_crit]
        elif reroll_all:
            results_roll_1 = np.zeros((n+1,n+1))
            p_one = 1-p_hit-p_crit
            p = [p_one, p_hit, p_crit]
        for i in range(n+1): #crits
            for j in range(n+1): #hits
                if reroll_all:
                    if i+j<=n:
                        results_roll_1[i,j] = multinomial.pmf([i,j,n-i-j], n=n, p=p)
                else: # reroll_ones
                    for l in range(n+1): #ones
                        if i+j+l<=n:
                                results_roll_1[i,j,l] = multinomial.pmf([i,j,l,n-i-j-l], n=n, p=p)
        
                                
        
        # Use the first distribution to reroll ones
        for i in range(n+1): #ones
            new_roll = single_roll(i,thresh,critting_on=critting_on)
            for j in range(n+1): #hits
                if reroll_all:
                    if i+j<=n:
                        l=n-j-i
                        results[j:j+i+1, l:l+i+1] += results_roll_1[i,j]*new_roll
                else: # reroll_ones
                    for l in range(n+1): #crits
                        if i+j+l<=n:
                            results[j:j+i+1, l:l+i+1] += results_roll_1[i,j,l]*new_roll
    return results

@st.cache_data
def roll(distr, thresh, reroll_ones = False,critting_on=6,reroll_all = False):
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
        if prob:
            n_distr = single_roll(n,thresh, reroll_ones,critting_on=critting_on,reroll_all=reroll_all)
            n_distr = np.pad(n_distr,(0,max_n-n-1), mode="constant", constant_values=0)
            resulting_distr += prob * n_distr
    return resulting_distr

@st.cache_data
def get_amount_of_hits(distr, sustained_hits = 0, lethal_hits = False):
    '''
    calculates a 1-d distribution of the amount of successes given the matrix of hits and crits
    here hits and crits are treated the same, so no extra rules implemented yet
    '''
    n = distr.shape[0]
    if sustained_hits and not lethal_hits:
        resulting_distr = [0]*((n-1)*(1+sustained_hits)+1)
        for i in range(n):
            for j in range(n):
                if i+j<=n-1:
                    resulting_distr[i+(sustained_hits+1)*j] += distr[i,j]
    elif lethal_hits and not sustained_hits:
        resulting_distr = distr
    elif lethal_hits and sustained_hits:
        resulting_distr = np.zeros(((n-1)*sustained_hits+1, distr.shape[1]))
        for i in range(n):
            for j in range(n):
                if i+j<=n-1:
                    resulting_distr[i+sustained_hits*j, j] = distr[i,j]
    else:
        resulting_distr = [0]*n
        for i in range(n):
            for j in range(i+1):
                resulting_distr[i] += distr[j,i-j]
        
    return resulting_distr

def get_dicesum(nr_dice, bias, dice_size):
    if nr_dice:
        single_die = np.ones(dice_size) / dice_size
        distr = single_die
        for _ in range(nr_dice-1):
            distr = np.convolve(distr, single_die)
        possible_sum = np.arange(nr_dice + bias, dice_size*nr_dice+bias+1)
        resulting_distr = [0]*(dice_size*nr_dice+bias+1)
        for i in possible_sum:
            resulting_distr[i] = distr[i-min(possible_sum)]
        return resulting_distr
    else: # in case nr_dice = 0
        return [0]*bias+[1]
    
def get_threshhold_plot(dice_roll, threshhold = 0.999, multi_list = False):
    if not multi_list:
        dice_roll_cumsum = np.cumsum(dice_roll)
        dice_roll_index = np.argmax(dice_roll_cumsum>0.999)
        dice_roll_index = min(dice_roll_index+1, len(dice_roll))
        return dice_roll[:dice_roll_index]
    if multi_list:
        max_index = 0
        for i in range(len(dice_roll)):
            dice_roll_cumsum = np.cumsum(dice_roll[i])
            dice_roll_index = np.argmax(dice_roll_cumsum>0.999)
            dice_roll_index = min(dice_roll_index+1, len(dice_roll[i]))
            if dice_roll_index>max_index:
                max_index = dice_roll_index
        return [dice_result[:max_index] for dice_result in dice_roll]