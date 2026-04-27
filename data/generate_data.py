import numpy as np
import pandas as pd

np.random.seed(42)
n = 24 * 60  # 60 days of hourly readings

timestamps = pd.date_range(start="2024-01-01", periods=n, freq="h")

# Hour of day pattern (0-23) for realistic daily cycles
hours = timestamps.hour

# Base profiles per zone using hour-of-day patterns
def hvac_profile(hour):
    if 8 <= hour <= 20:
        return np.random.normal(20, 1.5)
    return np.random.normal(10, 1.0)

def lighting_profile(hour):
    if 7 <= hour <= 22:
        return np.random.normal(8, 0.8)
    return np.random.normal(1, 0.3)

def lobby_profile(hour):
    if 8 <= hour <= 18:
        return np.random.normal(4, 0.5)
    return np.random.normal(1.5, 0.3)

def mechanical_room_profile(hour):
    return np.random.normal(10, 0.5)

def kitchen_profile(hour):
    if hour in [7, 8, 12, 13, 17, 18]:
        return np.random.normal(7, 0.8)
    return np.random.normal(3, 0.4)

# Generate readings
hvac     = np.array([hvac_profile(h)    for h in hours]).clip(min=0)
lighting = np.array([lighting_profile(h) for h in hours]).clip(min=0)
lobby    = np.array([lobby_profile(h)   for h in hours]).clip(min=0)
mechanical_room  = np.array([mechanical_room_profile(h) for h in hours]).clip(min=0)
kitchen  = np.array([kitchen_profile(h) for h in hours]).clip(min=0)

# Inject anomalies
# HVAC heatwave spike: days 20-23
hvac[24*20:24*23] += np.random.uniform(12, 18, 24*3)

# Lighting left on overnight: day 35
lighting[24*35:24*35+8] += np.random.uniform(8, 10, 8)

# Kitchen equipment fault: day 45
kitchen[24*45:24*45+6] += np.random.uniform(6, 9, 6)

df = pd.DataFrame({
    "timestamp": timestamps,
    "hvac":      hvac.round(2),
    "lighting":  lighting.round(2),
    "lobby":     lobby.round(2),
    "mechanical_room":   mechanical_room.round(2),
    "kitchen":   kitchen.round(2),
})

df.to_csv("data/energy_data.csv", index=False)
print(f"Energy dataset created: {len(df)} rows, 5 zones, 3 injected anomalies.")