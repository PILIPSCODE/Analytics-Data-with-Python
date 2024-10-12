import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import pandas as pd

sns.set(style="dark")


def calculate_aqi(AQI):
    if AQI >= 301:
        return "Hazardous"
    elif AQI >= 201:
        return "Very Unhealthy"
    elif AQI >= 151:
        return "Unhealthy"
    elif AQI >= 101:
        return "Unhealthy for Sensitive Groups"
    elif AQI >= 51:
        return "Moderate"
    else:
        return "Good"


def calculate_pm25(pm25_value):
    if pm25_value >= 250.4:
        return "Hazardous"
    elif pm25_value >= 150.4:
        return "Very Unhealthy"
    elif pm25_value >= 55.5:
        return "Unhealthy for Sensitive Groups"
    elif pm25_value >= 35.5:
        return "Unhealthy"
    elif pm25_value >= 12.1:
        return "Moderate"
    else:
        return "Good"


def calculate_pm10(pm10_value):
    if pm10_value >= 425.0:
        return "Hazardous"
    elif pm10_value >= 355.0:
        return "Very Unhealthy"
    elif pm10_value >= 255.0:
        return "Unhealthy for Sensitive Groups"
    elif pm10_value >= 155.0:
        return "Unhealthy"
    elif pm10_value >= 55.0:
        return "Moderate"
    else:
        return "Good"


def Season(month):
    if (
        month == "April"
        or month == "May"
        or month == "June"
        or month == "July"
        or month == "August"
    ):
        return "Summer"
    elif month == "November" or month == "December" or month == "January":
        return "Winter"
    elif month == "September" or month == "October":
        return "Autumn"
    else:
        return "Spring"


def create_monthly_AQI_df(main_df):
    monthly_AQI_df = main_df.resample(rule="ME", on="date").agg(
        {
            "AQI": "median",
        }
    )
    monthly_AQI_df.index = monthly_AQI_df.index.strftime("%B")

    monthly_Station = monthly_AQI_df.groupby(by="date")["AQI"].median().reset_index()
    monthly_Station["category"] = monthly_Station["AQI"].apply(
        lambda x: calculate_aqi(x)
    )

    month_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    monthly_Station["date"] = pd.Categorical(
        monthly_Station["date"], categories=month_order, ordered=True
    )

    monthly_Station_sorted = monthly_Station.sort_values("date").reset_index(drop=True)

    monthly_Station_sorted["season"] = monthly_Station_sorted["date"].apply(
        lambda x: Season(x)
    )

    return monthly_Station_sorted


def create_AQI_by_station(main_df):
    AQI_by_Station = (
        main_df.groupby(by="station")["AQI"]
        .median()
        .sort_values(ascending=True)
        .reset_index()
    )
    AQI_by_Station["category"] = AQI_by_Station["AQI"].apply(lambda x: calculate_aqi(x))
    return AQI_by_Station


def create_AQI_category(main_df):
    main_df["category"] = main_df["AQI"].apply(lambda x: calculate_aqi(x))

    AQI_Category_df = main_df.groupby(by="category").agg({"AQI": "count"}).reset_index()

    return AQI_Category_df


def create_aqi_categoryPM25(main_df):
    main_df["PM2.5_Category"] = main_df["PM2.5"].apply(lambda x: calculate_pm25(x))

    AQI_by_PM25 = main_df.groupby(by="PM2.5_Category")["PM2.5"].count().reset_index()

    return AQI_by_PM25


def create_aqi_categoryPM10(main_df):
    main_df["PM10_Category"] = main_df["PM10"].apply(lambda x: calculate_pm10(x))

    AQI_by_PM10 = main_df.groupby(by="PM10_Category")["PM10"].count().reset_index()
    return AQI_by_PM10


all_df = pd.read_csv("all_data.csv")


datetime_columns = ["date"]
all_df.sort_values(by="date", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])


min_date = all_df["date"].min()
max_date = all_df["date"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image(
        "https://tse2.mm.bing.net/th?id=OIP.NC8DHNajFL0wpAk0-SXCLAHaHa&pid=Api&P=0&h=180"
    )

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

main_df = all_df[
    (all_df["date"] >= str(start_date)) & (all_df["date"] <= str(end_date))
]

monthly_AQI_df = create_monthly_AQI_df(main_df)
AQI_by_station_df = create_AQI_by_station(main_df)
AQI_category_df = create_AQI_category(main_df)
AQI_categoryPM25_df = create_aqi_categoryPM25(main_df)
AQI_categoryPM10_df = create_aqi_categoryPM10(main_df)


st.header("AQI Dashboard :sparkles:")
st.subheader("Air Quality all Station")
colors = ["#ffcc00", "#ff6666"]
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    y="station", x="AQI", hue="category", palette=colors, data=AQI_by_station_df
)
st.pyplot(fig)

st.subheader("Comparison of Air Quality Between All Season")
colour = ["#3DC8EF", "#099E42", "#F8060A", "#FD7D00"]

fig, ax = plt.subplots(figsize=(20, 5))
sns.lineplot(
    x="date",
    y="AQI",
    data=monthly_AQI_df,
    markerfacecolor="limegreen",
    linewidth=4,
    color="black",
    marker="o",
    markersize=9,
)


sns.barplot(
    y="AQI",
    x="date",
    color="#D3D3D3",
    hue="season",
    palette=colour,
    data=monthly_AQI_df,
)
plt.show()
st.pyplot(fig)


colors = ["#2FCA30", "#212121", "#ffcc00", "#FE0000", "#ff6666", "#9B30FF"]
sizes1 = AQI_category_df["AQI"]
labels1 = AQI_category_df["category"]

sizes2 = AQI_categoryPM10_df["PM10"]
labels2 = AQI_categoryPM10_df["PM10_Category"]

sizes3 = AQI_categoryPM25_df["PM2.5"]
labels3 = AQI_categoryPM25_df["PM2.5_Category"]

st.subheader("Distribution of AQI Categories")
fig, ax = plt.subplots(figsize=(10, 7))
ax.pie(sizes1, labels=labels1, colors=colors, autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.pyplot(fig)


plt.clf()

# Distribusi PM10
st.subheader("Distribution of PM10 Categories")
fig, ax = plt.subplots(figsize=(10, 7))
ax.pie(sizes2, labels=labels2, colors=colors, autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.pyplot(fig)


plt.clf()


st.subheader("Distribution of PM2.5 Categories")
fig, ax = plt.subplots(figsize=(10, 7))
ax.pie(sizes3, labels=labels3, colors=colors, autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.pyplot(fig)
