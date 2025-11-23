import streamlit as st
import pandas as pd
from tools.wh.gen import Options

@st.cache_data
def read_data(filename):
    data = pd.read_csv(f"wahapedia/data/{filename}.csv", delimiter= "|")
    return data

def read_profile(profile):
    if "+" in profile:
            profile = profile.split("+")
            modifier = int(profile[1])
            profile = profile[0].split("D")
            if profile[0]:
                num_dice = int(profile[0])
            else:
                num_dice = 1
            dice_size = int(profile[1])
    else:
        if "D" in profile:
            profile = profile.split("D")
            if profile[0]:
                num_dice = int(profile[0])
            else:
                num_dice = 1
            dice_size = int(profile[1])
            modifier = 0
        else:
            num_dice = 0
            dice_size = 6
            modifier = int(profile)
    return num_dice, dice_size, modifier


class csv_files():
    def __init__(self):
        self.factions = read_data("Factions")
        self.sheets = read_data("Datasheets")
        self.models = read_data("Datasheets_models")
        self.wargear = read_data("Datasheets_wargear")
        self.options = read_data("Datasheets_options")
        self.unit_comp = read_data("Datasheets_unit_composition")
        self.unit_cost = read_data("Datasheets_models_cost")

    def get_defensive_stats(self,name):
        id = self.sheets[self.sheets.name == name].iloc[0]["id"]
        current_model = self.models[self.models.datasheet_id == id].iloc[0]
        toughness = current_model["T"]
        save = int(current_model["Sv"][0])
        inv_save = 7 if current_model["inv_sv"] == "-" else int(current_model["inv_sv"])
        model_count = self.unit_cost[self.unit_cost["datasheet_id"] == id]["description"].apply(lambda x: sum([int(nr) for nr in x.split(" ") if nr.isnumeric()])).values.tolist()
        if model_count == [0]:
            model_count = [1]
        wounds = current_model["W"]
        return toughness, save, inv_save, model_count, wounds
    
    def get_offensive_stats(self,name, weapon_name):
        id = self.sheets[self.sheets.name == name].iloc[0]["id"]
        weapon = self.wargear[(self.wargear.datasheet_id == id) & (self.wargear.name == weapon_name)].iloc[0]
        attack_profile = weapon["A"]
        num_dice_att, dice_size_att, modifier_att = read_profile(attack_profile)
        damage_profile = weapon["D"]
        num_dice_dmg, dice_size_dmg, modifier_dmg = read_profile(damage_profile)
        dice_threshhold_1 = weapon["BS_WS"]
        if dice_threshhold_1 != dice_threshhold_1: # checking for nan values in the case of torrent
            dice_threshhold_1 = 4 # default value to display, doesnt matter for torrent
        else:
            dice_threshhold_1 = int(dice_threshhold_1)
        strength = weapon["S"]
        if strength.isnumeric():
            strength = int(strength)
        else: # weird Ork units that roll for strength, maybe include them one day
            strength = 6
        ap = -weapon["AP"]
        offensive_stats = {
            "num_dice_att":num_dice_att,
            "dice_size_att":Options.DICE_SIZES_ATT.index(dice_size_att),
            "modifier_att":modifier_att,
            "num_dice_dmg":num_dice_dmg,
            "dice_size_dmg":Options.DICE_SIZES_WND.index(dice_size_dmg),
            "modifier_dmg":modifier_dmg,
            "dice_threshhold_1":dice_threshhold_1,
            "strength" : strength,
            "ap" : ap
        }
        return offensive_stats
            
    def get_weapon_options(self, name):
        id = self.sheets[self.sheets.name == name].iloc[0]["id"]
        weapon_df = self.wargear[self.wargear.datasheet_id == id]
        return weapon_df["name"].values.tolist()
    
    @st.cache_data
    def get_faction_names(_self):
        return _self.factions["name"].values.tolist()
    
    @st.cache_data
    def get_faction_member(_self, faction):
        if faction:
            faction_code = _self.factions[_self.factions["name"] == faction].iloc[0]["id"]
            all_model_names = _self.sheets[_self.sheets["faction_id"] == faction_code]["name"].values.tolist()
        else:
            all_model_names = _self.sheets["name"].values.tolist()
        return all_model_names