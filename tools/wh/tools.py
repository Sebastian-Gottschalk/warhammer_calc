import streamlit as st

class Default_weapon:
    default_wh_weapon = {
        "num_dice_att" : 0, "dice_size_att" : 1, "modifier_att" : 3,
        "start_distr" : [0,0,0,1],
        "num_dice_dmg" : 0, "dice_size_dmg" : 1, "modifier_dmg" : 3,
        "damage_distr" : [0,0,0,1],
        "dice_threshhold_1" : 4, "dice_threshhold_2" : 4,"dice_threshhold_3" : 4,
        "reroll": False, "reroll_hit": 0, "reroll_wound" : 0,
        "sustained_hits" : False, "sustained_hits_nr" : 0,
        "lethal_hits" : False, "dev_wounds" : False,"dev_wounds_overspill" : False, "torrent" : False,
        "crit_modifier" : False, "hit_roll_crit" : 6, "wound_roll_crit" : 6,
        "feel_no_pain_setting" : False, "feel_no_pain" : 6, "fnp_checkbox_mortals": False, "feel_no_pain_2" : 6
    }

class Options:
    DICE_SIZES_ATT = [3,6]
    DICE_SIZES_WND = [3,6]
    REROLL_OPTIONS = ["No reroll", "Reroll 1s", "Reroll all", "Fish for crits", "Fish for hits"]

def add_weapon(name):
    st.session_state.wh_number_of_weapons +=1
    if name == "default":
        st.session_state.wh_names_of_weapons.append(f"Weapon Nr. {st.session_state.wh_number_of_weapons}")
        st.session_state.wh_default_weapon_values.append(None)
    else:
        st.session_state.wh_names_of_weapons.append(name)
        st.session_state.wh_default_weapon_values.append(st.session_state.wh_saved_weapons[name])

def remove_weapon():
    if st.session_state.wh_number_of_weapons >1:
        st.session_state.wh_number_of_weapons -=1
        st.session_state.wh_names_of_weapons.pop()
        st.session_state.wh_default_weapon_values.pop()

def save_weapon(name, settings):
    st.session_state.wh_saved_weapons[name] = settings