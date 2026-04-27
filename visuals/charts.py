import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

ZONE_COLORS = {
    "hvac":     "#1f77b4",
    "lighting": "#ff7f0e",
    "lobby":    "#2ca02c",
    "it_room":  "#d62728",
    "kitchen":  "#9467bd"
}

def line_chart(df, zones):
    """Time-series line chart for selected zones."""
    fig = go.Figure()
    for zone in zones:
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df[zone],
            mode="lines",
            name=zone.replace("_", " ").title(),
            line=dict(color=ZONE_COLORS[zone])
        ))
    fig.update_layout(
        title="Energy Consumption Over Time",
        xaxis_title="Timestamp",
        yaxis_title="kWh",
        legend=dict(x=0.01, y=0.99)
    )
    return fig

def stacked_bar_chart(df, zones):
    """Daily stacked bar chart broken down by zone."""
    df = df.copy()
    df["date"] = df["timestamp"].dt.date
    daily = df.groupby("date")[zones].sum().reset_index()

    fig = go.Figure()
    for zone in zones:
        fig.add_trace(go.Bar(
            x=daily["date"],
            y=daily[zone],
            name=zone.replace("_", " ").title(),
            marker_color=ZONE_COLORS[zone]
        ))
    fig.update_layout(
        barmode="stack",
        title="Daily Energy Consumption by Zone",
        xaxis_title="Date",
        yaxis_title="kWh",
        legend=dict(x=0.01, y=0.99)
    )
    return fig

def heatmap_chart(df):
    """Heatmap of average consumption by hour of day vs day of week."""
    df = df.copy()
    df["hour"]    = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.day_name()
    df["total"]   = df[["hvac", "lighting", "lobby", "it_room", "kitchen"]].sum(axis=1)

    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = df.groupby(["weekday", "hour"])["total"].mean().unstack()
    pivot = pivot.reindex(order)

    fig = px.imshow(
        pivot,
        labels=dict(x="Hour of Day", y="Day of Week", color="Avg kWh"),
        title="Average Energy Consumption Heatmap",
        color_continuous_scale="RdYlGn_r",
        aspect="auto"
    )
    return fig

