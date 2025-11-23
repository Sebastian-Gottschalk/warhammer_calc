import streamlit as st

class Default_weapon:
    '''
    Class for the Default Weapon Options to use when creating a default weapon
    '''
    default_wh_weapon = {
        "weapon_kind" : 1,
        "num_dice_att" : 0, "dice_size_att" : 1, "modifier_att" : 3,
        "start_distr" : [0,0,0,1],
        "num_dice_dmg" : 0, "dice_size_dmg" : 1, "modifier_dmg" : 3,
        "damage_distr" : [0,0,0,1],
        "dice_threshhold_1" : 4,"strength" : 6, "modifier" : 0, "dice_threshhold_2" : 4,
        "ap": 0, "dice_threshhold_3" : 4,
        "reroll": False, "reroll_hit": 0, "reroll_wound" : 0,
        "sustained_hits" : False, "sustained_hits_nr" : 0,
        "lethal_hits" : False, "dev_wounds" : False,"dev_wounds_overspill" : False, "torrent" : False,
        "crit_modifier" : False, "hit_roll_crit" : 6, "wound_roll_crit" : 6,
        "feel_no_pain_setting" : False, "feel_no_pain" : 6, "fnp_checkbox_mortals": False, "feel_no_pain_2" : 6,
        "fixed_hit_thresh" : 0
    }

class Options:
    '''
    Class for some Options for different Dice sizes etc
    '''
    DICE_SIZES_ATT = [3,6]
    DICE_SIZES_WND = [3,6]
    REROLL_OPTIONS = ["No reroll", "Reroll 1s", "Reroll all", "Fish for crits"] #, "Fish for hits"]
    WEAPON_OPTIONS = ["Melee", "Ranged"]

def setup_40k():
    from wahapedia.db_interaction.interact import csv_files

    st.set_page_config(
        layout="wide", 
        page_title = "40K",
        page_icon = ":space_invader:"
    )

    st.session_state.wh_number_of_weapons = 1
    st.session_state.wh_current_settings = [Default_weapon.default_wh_weapon]
    st.session_state.wh_troops = 0
    st.session_state.wh_default_weapon_values = [None]
    st.session_state.wh_saved_weapons = {}
    st.session_state.wh_enabled_weapons = [True]
    st.session_state.wh_names_of_weapons = ["Weapon Nr. 1"]
    st.session_state.wh_current_names_of_weapons = st.session_state.wh_names_of_weapons.copy()
    st.session_state.wh_current_settings_wo_calc = st.session_state.wh_current_settings.copy()
    st.session_state.wh_expanders = [False]
    st.session_state.wh_expander_tracker = [0]
    st.session_state.wh_total_weapons = 1
    st.session_state.wh_files = csv_files()
    st.session_state.wh_model_amount = [None]

def add_weapon(name):
    st.session_state.wh_number_of_weapons +=1
    st.session_state.wh_total_weapons +=1
    if name == "default":
        st.session_state.wh_names_of_weapons.append(f"Weapon Nr. {st.session_state.wh_number_of_weapons}")
        st.session_state.wh_default_weapon_values.append(None)
        st.session_state.wh_current_settings_wo_calc.append(Default_weapon.default_wh_weapon)
    else:
        st.session_state.wh_names_of_weapons.append(name)
        st.session_state.wh_default_weapon_values.append(st.session_state.wh_saved_weapons[name])
        st.session_state.wh_current_settings_wo_calc.append(st.session_state.wh_saved_weapons[name])
    st.session_state.wh_expanders.append(False)
    st.session_state.wh_expander_tracker.append(st.session_state.wh_total_weapons)

def remove_weapon():
    if st.session_state.wh_number_of_weapons >1:
        st.session_state.wh_number_of_weapons -=1
        st.session_state.wh_names_of_weapons.pop()
        st.session_state.wh_default_weapon_values.pop()
        st.session_state.wh_current_settings_wo_calc.pop()
        st.session_state.wh_expanders.pop()
        st.session_state.wh_expander_tracker.pop()

def save_weapon(name, settings):
    st.session_state.wh_saved_weapons[name] = settings

def swap_weapons(settings,old_index, new_index):
    st.session_state.wh_current_settings_wo_calc = settings
    st.session_state.wh_current_settings_wo_calc[old_index], st.session_state.wh_current_settings_wo_calc[new_index] = (
        st.session_state.wh_current_settings_wo_calc[new_index], st.session_state.wh_current_settings_wo_calc[old_index]
    )
    st.session_state.wh_names_of_weapons[old_index], st.session_state.wh_names_of_weapons[new_index] = (
        st.session_state.wh_names_of_weapons[new_index], st.session_state.wh_names_of_weapons[old_index]
    )
    st.session_state.wh_expanders[old_index], st.session_state.wh_expanders[new_index] = (
        st.session_state.wh_expanders[new_index], st.session_state.wh_expanders[old_index]
    )
    st.session_state.wh_expander_tracker[old_index], st.session_state.wh_expander_tracker[new_index] = (
        st.session_state.wh_expander_tracker[new_index], st.session_state.wh_expander_tracker[old_index]
    )

def delete_current_weapon(settings,idx):
    settings.pop(idx)
    st.session_state.wh_number_of_weapons -=1
    st.session_state.wh_names_of_weapons.pop(idx)
    st.session_state.wh_default_weapon_values.pop(idx)
    st.session_state.wh_current_settings_wo_calc.pop(idx)
    st.session_state.wh_expanders.pop(idx)
    st.session_state.wh_expander_tracker.pop(idx)

def update_button_session_state(default_values,k):
    st.session_state[f"wh_num_dice_1_{k}"] = default_values["num_dice_att"]
    st.session_state[f"wh_dice_size_1_{k}"] = "W"+str(Options.DICE_SIZES_ATT[default_values["dice_size_att"]])
    st.session_state[f"wh_modifier_1_{k}"] = default_values["modifier_att"]
    st.session_state[f"wh_dice_size_2_{k}"] = "W" + str(Options.DICE_SIZES_ATT[default_values["dice_size_dmg"]])
    st.session_state[f"wh_num_dice_2_{k}"] = default_values["num_dice_dmg"]
    st.session_state[f"wh_modifier_2_{k}"] = default_values["modifier_dmg"]
    st.session_state[f"wh_hitting_on_{k}"] = default_values["dice_threshhold_1"]
    st.session_state[f"wh_wounding_on_{k}"] = default_values["strength"]
    st.session_state[f"wh_modifier_{k}"] = default_values["modifier"]
    st.session_state[f"wh_ap_{k}"] = default_values["ap"]