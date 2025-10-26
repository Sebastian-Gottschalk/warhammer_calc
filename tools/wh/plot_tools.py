import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import base64



def plot_result(hit_roll, auto_crit, col, title, custom_text = None):
    plot_roll = get_threshhold_plot(hit_roll)
    if not auto_crit:

        fig, ax = plt.subplots()
        ax.bar(range(len(plot_roll)),plot_roll)
        ax.set_xticks(range(0,len(plot_roll),np.max([1,len(plot_roll)//10])))
        ax.set_title(title+" roll")
        ax.set_ylabel("Density")
        ax2 = ax.twinx()
        ax2.plot(range(len(plot_roll)), np.cumsum(plot_roll), color='blue', marker='o', linestyle='-', label='Probability')
        ax2.set_ylabel('Distribution')
        ax2.set_ylim([0,1])
        col.pyplot(fig)
        expected_2 = 0
        for i in range(len(hit_roll)):
            expected_2 += i*hit_roll[i]
        if custom_text:
            return f"Expected nr of {custom_text}: {np.round(expected_2,3)}"
        return f"Expected nr of {title}s: {np.round(expected_2,3)}"
    else:
        hits = hit_roll.sum(axis=1)
        crits = hit_roll.sum(axis=0)
        if len(hits)>len(crits):
            crits = np.pad(crits, (0, len(hits)-len(crits)), mode="constant")
        
        [hits_plot, crits_plot] = get_threshhold_plot([hits,crits], multi_list=True)
        
        width = 0.35
        fig, ax = plt.subplots()
        ax.bar(np.arange(len(hits_plot))-width/2,hits_plot,width, label = "Hits", color = "blue")
        ax.bar(np.arange(len(hits_plot))+width/2,crits_plot,width, label = "Crits", color = "red")
        ax.set_xticks(range(0,len(hits_plot)+1,np.max([1,len(hits_plot)//10])))
        ax.set_title(title+" roll")
        ax.set_ylabel("Density")
        ax2 = ax.twinx()
        ax2.plot(range(len(hits_plot)), np.cumsum(hits_plot), color='blue', marker='o', linestyle='-', label='Hits')
        ax2.plot(range(len(crits_plot)), np.cumsum(crits_plot), color='red', marker='o', linestyle='-', label='Crits')
        ax2.set_ylabel('Distribution')
        ax2.set_ylim([0,1])
        ax.legend(loc = "upper left")
        st.pyplot(fig)
        expected_1 = 0
        expected_1_2 = 0
        for i in range(len(hits)):
            expected_1 += i*hits[i]
            expected_1_2 += i*crits[i]
        return f"Expected nr of {title}s / crits: {np.round(expected_1,3)} / {np.round(expected_1_2,3)}"


def get_threshhold_plot(dice_roll, threshhold = 0.999, multi_list = False):
    if not multi_list:
        if np.sum(dice_roll)<=0.999:
            return dice_roll
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
    

def show_kroot_1():
    side_bg = "img/kroot.png"
    side_bg_ext = "png"
    with open(side_bg, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] > div:first-child {{
            background: url(data:image/{side_bg_ext};base64,{encoded_string});
            background-size : contain;
            background-repeat: no-repeat;
            background-position: center 75%;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def show_kroot_2():
    side_bg = "img/kroot_2.png"
    side_bg_ext = "png"
    with open(side_bg, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: url(data:image/{side_bg_ext};base64,{encoded_string});
            background-size : 70%;
            background-repeat: no-repeat;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )