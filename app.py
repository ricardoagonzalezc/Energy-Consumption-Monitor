import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
from analysis.thresholds import check_alerts
from analysis.metrics import calculate_kpis
from visuals.charts import line_chart, stacked_bar_chart, heatmap_chart

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Energy Consumption Monitor", layout="wide")
st.title("⚡ Energy Consumption Monitor")
st.markdown("Multi-zone building energy tracking with anomaly alerts and KPI reporting.")

# ── Sidebar ───────────────────────────────────────────────────
st.sidebar.header("1. Data Source")
data_source = st.sidebar.radio("Choose data source:", ["Use Sample Data", "Upload CSV"])

df = None

if data_source == "Use Sample Data":
    df = pd.read_csv("data/energy_data.csv", parse_dates=["timestamp"])
    st.sidebar.success("Sample data loaded (1,440 hourly readings)")
else:
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file, parse_dates=["timestamp"])
        st.sidebar.success(f"{len(df)} rows loaded")

ZONES = ["hvac", "lighting", "lobby", "it_room", "kitchen"]

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
        st.subheader("📊 Key Performance Indicators")
        kpis = calculate_kpis(df[["timestamp"] + selected_zones], cost_per_kwh)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Consumption", f"{kpis['total_kwh']:,} kWh")
        c2.metric("Peak Demand",       f"{kpis['peak_kwh']} kWh")
        c3.metric("Daily Average",     f"{kpis['daily_avg']} kWh")
        c4.metric("Estimated Cost",    f"€{kpis['total_cost']:,}")
        c5.metric("Top Consumer",      kpis['worst_zone'].replace("_", " ").title())

        # ── Line Chart ────────────────────────────────────────
        st.subheader("📈 Consumption Over Time")
        st.plotly_chart(line_chart(df, selected_zones), use_container_width=True)

        # ── Stacked Bar Chart ─────────────────────────────────
        st.subheader("📊 Daily Totals by Zone")
        st.plotly_chart(stacked_bar_chart(df, selected_zones), use_container_width=True)

        # ── Heatmap ───────────────────────────────────────────
        st.subheader("🗓️ Consumption Heatmap")
        st.plotly_chart(heatmap_chart(df), use_container_width=True)

        # ── Alert Log ─────────────────────────────────────────
        st.subheader("🚨 Threshold Alert Log")
        alerts_df = check_alerts(df[["timestamp"] + selected_zones])

        if len(alerts_df) > 0:
            st.error(f"{len(alerts_df)} alerts triggered across selected zones")
            st.dataframe(alerts_df, use_container_width=True)
        else:
            st.success("✅ No threshold violations in selected range")

    else:
        st.warning("Please select at least one zone from the sidebar.")

else:
    st.info("👈 Select a data source in the sidebar to get started.")


    