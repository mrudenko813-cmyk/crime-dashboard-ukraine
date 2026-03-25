import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Злочинність у регіонах",
    page_icon="🚔",
    layout="wide"
)

st.markdown("""
<style>
.t1 {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 4px;
}
.t2 {
    font-size: 17px;
    color: #475569;
    margin-bottom: 18px;
}
.kartka {
    background-color: #f8fafc;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.kartka h3 {
    margin: 0;
    font-size: 16px;
}
.kartka p {
    margin: 8px 0 0 0;
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="t1">🚔 Злочинність у регіонах</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="t2">Вебзастосунок для аналізу категорій злочинів, регіонів, дат, карти та індексу криміногенності</div>',
    unsafe_allow_html=True
)

np.random.seed(42)

regions = ["Київ", "Львів", "Харків", "Одеса", "Дніпро"]
crime_types = ["Крадіжка", "Грабіж", "Шахрайство", "Напад", "Хуліганство"]

data = []
for _ in range(400):
    data.append({
        "Регіон": np.random.choice(regions),
        "Категорія злочину": np.random.choice(crime_types),
        "Дата": datetime(2025, 1, 1) + timedelta(days=np.random.randint(0, 365))
    })

df = pd.DataFrame(data)
df["Дата"] = pd.to_datetime(df["Дата"])
df["Місяць"] = df["Дата"].dt.strftime("%Y-%m")

st.sidebar.header("Фільтри")

selected_region = st.sidebar.selectbox("Оберіть регіон", ["Усі"] + regions)
selected_crime = st.sidebar.selectbox("Оберіть категорію злочину", ["Усі"] + crime_types)

min_date = df["Дата"].min().date()
max_date = df["Дата"].max().date()

selected_dates = st.sidebar.date_input(
    "Оберіть проміжок дат",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered = df.copy()

if selected_region != "Усі":
    filtered = filtered[filtered["Регіон"] == selected_region]

if selected_crime != "Усі":
    filtered = filtered[filtered["Категорія злочину"] == selected_crime]

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered = filtered[
        (filtered["Дата"].dt.date >= start_date) &
        (filtered["Дата"].dt.date <= end_date)
    ]

total_crimes = len(filtered)
unique_regions = filtered["Регіон"].nunique()
top_region = filtered["Регіон"].mode()[0] if not filtered.empty else "—"
crime_index = round(total_crimes / len(regions), 2)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="kartka">
            <h3>Загальна кількість злочинів</h3>
            <p>{total_crimes}</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kartka">
            <h3>Кількість охоплених регіонів</h3>
            <p>{unique_regions}</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kartka">
            <h3>Найбільш криміногенний регіон</h3>
            <p style="font-size:22px;">{top_region}</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="kartka">
            <h3>Індекс криміногенності</h3>
            <p>{crime_index}</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

left, right = st.columns([1.3, 1])

with left:
    st.subheader("Таблиця даних")
    st.dataframe(filtered.sort_values("Дата"), use_container_width=True)

with right:
    st.subheader("Кількість злочинів за регіонами")
    if not filtered.empty:
        region_stats = filtered["Регіон"].value_counts().reset_index()
        region_stats.columns = ["Регіон", "Кількість злочинів"]
        st.dataframe(region_stats, use_container_width=True)
    else:
        st.warning("Немає даних для відображення.")

st.markdown("---")

st.subheader("Динаміка злочинів")

if not filtered.empty:
    monthly_counts = filtered.groupby("Місяць").size()

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(monthly_counts.index, monthly_counts.values, marker="o")
    ax.set_title("Зміна кількості злочинів за місяцями")
    ax.set_xlabel("Місяць")
    ax.set_ylabel("Кількість злочинів")
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.warning("Немає даних для побудови графіка.")

st.markdown("---")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Розподіл злочинів за категоріями")
    if not filtered.empty:
        crime_counts = filtered["Категорія злочину"].value_counts()

        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ax2.bar(crime_counts.index, crime_counts.values)
        ax2.set_xlabel("Категорія злочину")
        ax2.set_ylabel("Кількість")
        ax2.set_title("Кількість злочинів за категоріями")
        plt.xticks(rotation=30)
        st.pyplot(fig2)
    else:
        st.warning("Немає даних для побудови діаграми.")

with chart_col2:
    st.subheader("Індекс криміногенності за регіонами")
    if not filtered.empty:
        crime_index_by_region = filtered["Регіон"].value_counts().reset_index()
        crime_index_by_region.columns = ["Регіон", "Індекс криміногенності"]
        st.dataframe(crime_index_by_region, use_container_width=True)
    else:
        st.warning("Немає даних для обчислення показника.")

st.markdown("---")

st.subheader("Карта злочинності")

region_coords = {
    "Київ": [50.45, 30.52],
    "Львів": [49.84, 24.03],
    "Харків": [49.99, 36.23],
    "Одеса": [46.48, 30.73],
    "Дніпро": [48.45, 34.98]
}

crime_map = folium.Map(location=[49.0, 31.0], zoom_start=6)

if not filtered.empty:
    counts = filtered["Регіон"].value_counts()

    for region, count in counts.items():
        folium.CircleMarker(
            location=region_coords[region],
            radius=8 + count / 4,
            popup=f"{region}: {count} злочинів",
            color="red",
            fill=True,
            fill_opacity=0.6
        ).add_to(crime_map)

st_folium(crime_map, width=1200, height=500)

st.markdown("---")
st.caption("Навчальний вебзастосунок для аналізу злочинності в регіонах України")
