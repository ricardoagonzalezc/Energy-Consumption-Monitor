def calculate_kpis(df, cost_per_kwh=0.15):
    """
    Calculate key energy KPIs from the dataframe.
    """
    zones = ["hvac", "lighting", "lobby", "mechanical_room", "kitchen"]

    # Total consumption per zone
    totals = {zone: df[zone].sum().round(2) for zone in zones}

    # Overall total
    df["total"] = df[zones].sum(axis=1)
    total_kwh = round(df["total"].sum(), 2)

    # Peak demand (single highest hour)
    peak_kwh  = round(df["total"].max(), 2)
    peak_time = df.loc[df["total"].idxmax(), "timestamp"]

    # Daily average
    df["date"]    = df["timestamp"].dt.date
    daily_totals  = df.groupby("date")["total"].sum()
    daily_avg_kwh = round(daily_totals.mean(), 2)

    # Cost estimate
    total_cost = round(total_kwh * cost_per_kwh, 2)

    # Worst zone (highest total consumption)
    worst_zone = max(totals, key=totals.get)

    return {
        "total_kwh":    total_kwh,
        "peak_kwh":     peak_kwh,
        "peak_time":    peak_time,
        "daily_avg":    daily_avg_kwh,
        "total_cost":   total_cost,
        "worst_zone":   worst_zone,
        "zone_totals":  totals
    }