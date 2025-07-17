import streamlit as st
import numpy as np
from scipy.stats import  multinomial, binom

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
def get_amount_of_hits(distr, sustained_hits = 0, crit_auto_hit = False):
    '''
    calculates a 1-d distribution of the amount of successes given the matrix of hits and crits
    here hits and crits are treated the same, so no extra rules implemented yet
    '''
    n = distr.shape[0]
    if sustained_hits and not crit_auto_hit:
        resulting_distr = [0]*((n-1)*(1+sustained_hits)+1)
        for i in range(n):
            for j in range(n):
                if i+j<=n-1:
                    resulting_distr[i+(sustained_hits+1)*j] += distr[i,j]
    elif crit_auto_hit and not sustained_hits:
        resulting_distr = distr
    elif crit_auto_hit and sustained_hits:
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


def get_wound_threshhold(strength, toughness,modifier = 0, fixed_value = 0):
    if fixed_value:
        return fixed_value
    
    if strength >= 2*toughness:
        return_value =  2
    elif strength > toughness:
        return_value =  3
    elif strength == toughness:
        return_value =  4
    elif strength >toughness/2:
        return_value =  5
    else:
        return_value =  6
    
    # add the modifier and clip it into the range from 2 to 6
    return_value += modifier
    return_value = np.min(return_value, 6)
    return_value = np.max(return_value, 2)

    return return_value


# save_roll_hits:
#   distribution of how many saves failed - independent of MW or not, in case of MW call this function twice
# damage_distr:
#   distribution of how much dmg each failed save will inflict
# troop:
#   numpy-array in the shape (wound_per_unit+1, amount_units)
# eg
#  [0 0
#   1 0]
#   generally troop[i,k] is equal to the probability that amount_units-k units are still alive and one of them still has i HP
#   note that p[0,k] should always be 0 except for p[0,amount_units] in which case this value represents the chance of the whole squad dying
def shoot_on_troop(save_roll_hits, damage_distr, troop, feel_no_pain):
    if feel_no_pain:
        # adjust damage_distr to include FnP
        damage_fnp = [0]*len(damage_distr)
        prob_fnp = (feel_no_pain-1)/6 # probability that the feel no pain roll misses
        for n in range(len(damage_distr)):
            for k in range(n+1):
                prob = binom.pmf(k,n,prob_fnp)
                damage_fnp[k]+=prob*damage_distr[n]
        damage_distr = damage_fnp

    resulting_distr = save_roll_hits[0]*troop
    for save in range(1,len(save_roll_hits)):
        new_distr = np.zeros(troop.shape)
        for i in range(troop.shape[0]):
            for k in range(troop.shape[1]):
                if troop[i,k]>0:
                    for dmg in range(len(damage_distr)):
                        if i-dmg>0:
                            new_distr[i-dmg,k] += damage_distr[dmg]*troop[i,k]
                        elif k == troop.shape[1]-1:
                            new_distr[0,k] += damage_distr[dmg]*troop[i,k]
                        else:
                            new_distr[troop.shape[0]-1,k+1] += damage_distr[dmg] * troop[i,k]
        troop = new_distr
        resulting_distr += save_roll_hits[save]*troop
    return resulting_distr