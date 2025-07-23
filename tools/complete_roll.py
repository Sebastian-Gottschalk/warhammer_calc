import streamlit as st
from tools.roll_tools import *
from tools.plot_tools import *
from scipy.stats import  multinomial, binom
import pandas as pd



@st.cache_data
def complete_roll(
        start_distr,
        dice_threshhold_1,dice_threshhold_2,dice_threshhold_3,
        hit_roll_crit,wound_roll_crit, damage_distr,
        reroll_ones_hit, reroll_all_hit, reroll_ones_wound, reroll_all_wound,
        sustained_hits_nr, lethal_hits,dev_wounds, torrent,
        feel_no_pain,feel_no_pain_2, plot_results, show_distr, troops
        ):

    no_save_roll = dice_threshhold_3==7

    if feel_no_pain and not np.sum(troops):
        col1, col2,col3,col4, col5= st.columns(5)
    else:
        col1, col2,col3,col4= st.columns(4)


    ### HIT ROLL

    with col1:
        hit_roll_hits = hit_roll(start_distr,dice_threshhold_1,reroll_ones_hit,hit_roll_crit,reroll_all_hit,sustained_hits_nr,lethal_hits,torrent)

        if plot_results:
            st.write(plot_result(hit_roll_hits, lethal_hits,col1,"Hit"))




    ### WOUND ROLL

    with col2:
        wound_roll_hits = wound_roll(hit_roll_hits,dice_threshhold_2,reroll_ones_wound,wound_roll_crit,reroll_all_wound,sustained_hits_nr,lethal_hits,torrent,dev_wounds)

        if plot_results:
            st.write(plot_result(wound_roll_hits, dev_wounds, col2, "Wound"))
    

    ### SAVE ROLL
    # save roll of 2 (removing a hit on 2+) is equivalent to hitting on 6

    with col3:

        save_roll_hits = save_roll(wound_roll_hits,dice_threshhold_3,dev_wounds,no_save_roll)

        if plot_results:
            st.write(plot_result(save_roll_hits,dev_wounds,col3,"Save",custom_text="failed Saves"))


    ### DAMAGE ROLL
    ### OR
    ### DISTRIBUTION OF GUYS SHOT

    with col4:
        if np.sum(troops):
            shooting_result = shoot_roll(save_roll_hits, damage_distr,troops,feel_no_pain,dev_wounds,feel_no_pain_2)
            if plot_results:
                st.write(plot_result(
                    shooting_result[1:,:].sum(axis=0).tolist() + [shooting_result[0,-1]],
                    False,col4,"dead Unit"
                ))
            st.write(f"Chance for annihilation: {np.round(100*shooting_result[0,-1],2)}%")
        else:
            damage_roll = damaging_roll(save_roll_hits,damage_distr,dev_wounds)

            if plot_results:
                st.write(plot_result(damage_roll,dev_wounds,col4,"Damage",custom_text="Damage"))

    ### FEEL NO PAIN


    if feel_no_pain and not np.sum(troops):
        with col5:
            damage_fnp = fnp_roll(damage_roll,feel_no_pain, dev_wounds, feel_no_pain_2)
            
            if plot_results:
                st.write(plot_result(damage_fnp,dev_wounds,col5,"Feel no Pain",custom_text="Damage after FnP"))


    if show_distr:
        col_distr_1, col_distr_2 = st.columns(2)


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

                hits = save_roll_hits.sum(axis=1)
                crits = save_roll_hits.sum(axis=0)
                data += [
                    hits,
                    list(pd.Series(hits).cumsum()),
                    crits,
                    list(pd.Series(crits).cumsum()),
                ]
                idx_tuple += [
                    ('Save', 'P(X=x)'),
                    ('Save', 'P(X<=x)'),
                    ("Save - Crit", "P(X=x)"),
                    ("Save - Crit", "P(X<=x)")
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
            if np.sum(troops):
                troops_killed = shooting_result[1:,:].sum(axis=0).tolist() + [shooting_result[0,-1]]
                data = [
                    troops_killed,
                    list(pd.Series(troops_killed).cumsum())
                ]
                index = pd.MultiIndex.from_tuples([
                    ('Units killed', 'P(X=x)'),
                    ('Units killed', 'P(X<=x)'),
                ])
            else:
                if dev_wounds:
                    hits = damage_roll.sum(axis=1)
                    crits = damage_roll.sum(axis=0)
                    data = [
                        hits,
                        list(pd.Series(hits).cumsum()),
                        crits,
                        list(pd.Series(crits).cumsum()),
                    ]
                    index = pd.MultiIndex.from_tuples([
                        ('Damage', 'P(X=x)'),
                        ('Damage', 'P(X<=x)'),
                        ("Damage - Crit", "P(X=x)"),
                        ("Damage - Crit", "P(X<=x)")
                    ])
                else:
                    data = [
                        damage_roll,
                        list(pd.Series(damage_roll).cumsum())
                    ]
                    index = pd.MultiIndex.from_tuples([
                        ('Damage', 'P(X=x)'),
                        ('Damage', 'P(X<=x)'),
                    ])
            st.dataframe(pd.DataFrame(data, index=index))







@st.cache_data
def hit_roll(start_distr,dice_threshhold_1,reroll_ones_hit,hit_roll_crit,reroll_all_hit,sustained_hits_nr,lethal_hits,torrent):
    ### HIT ROLL


    if not torrent: 
        hit_roll = roll(start_distr, dice_threshhold_1, reroll_ones=reroll_ones_hit, critting_on=hit_roll_crit, reroll_all=reroll_all_hit)
        hit_roll_hits = get_amount_of_hits(hit_roll, sustained_hits=sustained_hits_nr, crit_auto_hit=lethal_hits)
    else:
        hit_roll_hits = start_distr
        
    return hit_roll_hits


@st.cache_data
def wound_roll(hit_roll_hits,dice_threshhold_2,reroll_ones_wound,wound_roll_crit,reroll_all_wound,sustained_hits_nr,lethal_hits,torrent,dev_wounds):
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
    
    return wound_roll_hits


@st.cache_data
def save_roll(wound_roll_hits,dice_threshhold_3,dev_wounds,no_save_roll):
    if no_save_roll:
            # save_roll = wound_roll
            save_roll_hits = wound_roll_hits
    elif dev_wounds:
        save_roll_hits = [0]*(wound_roll_hits.shape[0]+wound_roll_hits.shape[1]-1)
        save_roll_hits = np.zeros(wound_roll_hits.shape)
        for i in range(wound_roll_hits.shape[1]):
            save_roll = roll([0]*i+[1],8-dice_threshhold_3)
            save_roll = get_amount_of_hits(save_roll)
            for k in range(wound_roll_hits.shape[0]):             
                save_roll_hits[0:i+1,k]+=wound_roll_hits[i,k]*np.array(save_roll)
        save_roll_hits=save_roll_hits[0:wound_roll_hits.shape[0]]
    else:
        save_roll = roll(wound_roll_hits, 8-dice_threshhold_3)
        save_roll_hits = get_amount_of_hits(save_roll)
    return save_roll_hits

@st.cache_data
def shoot_roll(save_roll_hits, damage_distr,troops,feel_no_pain, dev_wounds,feel_no_pain_2):
    if not dev_wounds:
        shooting_result = shoot_on_troop(save_roll_hits, damage_distr, troops, feel_no_pain,False)
    else:
        shooting_result = np.zeros(troops.shape)
        for hits in range(save_roll_hits.shape[0]):
            current_hits = [0]*hits + [1]
            # resolving the non Mortal wounds first
            first_result = shoot_on_troop(current_hits,damage_distr,troops,feel_no_pain, False)
            # st.write(first_result)
            # then resolving the mortal wounds
            second_result = shoot_on_troop(save_roll_hits[hits,:],damage_distr,first_result,feel_no_pain_2,True)
            shooting_result += second_result
            # st.write(second_result)
    if np.sum(shooting_result)<1:
        shooting_result[0,-1]+=1-np.sum(shooting_result)
    return shooting_result

@st.cache_data
def damaging_roll(save_roll_hits,damage_distr,dev_wounds):
    if dev_wounds:
        damage_roll = np.zeros(((save_roll_hits.shape[0]-1)*(len(damage_distr)-1)+1,(save_roll_hits.shape[1]-1)*(len(damage_distr)-1)+1))
        # damage_roll[i,k] = prob of i normal wounds and k mortal wounds
        all_damage_distr = [[1]]
        for i in range(save_roll_hits.shape[0]):
            all_damage_distr.append(list(np.convolve(all_damage_distr[-1],damage_distr)))
        for i in range(save_roll_hits.shape[0]):
            for k in range(save_roll_hits.shape[1]):
                for i_new in range(len(all_damage_distr[i])):
                    for k_new in range(len(all_damage_distr[k])):
                        damage_roll[i_new, k_new] += save_roll_hits[i,k]*all_damage_distr[i][i_new]*all_damage_distr[k][k_new]

    else:
        damage_roll = np.zeros((len(save_roll_hits)-1)*(len(damage_distr)-1)+1)
        damage_distr_cur = np.array([1])
        for i, prob in enumerate(save_roll_hits):
            damage_roll+=np.pad(prob*damage_distr_cur,(0,len(damage_roll)-len(damage_distr_cur)))
            damage_distr_cur = np.convolve(damage_distr_cur,damage_distr)
    return damage_roll

@st.cache_data
def fnp_roll(damage_roll,feel_no_pain, dev_wounds, feel_no_pain_2):
    prob_fnp = (feel_no_pain-1)/6 # probability that the feel no pain roll misses
    prob_fnp_2 = (feel_no_pain_2-1)/6
    if dev_wounds:
        damage_fnp_after_non_mortal = np.zeros(damage_roll.shape)
        damage_fnp = np.zeros(damage_roll.shape)
        # first apply FnP for the non mortal hits (rows in damage_roll)
        for n in range(damage_roll.shape[0]): # nr of hits
            for k in range(n+1):
                prob = binom.pmf(k,n,prob_fnp)
                for l in range(damage_roll.shape[1]):
                    damage_fnp_after_non_mortal[k,l] += prob * damage_roll[n,l]
        st.write(np.sum(damage_fnp_after_non_mortal))
        for n in range(damage_roll.shape[1]): # nr of hits
            for k in range(n+1):
                prob = binom.pmf(k,n,prob_fnp)
                for l in range(damage_roll.shape[0]):
                    damage_fnp[l,k] += prob * damage_fnp_after_non_mortal[l,n]
        st.write(np.sum(damage_fnp))
    else:
        damage_fnp = [0]*len(damage_roll)
        for n in range(len(damage_roll)):
            if damage_roll[n]:
                for k in range(n+1):
                    prob = binom.pmf(k,n,prob_fnp)
                    damage_fnp[k]+=prob*damage_roll[n]
    return damage_fnp