import streamlit as st
import pandas as pd

@st.cache_data
def read_data(filename):
    data = pd.read_csv(f"wahapedia/data/{filename}.csv", delimiter= "|")
    return data


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
        wounds = current_model["W"]
        return toughness, save, inv_save, model_count, wounds
    
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