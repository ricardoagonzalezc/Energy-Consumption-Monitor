import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

import theme

# One fixed colour per zone (blueprint palette, always in this order), so a zone keeps
# its colour in every chart no matter which zones are selected.
ZONE_COLORS = {
    "hvac":            theme.AMBER,
    "lighting":        theme.SKY,
    "lobby":           theme.MINT,
    "mechanical_room": theme.CORAL,
    "kitchen":         theme.LAVENDER,
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
            line=dict(color=ZONE_COLORS[zone], width=1.5)
        ))
    fig.update_layout(xaxis_title="Timestamp", yaxis_title="kWh", height=420)
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
            marker=dict(color=ZONE_COLORS[zone], line=dict(color=theme.PANEL, width=1))
        ))
    fig.update_layout(barmode="stack", xaxis_title="Date", yaxis_title="kWh", height=420)
    return fig

def heatmap_chart(df):
    """Heatmap of average consumption by hour of day vs day of week."""
    df = df.copy()
    df["hour"]    = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.day_name()
    df["total"]   = df[["hvac", "lighting", "lobby", "mechanical_room", "kitchen"]].sum(axis=1)

    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = df.groupby(["weekday", "hour"])["total"].mean().unstack()
    pivot = pivot.reindex(order)

    fig = px.imshow(
        pivot,
        labels=dict(x="Hour of Day", y="Day of Week", color="Avg kWh"),
        # single-hue ramp (dark panel -> amber): darker = less energy, brighter = more
        color_continuous_scale=[[0, "#1B3A5C"], [1, theme.AMBER]],
        aspect="auto"
    )
    fig.update_layout(height=380, coloraxis_colorbar=dict(
        tickfont=dict(family=theme.FONT_MONO, color=theme.INK_DIM),
        title=dict(font=dict(family=theme.FONT_MONO, color=theme.INK_DIM)), outlinewidth=0))
    return fig

