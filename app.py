import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd

import theme
from analysis.thresholds import check_alerts
from analysis.metrics import calculate_kpis
from visuals.charts import line_chart, stacked_bar_chart, heatmap_chart

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Energy Consumption Monitor", layout="wide")
theme.apply_theme()
theme.header(
    "Energy Consumption Dashboard",
    "Multi-zone building energy tracking with anomaly alerts and KPI reporting.",
    eyebrow="Project · Facilities & energy",
)

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.header("1. Data Source")
data_source = st.sidebar.radio("Choose data source:", ["Use Sample Data", "Upload CSV"],
                               label_visibility="collapsed")

df = None

if data_source == "Use Sample Data":
    df = pd.read_csv("data/energy_data.csv", parse_dates=["timestamp"])
    st.sidebar.success("Sample data loaded (1,440 hourly readings)")
else:
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file, parse_dates=["timestamp"])
        st.sidebar.success(f"{len(df)} rows loaded")

ZONES = ["hvac", "lighting", "lobby", "mechanical_room", "kitchen"]

if df is not None:

    # ── Filters ───────────────────────────────────────────────
    st.sidebar.header("2. Filters")
    selected_zones = st.sidebar.multiselect(
        "Select zones:",
        ZONES,
        default=ZONES
    )

    st.sidebar.header("3. Cost Settings")
    cost_per_kwh = st.sidebar.slider(
        "Cost per kWh (€)", 
        min_value=0.05, 
        max_value=0.50, 
        value=0.15, 
        step=0.01
    )

    date_range = st.sidebar.date_input(
        "Date range:",
        value=[df["timestamp"].min().date(), df["timestamp"].max().date()]
    )

    # Apply date filter
    if len(date_range) == 2:
        df = df[
            (df["timestamp"].dt.date >= date_range[0]) &
            (df["timestamp"].dt.date <= date_range[1])
        ]

    if selected_zones and len(df) > 0:

        # ── KPI Cards ─────────────────────────────────────────
        st.subheader("Key Performance Indicators")
        kpis = calculate_kpis(df[["timestamp"] + selected_zones], cost_per_kwh)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown(theme.tile("Total consumption", f"{kpis['total_kwh']:,}", "kWh"), unsafe_allow_html=True)
        c2.markdown(theme.tile("Peak demand", f"{kpis['peak_kwh']}", "kWh in one hour"), unsafe_allow_html=True)
        c3.markdown(theme.tile("Daily average", f"{kpis['daily_avg']}", "kWh per day"), unsafe_allow_html=True)
        c4.markdown(theme.tile("Estimated cost", f"€{kpis['total_cost']:,.2f}", f"at €{cost_per_kwh:.2f} / kWh"),
                    unsafe_allow_html=True)
        c5.markdown(theme.tile("Top consumer", kpis['worst_zone'].replace("_", " ").title(), "highest total kWh"),
                    unsafe_allow_html=True)
        st.write("")

        # ── Line Chart ────────────────────────────────────────
        st.subheader("Consumption Over Time")
        st.plotly_chart(line_chart(df, selected_zones), width="stretch")

        # ── Stacked Bar Chart ─────────────────────────────────
        st.subheader("Daily Totals by Zone")
        st.plotly_chart(stacked_bar_chart(df, selected_zones), width="stretch")

        # ── Heatmap ───────────────────────────────────────────
        st.subheader("Consumption Heatmap")
        st.plotly_chart(heatmap_chart(df), width="stretch")

        # ── Alert Log ─────────────────────────────────────────
        st.subheader("Threshold Alert Log")
        alerts_df = check_alerts(df[["timestamp"] + selected_zones])

        if len(alerts_df) > 0:
            st.error(f"{len(alerts_df)} alerts triggered across selected zones")
            st.dataframe(alerts_df, width="stretch")
        else:
            st.success("No threshold violations in selected range")

    else:
        st.warning("Please select at least one zone from the sidebar.")

else:
    st.info("Select a data source to get started.")
