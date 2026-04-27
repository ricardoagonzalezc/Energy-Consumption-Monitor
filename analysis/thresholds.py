import pandas as pd

THRESHOLDS = {
    "hvac":     {"max": 32.0, "unit": "kWh"},
    "lighting": {"max": 14.0, "unit": "kWh"},
    "lobby":    {"max": 8.0,  "unit": "kWh"},
    "it_room":  {"max": 16.0, "unit": "kWh"},
    "kitchen":  {"max": 12.0, "unit": "kWh"},
}

def check_alerts(df):
    """
    Check each row against zone thresholds.
    Returns a dataframe of triggered alerts.
    """
    alerts = []

    for _, row in df.iterrows():
        for zone, limits in THRESHOLDS.items():
            value = row[zone]
            if value > limits["max"]:
                alerts.append({
                    "timestamp": row["timestamp"],
                    "zone":      zone,
                    "value":     round(value, 2),
                    "limit":     limits["max"],
                    "excess":    round(value - limits["max"], 2),
                    "unit":      limits["unit"]
                })

    if alerts:
        return pd.DataFrame(alerts)
    else:
        return pd.DataFrame(
            columns=["timestamp", "zone", "value", "limit", "excess", "unit"]
        )