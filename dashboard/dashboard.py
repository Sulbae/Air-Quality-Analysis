import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

url = "https://raw.githubusercontent.com/Sulbae/Air-Quality-Analysis/main/dashboard/all_data.csv"
data = pd.read_csv(url)
data["datetime"] = pd.to_datetime(data["datetime"])

data = data.round(decimals=2)

## Date Range
min_date = data["datetime"].min()
max_date = data["datetime"].max()

st.title("Air Quality in China in Tahun 2013 - 2017")

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    start_date, end_date = st.date_input(
        label="Rentang Waktu", min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Function untuk membuat dataframe
def create_daily_averages(df, pollutant):
    daily_averages = df.groupby(by=["datetime", "station"])[pollutant].mean()
    daily_averages = daily_averages.reset_index()
    return daily_averages

def combine_daily_data(df):
    daily_PM2_5 = create_daily_averages(df, "PM2_5")
    daily_PM10 = create_daily_averages(df, "PM10")
    daily_NO2 = create_daily_averages(df, "NO2")
    daily_SO2 = create_daily_averages(df, "SO2")

    combined_df = daily_PM2_5.merge(daily_PM10, on=["datetime", "station"], suffixes=("PM2_5", "PM10")) \
                              .merge(daily_NO2, on=["datetime", "station"]) \
                              .merge(daily_SO2, on=["datetime", "station"])

    combined_df = combined_df.groupby(["datetime", "station"]).mean()
    combined_df = combined_df.reset_index()
    return combined_df

def create_level_df(df):
    average_pollution_level = df.groupby(['station', 'category'])[['SO2','PM2_5', 'PM10',"NO2"]].mean()
    average_pollution_level = df.reset_index()
    return average_pollution_level


# Filter

main_df = data[(data["datetime"] >= str(start_date)) & 
                (data["datetime"] <= str(end_date))]

## Kategori
custom_category = ["Bahaya", "Tidak Sehat", "Sedang", "Baik"]

selected_stations = st.sidebar.multiselect("Select Stations", ["All Station"] + list(data["station"].unique()))

selected_category = st.sidebar.selectbox("Select Category", ["All Category"] + list(data["category"].unique()), index=0)

if "All Station" not in selected_stations:
    data = data[data["station"].isin(selected_stations)]
if selected_category != "All Category":
    data = data[data["category"] == selected_category]


# Membuat Dataframe
daily_all_data = combine_daily_data(main_df)
categorize_data = create_level_df(main_df)

# Visualisasi

st.header("Pollutant Concentration")

fig, axes = plt.subplots(2, 2, figsize=(20, 14))

pollutants = ["PM2_5", "PM10", "NO2", "SO2"]

for i, pollutant in enumerate(pollutants, 1):
    ax = plt.subplot(2, 2, i)
    sns.lineplot(data=daily_all_data, x="datetime", y=pollutant, hue="station", ax=ax)
    ax.set_title(f"{pollutant} Levels Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Pollutant Level")
    ax.legend(title="Station", loc="upper right", bbox_to_anchor=(1.2, 1))


plt.tight_layout()
st.pyplot(fig)

# Visualisasi barplot

st.header("Level of Air Quality")

fig, axes = plt.subplots(2, 2, figsize=(16, 10))

for i, ax in enumerate(axes.flatten()):
    sns.barplot(data=categorize_data, x="station", y=pollutants[i], hue="category", palette="viridis", ax=ax)
    ax.set_title(f"Average {pollutants[i]} Levels by Station and Category")
    ax.set_xlabel("Station")
    ax.set_ylabel(f"Average {pollutants[i]} Level")
    ax.legend(title="Category", loc="upper right", bbox_to_anchor=(1.3, 1))
    ax.set_xticks(ax.get_xticks())
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

plt.tight_layout()
st.pyplot(fig)

st.caption("Copyright (c) Bangkit 2024")

