import streamlit as st
import os
from tools.kt.gen import *



'''
To do list:
    - Handle attacks (Ranged):
        - Nr Attack Dice
        - Hit on / Crit on (Lethal)
        - DMG normal / crit
        - possible extra rules:
            - Devastating
            - Piercing
        - Defense Dice
    - Melee?

Variables to add:
    - Session state
        - kt_number_of_weapons
        - kt_current_settings_wo_calc / with calc
        - kt_names_of_weapons
    - default_weapon
'''





st.set_page_config(
    page_title="Work in Progress",
    page_icon="🐗",
)

if st.checkbox("Debug Session state"):
    st.session_state


all_settings = []
all_enabled = []

all_right_columns = []
# Setting up the Interface to have the user select stats ktile saving them in variables
for i in range(st.session_state.kt_number_of_weapons):
    # read the currently saved value from the session state
    default_values = st.session_state.kt_current_settings_wo_calc[i]
    
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
    enabled = left.checkbox(" ", key=f"kt_enabled_{i}", value = True)

    # Markdown to set the background of expander objects
    middle.markdown(
        """
        <style>
        /* Style the expander container */
        div[data-testid="stExpander"] {
            background-color: rgba(0, 0, 0, 0.8) !important;  /* Dark gray opaque */
            border-radius: 8px !important;
            padding: 0 !important;
            color: ktite !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Building the Options for the user to choose and saving the resulting weapon in a variable
    with middle.expander(f"{i+1} - {st.session_state.kt_names_of_weapons[i]}"):
        left,middle, col_save = st.columns([7,1,1])
        name = left.text_input("Name",value = st.session_state.kt_names_of_weapons[i], key=f"kt_enter_name_{i}")
        weapon_kind = middle.selectbox(" ",Options.WEAPON_OPTIONS, index = default_values["weapon_kind"],key = f"kt_weapon_kind_{i}")

        if weapon_kind == "Melee":
            st.write("Melee is currently not supported")

        if name != st.session_state.kt_names_of_weapons[i]:
            st.session_state.kt_names_of_weapons[i] = name
            st.rerun()

        main_col_1, main_col_2 = st.columns(2)

        _,col_title_1,_ = main_col_1.columns([0.25,1,0.25])
        with col_title_1:
            st.title("Attack Dice")
            num_dice_att = st.number_input("Nr. of Dice", min_value = 1, value = )

        _,coll1,_, coll2,_, coll3,_ = main_col_1.columns([0.25,1,0.125,0.75,0.125,1,0.25])
        with coll1:
            num_dice_att = st.number_input("Dice", min_value=0, value=default_values["num_dice_att"], key=f"kt_num_dice_1_{i}")
        with coll2:
            dice_size_att = int(st.radio("_", ["W"+str(number) for number in Options.DICE_SIZES_ATT], key=f"kt_dice_size_1_{i}", label_visibility = "hidden", index = default_values["dice_size_att"])[1:])
        with coll3:
            modifier_att = st.number_input("Modifier", value=default_values["modifier_att"], key=f"kt_modifier_1_{i}", min_value=0)

        start_distr = get_dicesum(num_dice_att, modifier_att, dice_size_att)

        _,col_title_2,_ = main_col_2.columns([0.125,1,0.125])
        with col_title_2:
            st.title("Damage Profile")

        _,colllll1,_, colllll2,_, colllll3,_ = main_col_2.columns([0.25,1,0.125,0.75,0.125,1,0.25])
        with colllll1:
            num_dice_dmg = st.number_input("Dice", min_value=0, value=default_values["num_dice_dmg"], key=f"kt_num_dice_2_{i}")
        with colllll2:
            dice_size_dmg = int(st.radio("_2", ["W"+str(number) for number in Options.DICE_SIZES_WND], key=f"kt_dice_size_2_{i}",index=default_values["dice_size_dmg"], label_visibility = "hidden")[1:])
        with colllll3:
            modifier_dmg = st.number_input("Modifier", value=default_values["modifier_dmg"], key=f"kt_modifier_2_{i}", min_value=0)
            
        damage_distr = get_dicesum(num_dice_dmg, modifier_dmg, dice_size_dmg)

        if fight_troop:
            co1, co2, co3,co4 = st.columns(4)
        else:
            co1, co2, co4 = st.columns(3)
        
        with co1:
            dice_threshhold_1 = st.number_input("Hitting on",2,6,key=f"kt_hitting_on_{i}", value=default_values["dice_threshhold_1"])
        
        if fight_troop:
            with co2:
                strength = st.number_input("Strength",1,50, value=default_values["strength"], key=f"kt_wounding_on_{i}")
            with co3:
                modifier = st.number_input("Modifier to wound", -5,5,value = default_values["modifier"], key = f"modifier_{i}")
            with co4:
                ap = st.number_input("AP",0,6,value = default_values["ap"], key=f"ap_{i}")
                dice_threshhold_3 = min([troops_save + ap, 6])
                if invul_melee:
                    if weapon_kind == "Melee": # melee
                        dice_threshhold_3 = min([dice_threshhold_3, invul_melee])
                    elif weapon_kind == "Ranged": # ranged
                        dice_threshhold_3 = min([dice_threshhold_3, invul_ranged])
        else:
            with co2:
                dice_threshhold_2 = st.number_input("Wounding on",2,6, value=default_values["dice_threshhold_2"], key=f"kt_wounding_on_{i}")
            strength = default_values["strength"]
            modifier = default_values["modifier"]
            ap = default_values["ap"]
            with co4:
                dice_threshhold_3 = st.number_input("Saving on",2,7, value=default_values["dice_threshhold_3"], key=f"kt_saving_on_{i}")
        
        if fight_troop:
            col1,col2,col3,col4,col5,col6,col7,col8,col9 = st.columns(9)
        else:
            col1,col2,col3,col4,col5,col6,col7 = st.columns(7)
        dev_wounds_overspill = False
        
        reroll = col1.checkbox("Rerolls", key=f"kt_rerolls_{i}", value = default_values["reroll"])
        if reroll:
            rerolls_hit = col1.selectbox("Hit Roll",Options.REROLL_OPTIONS , key=f"kt_hit_roll_{i}", index=default_values["reroll_hit"])
            rerolls_wound = col1.selectbox("Wound Roll", Options.REROLL_OPTIONS, key=f"kt_wound_roll_{i}", index = default_values["reroll_wound"])
        else: # default values for saving
            rerolls_hit = "No reroll"
            rerolls_wound = "No reroll"
        
        sustained_hits = col2.checkbox("Sustained hits", key=f"kt_sustained_hits_{i}", value = default_values["sustained_hits"])
        if sustained_hits:
            sus_key = f"kt_sustained_hits_nr_{i}"
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
        
        lethal_hits = col3.checkbox("Lethal Hits", key=f"kt_lethal_hits_{i}", value = default_values["lethal_hits"])
        dev_wounds = col4.checkbox("Dev Wounds", key=f"kt_dev_wounds_{i}", value = default_values["dev_wounds"])
        torrent = col5.checkbox("Torrent", key=f"kt_torrent_{i}", value = default_values["torrent"])
        crit_modifier= col6.checkbox("Crit Modifier", key=f"kt_modify_crit_{i}", value = default_values["crit_modifier"])        
        fnp_checkbox =  col7.checkbox("Feel No Pain", key=f"kt_feel_no_pain_{i}", value = default_values["feel_no_pain_setting"])
        
        if dev_wounds:
            dev_wounds_overspill = col4.checkbox("Overspill", key=f"kt_dev_wounds_overspill_{i}", value = default_values["dev_wounds_overspill"])
        if torrent: # the combination doesnt make sense and only screws up the plots
            lethal_hits = False
        if fnp_checkbox:
            feel_no_pain = col7.number_input("Normal FnP",2,7,value=default_values["feel_no_pain"],label_visibility="collapsed", key=f"kt_normal_fnp_{i}")
            fnp_checkbox_mortals = col7.checkbox("Different FnP on Mortals", key=f"kt_weird_stuff_{i}", value = default_values["fnp_checkbox_mortals"])
            if fnp_checkbox_mortals:
                feel_no_pain_2 = col7.number_input("DevWounds FnP",2,7,value=default_values["feel_no_pain_2"],label_visibility="collapsed")
            else:
                feel_no_pain_2 = feel_no_pain     
        else:
            feel_no_pain = 6
            feel_no_pain_2 = 6
            fnp_checkbox_mortals = False

        if fight_troop:
            if col8.checkbox("No saving throw", value = default_values["dice_threshhold_3"] == 7,key=f"kt_no_sv_throw_{i}"):
                dice_threshhold_3 = 7
            if col9.checkbox("Fixed value to hit", value = default_values["fixed_hit_thresh"] > 0, key = f"kt_fixed_value_{i}"):
                fix_hit_def_value = default_values["fixed_hit_thresh"] if default_values["fixed_hit_thresh"] else 4
                fix_hit = col9.number_input("Test",2,6, value = fix_hit_def_value, key = f"kt_fixed_value_nr_input_{i}")
            else:
                fix_hit = 0                
            dice_threshhold_2 = get_wound_threshhold(strength,toughness,modifier, fix_hit)
        else:
            fix_hit = 0

        if crit_modifier:
            hit_roll_crit = col6.number_input("Hit roll critting on",2,6,value=default_values["hit_roll_crit"], key=f"kt_hit_roll_crit_{i}")
            if hit_roll_crit<dice_threshhold_1:
                dice_threshhold_1 = hit_roll_crit
            wound_roll_crit = col6.number_input("Wound roll critting on", 2,6, value=default_values["wound_roll_crit"], key=f"kt_wound_roll_crit_{i}")
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
        button_key = f"kt_save_button_{i}"
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
        col_save.button("Save Weapon", on_click = save_weapon, args = [name, save_weapon_settings], key=button_key)
    
    # saving the weapon options and the fact if they are selected or not
    all_settings.append(save_weapon_settings)
    all_enabled.append(enabled)