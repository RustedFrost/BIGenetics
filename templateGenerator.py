# create_expanded_template.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from datetime import time

# -------------------------------
# 1. Athlete Profiles (7 athletes)
# -------------------------------

athlete_data = [
    {"athlete_id": "alex", "name": "Alex Rivera", "age": 26, "sex": "M", "sport": "Professional Cyclist", "team": "Team Apex", "baseline_start_date": "2025-03-01", "notes": "Altitude specialist"},
    {"athlete_id": "jordan", "name": "Jordan Kim", "age": 29, "sex": "F", "sport": "Marathon Runner", "team": "Team Apex", "baseline_start_date": "2025-03-01", "notes": "High-mileage phase"},
    {"athlete_id": "taylor", "name": "Taylor Wu", "age": 24, "sex": "M", "sport": "Triathlete", "team": "Team Apex", "baseline_start_date": "2025-03-01", "notes": "Sprint distance focus"},
    {"athlete_id": "morgan", "name": "Morgan Lee", "age": 27, "sex": "F", "sport": "Swimmer", "team": "Team Apex", "baseline_start_date": "2025-03-01", "notes": "Pool taper phase"},
    {"athlete_id": "casey", "name": "Casey Dunn", "age": 25, "sex": "M", "sport": "Soccer Midfielder", "team": "Team Apex", "baseline_start_date": "2025-03-01", "notes": "In-season monitoring"},
    {"athlete_id": "riley", "name": "Riley Park", "age": 28, "sex": "F", "sport": "CrossFit Athlete", "team": "Team Apex", "baseline_start_date": "2025-03-01", "notes": "High-intensity training"},
    {"athlete_id": "austin", "name": "Austin Cole", "age": 30, "sex": "M", "sport": "Ultra Runner", "team": "Team Apex", "baseline_start_date": "2025-03-01", "notes": "Long-distance recovery focus"},
]

athletes_df = pd.DataFrame(athlete_data)

# -------------------------------
# 2. Genetic Profiles (from your spec)
# -------------------------------

genetic_data = []

# Define genetic profiles per athlete
genetic_profiles = {
    "alex": {
        "COMT": ("rs4680", "AA", "Slow (high stress reactivity)"),
        "PER3": ("PER3 VNTR", "long", "Long allele → higher sleep need"),
        "CLOCK": ("rs1801260", "AA", "Circadian delay risk"),
        "BDNF": ("rs6265", "Met", "Hypoxia & sleep loss sensitivity"),
        "PPARGC1A": ("rs8192678", "G", "High mitochondrial efficiency"),
        "ACTN3": ("rs1815739", "C", "Fast recovery"),
        "NOS3": ("rs1799983", "T", "Reduced vascular efficiency"),
    },
    "jordan": {
        "COMT": ("rs4680", "GG", "Fast"),
        "PER3": ("PER3 VNTR", "short", "Short allele"),
        "CLOCK": ("rs1801260", "GG", "No delay"),
        "BDNF": ("rs6265", "Val", "Resilient"),
        "PPARGC1A": ("rs8192678", "A", "Lower efficiency"),
        "ACTN3": ("rs1815739", "X", "Slower recovery"),
        "NOS3": ("rs1799983", "T", "Reduced vascular efficiency"),
    },
    "taylor": {
        "COMT": ("rs4680", "AG", "Medium"),
        "PER3": ("PER3 VNTR", "long", "High sleep need"),
        "CLOCK": ("rs1801260", "AG", "Mild delay"),
        "BDNF": ("rs6265", "Met", "Sensitive"),
        "PPARGC1A": ("rs8192678", "G", "Efficient"),
        "ACTN3": ("rs1815739", "R", "Balanced"),
        "NOS3": ("rs1799983", "C", "Normal"),
    },
    "morgan": {
        "COMT": ("rs4680", "GG", "Fast"),
        "PER3": ("PER3 VNTR", "short", "Low sleep need"),
        "CLOCK": ("rs1801260", "GG", "Stable"),
        "BDNF": ("rs6265", "Val", "Resilient"),
        "PPARGC1A": ("rs8192678", "G", "Efficient"),
        "ACTN3": ("rs1815739", "C", "Fast recovery"),
        "NOS3": ("rs1799983", "C", "Normal"),
    },
    "casey": {
        "COMT": ("rs4680", "AA", "Slow"),
        "PER3": ("PER3 VNTR", "long", "High sleep need"),
        "CLOCK": ("rs1801260", "AA", "Delay risk"),
        "BDNF": ("rs6265", "Met", "Sensitive"),
        "PPARGC1A": ("rs8192678", "A", "Moderate"),
        "ACTN3": ("rs1815739", "X", "Slower recovery"),
        "NOS3": ("rs1799983", "T", "Reduced efficiency"),
    },
    "riley": {
        "COMT": ("rs4680", "AA", "Slow"),
        "PER3": ("PER3 VNTR", "long", "Very high sleep need"),
        "CLOCK": ("rs1801260", "AA", "Strong delay"),
        "BDNF": ("rs6265", "Met", "High sensitivity"),
        "PPARGC1A": ("rs8192678", "G", "Efficient"),
        "ACTN3": ("rs1815739", "C", "Fast recovery"),
        "NOS3": ("rs1799983", "T", "Reduced efficiency"),
    },
    "austin": {
        "COMT": ("rs4680", "GG", "Fast"),
        "PER3": ("PER3 VNTR", "short", "Low sleep need"),
        "CLOCK": ("rs1801260", "GG", "Stable"),
        "BDNF": ("rs6265", "Val", "Resilient"),
        "PPARGC1A": ("rs8192678", "A", "Moderate"),
        "ACTN3": ("rs1815739", "X", "Slower recovery"),
        "NOS3": ("rs1799983", "C", "Normal"),
    },
}

for athlete_id, genes in genetic_profiles.items():
    for gene, (rsid, genotype, interpretation) in genes.items():
        genetic_data.append({
            "athlete_id": athlete_id,
            "gene": gene,
            "rsid": rsid,
            "genotype": genotype,
            "interpretation": interpretation
        })

genetics_df = pd.DataFrame(genetic_data)

# -------------------------------
# 3. Biometric Daily Data (14 days × 7 athletes)
# -------------------------------

np.random.seed(42)
biometric_data = []
start_date = datetime(2025, 4, 1)

# Baseline values per athlete (genetically adjusted)
baselines = {
    "alex": {"rhr": 50, "hrv": 90, "spo2": 98, "temp": 36.6, "deep": 22, "rem": 23, "light": 40, "duration": 8.0, "rr": 13, "load": 95},
    "jordan": {"rhr": 52, "hrv": 85, "spo2": 97, "temp": 36.7, "deep": 20, "rem": 22, "light": 45, "duration": 7.5, "rr": 14, "load": 90},
    "taylor": {"rhr": 48, "hrv": 92, "spo2": 98, "temp": 36.6, "deep": 23, "rem": 23, "light": 42, "duration": 8.2, "rr": 13, "load": 95},
    "morgan": {"rhr": 46, "hrv": 95, "spo2": 99, "temp": 36.5, "deep": 24, "rem": 24, "light": 38, "duration": 8.5, "rr": 12, "load": 88},
    "casey": {"rhr": 54, "hrv": 80, "spo2": 97, "temp": 36.8, "deep": 19, "rem": 21, "light": 46, "duration": 7.0, "rr": 15, "load": 92},
    "riley": {"rhr": 56, "hrv": 78, "spo2": 96, "temp": 36.9, "deep": 18, "rem": 20, "light": 48, "duration": 6.8, "rr": 16, "load": 94},
    "austin": {"rhr": 50, "hrv": 88, "spo2": 98, "temp": 36.6, "deep": 21, "rem": 22, "light": 43, "duration": 7.8, "rr": 14, "load": 85},
}

# Simulate 14 days
for days_offset in range(14):
    current_date = start_date + timedelta(days=days_offset)

    for athlete_id in athletes_df['athlete_id']:
        base = baselines[athlete_id]
        genetic = genetic_profiles[athlete_id]

        # Add realistic events
        is_travel_week = days_offset >= 8 and days_offset <= 10 and athlete_id in ["alex", "casey"]
        is_illness = days_offset >= 11 and athlete_id == "jordan"
        is_overtrained = days_offset >= 12 and athlete_id == "riley"
        is_recovering = days_offset >= 5 and athlete_id == "taylor"

        # Noise
        noise = np.random.normal(0, 1.5)

        # Resting HR
        rhr = base["rhr"] + noise
        if is_illness:
            rhr += 8
        elif is_overtrained:
            rhr += 6

        # HRV
        hrv = base["hrv"] - 0.5 * days_offset + noise * 2
        if is_illness:
            hrv -= 15
        elif is_overtrained:
            hrv -= 20
        elif is_recovering:
            hrv += 10

        # SpO2
        spo2 = base["spo2"] - 0.2 * days_offset + np.random.normal(0, 0.5)
        if is_illness:
            spo2 -= 3

        # Temp
        temp = base["temp"] + 0.05 * days_offset + np.random.normal(0, 0.1)
        if is_illness:
            temp += 0.6

        # Sleep
        deep = np.random.normal(base["deep"], 2)
        rem = np.random.normal(base["rem"], 2)
        light = 100 - deep - rem
        duration = base["duration"] + np.random.normal(0, 0.5)
        if is_travel_week:
            duration -= 1.5
            deep -= 5

        # Respiratory Rate
        rr = base["rr"] + np.random.normal(0, 1)
        if is_illness:
            rr += 3

        # Load
        load = base["load"] + np.random.normal(0, 5)
        if is_overtrained:
            load -= 25

        # Adjust load for travel
        # Sleep Onset (simulate circadian delay for long PER3)
        if genetic["PER3"][1] == "long" or genetic["CLOCK"][1] == "AA":
            if days_offset >= 5:
                # Pick hour from [23, 0, 1]
                sleep_onset_hour = random.choice([23, 0, 1])
            else:
                sleep_onset_hour = random.randint(21, 22)
        else:
            sleep_onset_hour = random.randint(21, 23)

        sleep_onset = f"{sleep_onset_hour % 24:02d}:{random.choice(['30', '45', '15'])}"

        wake_time = f"{(sleep_onset_hour + int(duration)) % 24:02d}:{random.choice(['00', '15', '30'])}"

        biometric_data.append({
            "athlete_id": athlete_id,
            "date": current_date,
            "resting_hr": max(40, min(100, round(rhr, 1))),
            "avg_hr_day": round(rhr + 15 + np.random.normal(0, 2), 1),
            "hrv_night": max(50, min(200, round(hrv, 1))),
            "spo2_night": max(85, min(100, round(spo2, 1))),
            "deep_sleep_pct": max(5, min(40, round(deep, 1))),
            "rem_sleep_pct": max(10, min(35, round(rem, 1))),
            "light_sleep_pct": max(30, min(70, round(light, 1))),
            "sleep_duration_h": max(4, min(12, round(duration, 1))),
            "resp_rate_night": max(8, min(30, round(rr, 1))),
            "temp_trend_c": max(35.0, min(40.0, round(temp, 1))),
            "training_load_pct": max(0, min(100, round(load, 1))),
            "sleep_onset_time": sleep_onset,
            "wake_time": wake_time
        })

biometrics_df = pd.DataFrame(biometric_data)

# -------------------------------
# 4. SAM Metrics Config (from spec)
# -------------------------------

metrics_config = pd.DataFrame([
    {"metric_name": "resting_hr", "green_low": 42, "green_high": 54, "yellow_low": 55, "yellow_high": 59, "red_low": 60, "red_high": 100, "unit": "bpm"},
    {"metric_name": "avg_hr_day", "green_low": 50, "green_high": 68, "yellow_low": 69, "yellow_high": 74, "red_low": 75, "red_high": 120, "unit": "bpm"},
    {"metric_name": "spo2_night", "green_low": 97, "green_high": 100, "yellow_low": 95, "yellow_high": 96, "red_low": 0, "red_high": 94, "unit": "%"},
    {"metric_name": "hrv_night", "green_low": 90, "green_high": 200, "yellow_low": 70, "yellow_high": 89, "red_low": 0, "red_high": 69, "unit": "ms"},
    {"metric_name": "deep_sleep_pct", "green_low": 22, "green_high": 100, "yellow_low": 17, "yellow_high": 21, "red_low": 0, "red_high": 16, "unit": "%"},
    {"metric_name": "rem_sleep_pct", "green_low": 20, "green_high": 25, "yellow_low": 16, "yellow_high": 19, "red_low": 0, "red_high": 15, "yellow_low2": 26, "yellow_high2": 30, "red_low2": 31, "red_high2": 100, "unit": "%"},
    {"metric_name": "light_sleep_pct", "green_low": 35, "green_high": 45, "yellow_low": 46, "yellow_high": 50, "red_low": 51, "red_high": 100, "unit": "%"},
    {"metric_name": "sleep_duration_h", "green_low": 8.0, "green_high": 9.2, "yellow_low": 7.0, "yellow_high": 7.9, "red_low": 0, "red_high": 6.9, "unit": "h"},
    {"metric_name": "resp_rate_night", "green_low": 10, "green_high": 14, "yellow_low": 15, "yellow_high": 16, "red_low": 17, "red_high": 100, "unit": "/min"},
    {"metric_name": "temp_trend_c", "green_low": 36.4, "green_high": 36.9, "yellow_low": 37.0, "yellow_high": 37.3, "red_low": 37.4, "red_high": 42.0, "yellow_low2": 36.3, "yellow_high2": 36.3, "red_low2": 0, "red_high2": 36.2, "unit": "°C"},
    {"metric_name": "training_load_pct", "green_low": 100, "green_high": 100, "yellow_low": 85, "yellow_high": 99, "red_low": 0, "red_high": 70, "unit": "%"},
])

# -------------------------------
# 5. Predictive Rules (from spec)
# -------------------------------

rules_df = pd.DataFrame([
    {"rule_id": "circadian", "metric_drop": "HRV↓ + Deep↓ + late sleep", "genetic_condition": "PER3 long or CLOCK AA", "cause": "Circadian misalignment", "recommendation": "Advance bedtime by 45 min, ↑ morning light, Mg glycinate + choline"},
    {"rule_id": "inflammation", "metric_drop": "HRV↓ + RHR↑ + Temp↑ + SpO₂↓", "genetic_condition": "Any", "cause": "Systemic inflammation", "recommendation": "Rest, hydrate, anti-inflammatory nutrition (omega-3, turmeric)"},
    {"rule_id": "nutrient_gap", "metric_drop": "HRV↓ + stable RHR/Temp + ↓REM/Deep", "genetic_condition": "COMT AA, MTHFR CT", "cause": "Nutrient deficiency", "recommendation": "Check iron, Mg, omega-3, B12; add choline (eggs, liver)"},
    {"rule_id": "airway_stress", "metric_drop": "SpO₂↓ + RR↑", "genetic_condition": "NOS3 T, ADRB2 risk", "cause": "Airway restriction", "recommendation": "Evaluate sleep environment, nasal breathing, allergens"},
    {"rule_id": "overtraining", "metric_drop": "HRV↓ + load↓", "genetic_condition": "ACTN3 X, AMPD1 C", "cause": "Overtraining syndrome", "recommendation": "Deload week, prioritize sleep and protein"},
])

# -------------------------------
# 6. Write to Excel
# -------------------------------

with pd.ExcelWriter("SAM_Recovery_Data_Template_Expanded.xlsx", engine="openpyxl") as writer:
    athletes_df.to_excel(writer, sheet_name="athlete_profiles", index=False)
    genetics_df.to_excel(writer, sheet_name="genetic_profiles", index=False)
    biometrics_df.to_excel(writer, sheet_name="biometric_daily", index=False)
    metrics_config.to_excel(writer, sheet_name="sam_metrics_config", index=False)
    rules_df.to_excel(writer, sheet_name="predictive_rules", index=False)

print("✅ Expanded Excel template created: SAM_Recovery_Data_Template_Expanded.xlsx")