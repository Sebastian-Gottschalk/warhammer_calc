import numpy as np
from scipy.stats import  multinomial, binom
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import base64

from tools.wh.plot_tools import *
from tools.general.roll_tools import *
from tools.wh.complete_roll import *
from tools.wh.gen import *

from wahapedia.db_interaction.interact import csv_files



### STREAMLIT INTERFACE

# setup
if "setup_40k" not in st.session_state:
    setup_40k()
    st.session_state.setup_40k = True


files = st.session_state.wh_files


# Buttons to add / remove weapons
_,minus,middle,plus,col_weapon_load = st.columns(5)
minus.button(":heavy_minus_sign:", on_click=remove_weapon, disabled= st.session_state.wh_number_of_weapons == 1)
weapon_to_load = col_weapon_load.selectbox("Select Weapon to add", options = ["default"] + list(st.session_state.wh_saved_weapons.keys()))
plus.button(":heavy_plus_sign:", on_click=add_weapon, args = [weapon_to_load])
middle.write(f"Current Nr of weapons: {st.session_state.wh_number_of_weapons}")

# setting up the sidebar options
with st.sidebar:

    fight_troop = st.checkbox("Shoot on dudes", value = True)
    troops = 0
    
    # Setting up the options to choose for troop size / wounds per model / ...
    if fight_troop:
        faction = st.selectbox("Faction", [""] + files.get_faction_names(), index = 0)
        
        model_name = st.selectbox("Model", [""] + files.get_faction_member(faction), index = 0)

        if model_name:
            m_toughness, m_save, m_invul, m_troopsize, m_wounds = files.get_defensive_stats(model_name)
        else:
            m_toughness, m_save, m_invul, m_troopsize, m_wounds = 6,4,7,[10],3
        

        co1, co2, co3, co4 = st.columns([2,1,1,1])
        amount_of_troops = co1.selectbox("\# of Models", m_troopsize, accept_new_options = True)
        if isinstance(amount_of_troops, str):
            if amount_of_troops.isnumeric():
                amount_of_troops = int(amount_of_troops)
            else:
                st.warning("Invalid Input, defaulting to 10 models")
                amount_of_troops = 10
        wounds_per_troop = co2.number_input("W",1,20,value=m_wounds)
        toughness = co3.number_input("T",1,100,value=m_toughness)
        troops_save = co4.number_input("SV",2,6,value=m_save)
        troops = np.zeros((wounds_per_troop+1,amount_of_troops))
        troops[wounds_per_troop,0] = 1
        if st.checkbox("Invul save", value = m_invul < 7):
            default_invul = 5 if m_invul == 7 else m_invul
            co1, co2 = st.columns(2)
            with co1:
                invul_melee = st.number_input("Melee",2,6,value = m_invul)
            with co2:
                invul_ranged = st.number_input("Ranged",2,6,value = m_invul)
        else:
            invul_melee = 0
            invul_ranged = 0
    
    plot_results = st.checkbox("Plot Results", value = True)
    if plot_results:
        plot_all_results = st.checkbox("Plot all results")
    else:
        plot_all_results = False

    plot_sum = st.checkbox("Plot dmg + mortals", value = True)
    plot_sep = st.checkbox("Plot dmg and mortals seperate", value = False)
    
    show_distr = st.checkbox("Show distribution")

    inv_distr = st.checkbox("Invert Distribution")

    st.write("")
    st.write("")
    st.write("Additional ressources:")
    st.page_link("http://wahapedia.ru/", label = "Wahapedia")
    st.page_link("https://www.amazon.de/My-First-Math-Book-Introduction/dp/197596490X", label = "Help, I dont know math")
    st.page_link("https://www.linkedin.com/in/josua-keil-10546a311/", label = "Show me some Orc pictures")
    show_kroot_1()
    st.write("The stats of the individual units are powered by Wahapedia")

show_kroot_2()

all_settings = []
all_enabled = []

all_right_columns = []
all_delete_columns = []
# Setting up the Interface to have the user select stats while saving them in variables
for i in range(st.session_state.wh_number_of_weapons):
    # read the currently saved value from the session state
    default_values = st.session_state.wh_current_settings_wo_calc[i]
    k = st.session_state.wh_expander_tracker[i]
    
    
    left,middle, right = st.columns([1,30,1])
    all_right_columns.append(right) # saving that column for the swap weapon option
    
    # moving the checkboxes 10px down and scaling them with factor 1.2 to align the enable boxes with the text
    left.markdown(
        """
        <style>
        /* Target all checkboxes */
        div[data-testid="stCheckbox"] {
            margin-top: 10px;  /* Moves checkbox down */
        }

        /* Optionally, adjust the checkbox input height */
        div[data-testid="stCheckbox"] input[type="checkbox"] {
            transform: scale(1.2);  /* Makes the checkbox bigger */
            margin-right: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    enabled = left.checkbox(" ", key=f"wh_enabled_{k}", value = True)

    # Markdown to set the background of expander objects
    middle.markdown(
        """
        <style>
        /* Style the expander container */
        div[data-testid="stExpander"] {
            background-color: rgba(0, 0, 0, 0.8) !important;  /* Dark gray opaque */
            border-radius: 8px !important;
            padding: 0 !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Building the Options for the user to choose and saving the resulting weapon in a variable
    with middle.expander(f"{i+1} - {st.session_state.wh_names_of_weapons[i]}", expanded = st.session_state.wh_expanders[i]):
        
        if fight_troop:
            co1,co2,co3,co4 = st.columns([1,4,4,1]) # needed to define here to avoid issues with reseting the faction selection if name changes happen
                    
        st.session_state.wh_expanders[i] = True
        left,middle, col_save,col_del,_ = st.columns([21,3,3,1,1])
        all_delete_columns.append(col_del)
        # name = left.text_input("Name",value = st.session_state.wh_names_of_weapons[i], key=f"wh_enter_name_{k}")
        weapon_kind = middle.selectbox(" ",Options.WEAPON_OPTIONS, index = default_values["weapon_kind"],key = f"wh_weapon_kind_{k}")
        # if name != st.session_state.wh_names_of_weapons[i]:
        #     st.session_state.wh_names_of_weapons[i] = name
        #     st.session_state[f"wh_faction_sel_{k}"] = ""
        #     st.session_state[f"wh_model_sel_{k}"] = ""
        #     st.session_state[f"wh_weapon_sel_{k}"] = ""
        #     st.session_state[f"wh_model_amount_sel_{k}"] = ""
        #     st.rerun()

        if fight_troop:
            faction = co1.selectbox("Faction", [""] + files.get_faction_names(), index = 0, key = f"wh_faction_sel_{k}")
            model_name = co2.selectbox("Model", [""] + files.get_faction_member(faction), index = 0, key = f"wh_model_sel_{k}")
            if model_name:
                weapon_name = co3.selectbox("Weapon",[""] + files.get_weapon_options(model_name), index = 0, key = f"wh_weapon_sel_{k}")
                if weapon_name:
                    model_amount = co4.selectbox("\# of Models", files.get_model_count(files.get_id(model_name)), accept_new_options = True, key = f"wh_model_amount_sel_{k}")
                    if isinstance(model_amount,str):
                        if model_amount.isnumeric():
                            model_amount = int(model_amount)
                        else:
                            st.warning("Enter only numbers")
                            model_amount = 1 #defaulting to 1
                    weapon_stats = files.get_offensive_stats(model_name, weapon_name, model_amount)
                    for key, val in weapon_stats.items():
                        default_values[key] = val
                    if st.session_state.wh_names_of_weapons[i] != weapon_name or st.session_state.wh_model_amount[i] != model_amount:
                        st.session_state.wh_names_of_weapons[i] = weapon_name
                        st.session_state.wh_model_amount[i] = model_amount
                        update_button_session_state(default_values,k)
                        
                        st.rerun()

        main_col_1, main_col_2 = st.columns(2)

        _,col_title_1,_ = main_col_1.columns([0.25,1,0.25])
        with col_title_1:
            st.title("Attack Dice")

        _,coll1,_, coll2,_, coll3,_ = main_col_1.columns([0.25,1,0.125,0.75,0.125,1,0.25])
        with coll1:
            num_dice_att = st.number_input("Dice", min_value=0, key=f"wh_num_dice_1_{k}", step = 1)
        with coll2:
            dice_size_att = int(st.radio("_", ["W"+str(number) for number in Options.DICE_SIZES_ATT], key=f"wh_dice_size_1_{k}", label_visibility = "hidden")[1:])
        with coll3:
            modifier_att = st.number_input("Modifier", key=f"wh_modifier_1_{k}", min_value=0, step = 1)

        start_distr = get_dicesum(num_dice_att, modifier_att, dice_size_att)

        _,col_title_2,_ = main_col_2.columns([0.125,1,0.125])
        with col_title_2:
            st.title("Damage Profile")

        _,colllll1,_, colllll2,_, colllll3,_ = main_col_2.columns([0.25,1,0.125,0.75,0.125,1,0.25])
        with colllll1:
            num_dice_dmg = st.number_input("Dice", min_value=0, key=f"wh_num_dice_2_{k}", step = 1)
        with colllll2:
            dice_size_dmg = int(st.radio("_2", ["W"+str(number) for number in Options.DICE_SIZES_WND], key=f"wh_dice_size_2_{k}", label_visibility = "hidden")[1:])
        with colllll3:
            modifier_dmg = st.number_input("Modifier", key=f"wh_modifier_2_{k}", step = 1)
            
        damage_distr = get_dicesum(num_dice_dmg, modifier_dmg, dice_size_dmg)

        if fight_troop:
            co1, co2, co3,co4 = st.columns(4)
        else:
            co1, co2, co4 = st.columns(3)
        
        with co1:
            dice_threshhold_1 = st.number_input("Hitting on",2,6,key=f"wh_hitting_on_{k}")
        
        if fight_troop:
            with co2:
                strength = st.number_input("Strength",1,50, key=f"wh_wounding_on_{k}")
            with co3:
                modifier = st.number_input("Modifier to wound", -5,5, key = f"wh_modifier_{k}")
            with co4:
                ap = st.number_input("AP",0,6, key=f"wh_ap_{k}")
                dice_threshhold_3 = min([troops_save + ap, 6])
                if invul_melee:
                    if weapon_kind == "Melee": # melee
                        dice_threshhold_3 = min([dice_threshhold_3, invul_melee])
                    elif weapon_kind == "Ranged": # ranged
                        dice_threshhold_3 = min([dice_threshhold_3, invul_ranged])
        else:
            with co2:
                dice_threshhold_2 = st.number_input("Wounding on",2,6, value=default_values["dice_threshhold_2"], key=f"wh_wounding_on_{k}")
            strength = default_values["strength"]
            modifier = default_values["modifier"]
            ap = default_values["ap"]
            with co4:
                dice_threshhold_3 = st.number_input("Saving on",2,7, value=default_values["dice_threshhold_3"], key=f"wh_saving_on_{k}")
        
        if fight_troop:
            col1,col2,col3,col4,col5,col6,col7,col8,col9 = st.columns(9)
        else:
            col1,col2,col3,col4,col5,col6,col7 = st.columns(7)
        dev_wounds_overspill = False
        
        reroll = col1.checkbox("Rerolls", key=f"wh_rerolls_{k}", value = default_values["reroll"])
        if reroll:
            rerolls_hit = col1.selectbox("Hit Roll",Options.REROLL_OPTIONS , key=f"wh_hit_roll_{k}", index=default_values["reroll_hit"])
            rerolls_wound = col1.selectbox("Wound Roll", Options.REROLL_OPTIONS, key=f"wh_wound_roll_{k}", index = default_values["reroll_wound"])
        else: # default values for saving
            rerolls_hit = "No reroll"
            rerolls_wound = "No reroll"
        
        sustained_hits = col2.checkbox("Sustained hits", key=f"wh_sustained_hits_{k}", value = default_values["sustained_hits"])
        if sustained_hits:
            sus_key = f"wh_sustained_hits_nr_{k}"
            st.markdown(
                f"""
                <style>
                div.st-key-{sus_key} {{
                    margin-top: 27px !important;
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )
            sustained_hits_nr = col2.number_input("Sustained Hits",1,10,label_visibility="collapsed", key=sus_key, value = max(default_values["sustained_hits_nr"],1))
        else:
            sustained_hits_nr = 0
        
        lethal_hits = col3.checkbox("Lethal Hits", key=f"wh_lethal_hits_{k}", value = default_values["lethal_hits"])
        dev_wounds = col4.checkbox("Dev Wounds", key=f"wh_dev_wounds_{k}", value = default_values["dev_wounds"])
        torrent = col5.checkbox("Torrent", key=f"wh_torrent_{k}", value = default_values["torrent"])
        crit_modifier= col6.checkbox("Crit Modifier", key=f"wh_modify_crit_{k}", value = default_values["crit_modifier"])        
        fnp_checkbox =  col7.checkbox("Feel No Pain", key=f"wh_feel_no_pain_{k}", value = default_values["feel_no_pain_setting"])
        
        if dev_wounds:
            dev_wounds_overspill = col4.checkbox("Overspill", key=f"wh_dev_wounds_overspill_{k}", value = default_values["dev_wounds_overspill"])
        if torrent: # the combination doesnt make sense and only screws up the plots
            lethal_hits = False
        if fnp_checkbox:
            feel_no_pain = col7.number_input("Normal FnP",2,7,value=default_values["feel_no_pain"],label_visibility="collapsed", key=f"wh_normal_fnp_{k}")
            fnp_checkbox_mortals = col7.checkbox("Different FnP on Mortals", key=f"wh_weird_stuff_{k}", value = default_values["fnp_checkbox_mortals"])
            if fnp_checkbox_mortals:
                feel_no_pain_2 = col7.number_input("DevWounds FnP",2,7,value=default_values["feel_no_pain_2"],label_visibility="collapsed")
            else:
                feel_no_pain_2 = feel_no_pain     
        else:
            feel_no_pain = 6
            feel_no_pain_2 = 6
            fnp_checkbox_mortals = False

        if fight_troop:
            if col8.checkbox("No saving throw", value = default_values["dice_threshhold_3"] == 7,key=f"wh_no_sv_throw_{k}"):
                dice_threshhold_3 = 7
            if col9.checkbox("Fixed value to wound", value = default_values["fixed_hit_thresh"] > 0, key = f"wh_fixed_value_{k}"):
                fix_hit_def_value = default_values["fixed_hit_thresh"] if default_values["fixed_hit_thresh"] else 4
                fix_hit = col9.number_input("",2,6, value = fix_hit_def_value, key = f"wh_fixed_value_nr_input_{k}")
            else:
                fix_hit = 0                
            dice_threshhold_2 = get_wound_threshhold(strength,toughness,modifier, fix_hit)
        else:
            fix_hit = 0

        if crit_modifier:
            hit_roll_crit = col6.number_input("Hit roll critting on",2,6,value=default_values["hit_roll_crit"], key=f"wh_hit_roll_crit_{k}")
            if hit_roll_crit<dice_threshhold_1:
                dice_threshhold_1 = hit_roll_crit
            wound_roll_crit = col6.number_input("Wound roll critting on", 2,6, value=default_values["wound_roll_crit"], key=f"wh_wound_roll_crit_{k}")
            if wound_roll_crit<dice_threshhold_2:
                dice_threshhold_2 = wound_roll_crit
        else:
            hit_roll_crit=6
            wound_roll_crit=6

        save_weapon_settings = {
            "weapon_kind" : Options.WEAPON_OPTIONS.index(weapon_kind),
            "num_dice_att":num_dice_att,
            "dice_size_att":Options.DICE_SIZES_ATT.index(dice_size_att),
            "modifier_att":modifier_att,
            "start_distr": start_distr,
            "num_dice_dmg":num_dice_dmg,
            "dice_size_dmg":Options.DICE_SIZES_WND.index(dice_size_dmg),
            "modifier_dmg":modifier_dmg,
            "damage_distr": damage_distr,
            "dice_threshhold_1":dice_threshhold_1,
            "strength" : strength,
            "modifier" : modifier,
            "dice_threshhold_2":dice_threshhold_2,
            "ap" : ap,
            "dice_threshhold_3":dice_threshhold_3,
            "reroll":reroll,
            "reroll_hit":Options.REROLL_OPTIONS.index(rerolls_hit),
            "reroll_wound":Options.REROLL_OPTIONS.index(rerolls_wound),
            "sustained_hits":sustained_hits,
            "sustained_hits_nr":sustained_hits_nr,
            "lethal_hits":lethal_hits,
            "dev_wounds":dev_wounds,
            "dev_wounds_overspill": dev_wounds_overspill,
            "torrent": torrent,
            "crit_modifier":crit_modifier,
            "hit_roll_crit": hit_roll_crit,
            "wound_roll_crit": wound_roll_crit,
            "feel_no_pain_setting": fnp_checkbox,
            "feel_no_pain": feel_no_pain,
            "fnp_checkbox_mortals": fnp_checkbox_mortals,
            "feel_no_pain_2": feel_no_pain_2,
            "fixed_hit_thresh" : fix_hit
        }
        
        # move the button 10 pixel down
        button_key = f"wh_save_button_{k}"
        col_save.markdown(
            f"""
            <style>
            div.st-key-{button_key} {{
                margin-top: 10px !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
        col_save.button("Save Weapon", on_click = save_weapon, args = [st.session_state.wh_names_of_weapons[i], save_weapon_settings], key=button_key)
        
    # saving the weapon options and the fact if they are selected or not
    all_settings.append(save_weapon_settings)
    all_enabled.append(enabled)

# Creating the Swap weapons menu and the Delete buttons
for i in range(st.session_state.wh_number_of_weapons):
    right = all_right_columns[i]
    # moving the up arrow 18px down
    st.markdown(
                f"""
                <style>
                div.st-key-weapon_move_up_{i} {{
                    transform: scale(0.8) !important;
                    margin-top: 0px;
                    margin-bottom: -18px;
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )
    # moving the down arrow 18px up
    st.markdown(
                f"""
                <style>
                div.st-key-weapon_move_down_{i} {{
                    transform: scale(0.8) !important;
                    margin-top: 0px;
                    margin-bottom: 18px;
                }}
                </style>
                """,
                unsafe_allow_html=True,
            )

    if right.button("", icon = ":material/arrow_drop_up:", key= f"weapon_move_up_{i}", disabled = i == 0, on_click = swap_weapons, args = [all_settings,i,i-1]):
        st.rerun()

    if right.button("", icon = ":material/arrow_drop_down:", key= f"weapon_move_down_{i}",disabled = i == st.session_state.wh_number_of_weapons -1, on_click = swap_weapons, args = [all_settings,i,i+1]):
        st.rerun()

    # move the button 10 pixel down
    col_del = all_delete_columns[i]
    button_key = f"delete_weapon_{i}"
    col_del.markdown(
        f"""
        <style>
        div.st-key-{button_key} {{
            margin-top: 10px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    if col_del.button(" ", icon = ":material/delete:", key = button_key, on_click = delete_current_weapon, args = [all_settings,i], disabled = st.session_state.wh_number_of_weapons == 1):
        st.rerun()

    



if sustained_hits_nr>=2 and lethal_hits and dev_wounds:
    st.write("The plots and future calculations are wrong. To-do: fix")



# Setting up the Calculate Button and updating session states if pressed
_,middle,_ = st.columns([3,1,3])
if middle.button("Calculate"):
    st.session_state.wh_current_settings_wo_calc = all_settings
    st.session_state.wh_current_settings= st.session_state.wh_current_settings_wo_calc.copy()
    st.session_state.wh_troops = troops
    st.session_state.wh_current_troops = [troops]
    st.session_state.wh_enabled_weapons = all_enabled
    st.session_state.wh_current_names_of_weapons = st.session_state.wh_names_of_weapons.copy()
    
    st.rerun()


### doing the calculations with the selected weapons
if any(st.session_state.wh_enabled_weapons):
    j = 0 #counting the actual amount of weapons used
    last_index_to_calc = len(st.session_state.wh_enabled_weapons) - 1 - st.session_state.wh_enabled_weapons[::-1].index(True)
    for i in range(len(st.session_state.wh_current_settings)):
        if st.session_state.wh_enabled_weapons[i]:
            current_settings = st.session_state.wh_current_settings[i]
            current_plot_result = (plot_results and i==last_index_to_calc) or plot_all_results
            if current_plot_result:
                st.write(f"Result for {st.session_state.wh_current_names_of_weapons[i]}")
            if np.sum(st.session_state.wh_troops):
                new_troops = complete_roll(
                current_settings, current_plot_result, show_distr, st.session_state.wh_current_troops[j], plot_sep, plot_sum, inv_distr
                )
                if len(st.session_state.wh_current_troops) < sum(st.session_state.wh_enabled_weapons):
                    st.session_state.wh_current_troops.append(new_troops)
            else:        
                complete_roll(
                    current_settings, current_plot_result, show_distr, st.session_state.wh_troops, plot_sep, plot_sum, inv_distr
                )
            j+=1