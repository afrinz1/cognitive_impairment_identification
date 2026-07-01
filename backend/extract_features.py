# ==================================
# EXTRACT GAIT FEATURES FROM ARDUINO DATA
# ==================================

import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime

print("="*60)
print("GAIT FEATURE EXTRACTION")
print("="*60)

# --------------------------
# Configuration
# --------------------------
INPUT_FILE = "data/gait_data_1.csv"
OUTPUT_FILE = "results/extract1.csv"
FRONTEND_OUTPUT_FILE = "../frontend/results/extract1.csv"

# --------------------------
# 1. Load Data
# --------------------------
print(f"\n📂 Loading gait data from: {INPUT_FILE}")
dataset = pd.read_csv(INPUT_FILE)

print(f"✅ Loaded {len(dataset)} samples")
print(f"Duration: {dataset.iloc[-1]['time_ms'] / 1000:.2f} seconds")

# Debug: Check data structure
print(f"\n🔍 Data columns: {list(dataset.columns)}")
print(f"First few rows:\n{dataset.head()}")

# --------------------------
# Helper Functions
# --------------------------

def avg(x):
    """Calculate average, handle empty lists"""
    if not x or len(x) == 0:
        return None
    try:
        return sum(x) / len(x)
    except (ZeroDivisionError, TypeError):
        return None

# --------------------------
# 2. Detect Gait Events (FIXED)
# --------------------------

def detect_gait_events(data, gyro_col, flag_col, event_col):
    """
    Detect Heel Strike (HS) and Toe Off (TO) events
    HS: transition from active (1) to rest (0) - foot lands
    TO: transition from rest (0) to active (1) - foot lifts
    """
    
    events_detected = 0
    
    for i in range(1, len(data)):
        current_flag = data.loc[i, flag_col]
        previous_flag = data.loc[i-1, flag_col]
        
        # Heel Strike: Active → Rest (1 → 0)
        # When gyro goes below threshold, foot is landing
        if previous_flag == 1 and current_flag == 0:
            data.loc[i, event_col] = "HS"
            events_detected += 1
        
        # Toe Off: Rest → Active (0 → 1)  
        # When gyro exceeds threshold, foot is lifting
        elif previous_flag == 0 and current_flag == 1:
            data.loc[i, event_col] = "TO"
            events_detected += 1
    
    return events_detected

# Add event columns if they don't exist
if 'left_event' not in dataset.columns:
    dataset['left_event'] = ""
if 'right_event' not in dataset.columns:
    dataset['right_event'] = ""

print("\n🔍 Detecting gait events...")

# Detect events for both feet
left_events = detect_gait_events(dataset, 'leftY_dps', 'left_flag', 'left_event')
right_events = detect_gait_events(dataset, 'rightY_dps', 'right_flag', 'right_event')

# Count specific event types
hs_left = (dataset['left_event'] == 'HS').sum()
to_left = (dataset['left_event'] == 'TO').sum()
hs_right = (dataset['right_event'] == 'HS').sum()
to_right = (dataset['right_event'] == 'TO').sum()

print(f"Left  - Heel Strikes: {hs_left}, Toe Offs: {to_left}")
print(f"Right - Heel Strikes: {hs_right}, Toe Offs: {to_right}")

# Debug: Show sample events
if hs_left > 0 or to_left > 0:
    print("\n📋 Sample left events:")
    print(dataset[dataset['left_event'].isin(['HS', 'TO'])][['time_ms', 'leftY_dps', 'left_flag', 'left_event']].head(10))

if hs_left == 0 and to_left == 0:
    print("\n⚠️  WARNING: No events detected! Checking data...")
    print(f"   Left flag distribution: {dataset['left_flag'].value_counts().to_dict()}")
    print(f"   Right flag distribution: {dataset['right_flag'].value_counts().to_dict()}")

# --------------------------
# 3. Feature Extraction Functions
# --------------------------

def extract_time_intervals(event_col, start_event, end_event):
    """
    Extract time intervals between two event types
    Returns list of intervals in milliseconds
    """
    intervals = []
    start_time = None
    
    for i in range(len(dataset)):
        event = dataset.loc[i, event_col]
        
        if event == start_event:
            start_time = dataset.loc[i, 'time_ms']
        elif event == end_event and start_time is not None:
            end_time = dataset.loc[i, 'time_ms']
            interval = end_time - start_time
            if interval > 0 and interval < 5000:  # Sanity check: 0-5 seconds
                intervals.append(interval)
            start_time = None
    
    # Keep last 10 measurements for stability
    if len(intervals) > 10:
        intervals = intervals[-10:]
    
    return intervals

def stride_time_left():
    """Stride time: HS → HS (same foot)"""
    intervals = []
    last_hs_time = None
    
    for i in range(len(dataset)):
        if dataset.loc[i, 'left_event'] == 'HS':
            if last_hs_time is not None:
                interval = dataset.loc[i, 'time_ms'] - last_hs_time
                if 500 < interval < 2500:  # Reasonable stride: 0.5-2.5s
                    intervals.append(interval)
            last_hs_time = dataset.loc[i, 'time_ms']
    
    if len(intervals) > 10:
        intervals = intervals[-10:]
    return avg(intervals)

def stride_time_right():
    """Stride time: HS → HS (same foot)"""
    intervals = []
    last_hs_time = None
    
    for i in range(len(dataset)):
        if dataset.loc[i, 'right_event'] == 'HS':
            if last_hs_time is not None:
                interval = dataset.loc[i, 'time_ms'] - last_hs_time
                if 500 < interval < 2500:
                    intervals.append(interval)
            last_hs_time = dataset.loc[i, 'time_ms']
    
    if len(intervals) > 10:
        intervals = intervals[-10:]
    return avg(intervals)

def step_time():
    """Step time: Left HS → Right HS (alternating)"""
    intervals = []
    last_left_hs = None
    last_right_hs = None
    
    for i in range(len(dataset)):
        if dataset.loc[i, 'left_event'] == 'HS':
            last_left_hs = dataset.loc[i, 'time_ms']
            if last_right_hs is not None:
                interval = last_left_hs - last_right_hs
                if 200 < interval < 1500:
                    intervals.append(interval)
        
        if dataset.loc[i, 'right_event'] == 'HS':
            last_right_hs = dataset.loc[i, 'time_ms']
            if last_left_hs is not None:
                interval = last_right_hs - last_left_hs
                if 200 < interval < 1500:
                    intervals.append(interval)
    
    if len(intervals) > 10:
        intervals = intervals[-10:]
    return avg(intervals)

def swing_time(foot='left'):
    """Swing time: TO → HS (foot in air)"""
    event_col = 'left_event' if foot == 'left' else 'right_event'
    intervals = []
    to_time = None
    
    for i in range(len(dataset)):
        if dataset.loc[i, event_col] == 'TO':
            to_time = dataset.loc[i, 'time_ms']
        elif dataset.loc[i, event_col] == 'HS' and to_time is not None:
            interval = dataset.loc[i, 'time_ms'] - to_time
            if 100 < interval < 1000:
                intervals.append(interval)
            to_time = None
    
    if len(intervals) > 10:
        intervals = intervals[-10:]
    return avg(intervals)

def stance_time(foot='left'):
    """Stance time: HS → TO (foot on ground)"""
    event_col = 'left_event' if foot == 'left' else 'right_event'
    intervals = []
    hs_time = None
    
    for i in range(len(dataset)):
        if dataset.loc[i, event_col] == 'HS':
            hs_time = dataset.loc[i, 'time_ms']
        elif dataset.loc[i, event_col] == 'TO' and hs_time is not None:
            interval = dataset.loc[i, 'time_ms'] - hs_time
            if 200 < interval < 2000:
                intervals.append(interval)
            hs_time = None
    
    if len(intervals) > 10:
        intervals = intervals[-10:]
    return avg(intervals)

def double_support_initial():
    """Initial double support: Right HS → Left TO"""
    intervals = []
    right_hs_time = None
    
    for i in range(len(dataset)):
        if dataset.loc[i, 'right_event'] == 'HS':
            right_hs_time = dataset.loc[i, 'time_ms']
        elif dataset.loc[i, 'left_event'] == 'TO' and right_hs_time is not None:
            interval = dataset.loc[i, 'time_ms'] - right_hs_time
            if 50 < interval < 500:
                intervals.append(interval)
            right_hs_time = None
    
    if len(intervals) > 10:
        intervals = intervals[-10:]
    return avg(intervals)

def double_support_terminal():
    """Terminal double support: Left HS → Right TO"""
    intervals = []
    left_hs_time = None
    
    for i in range(len(dataset)):
        if dataset.loc[i, 'left_event'] == 'HS':
            left_hs_time = dataset.loc[i, 'time_ms']
        elif dataset.loc[i, 'right_event'] == 'TO' and left_hs_time is not None:
            interval = dataset.loc[i, 'time_ms'] - left_hs_time
            if 50 < interval < 500:
                intervals.append(interval)
            left_hs_time = None
    
    if len(intervals) > 10:
        intervals = intervals[-10:]
    return avg(intervals)

# --------------------------
# 4. Extract All Features
# --------------------------

print("\n⚙️  Extracting gait features...")

features = {}

# Calculate features
stride_left = stride_time_left()
stride_right = stride_time_right()
swing_left = swing_time('left')
swing_right = swing_time('right')
stance_left = stance_time('left')
stance_right = stance_time('right')

# Average bilateral features
features['Step_Time_MS'] = step_time()
features['Stride_Time_MS'] = avg([stride_left, stride_right]) if stride_left and stride_right else None
features['IDS_MS'] = double_support_initial()
features['TDS_MS'] = double_support_terminal()
features['SLS_MS'] = avg([swing_left, swing_right]) if swing_left and swing_right else None
features['Stance_MS'] = avg([stance_left, stance_right]) if stance_left and stance_right else None
features['Swing_MS'] = avg([swing_left, swing_right]) if swing_left and swing_right else None

# Convert to seconds for model input
features['Step_Time_Sec'] = round(features['Step_Time_MS'] / 1000, 4) if features['Step_Time_MS'] else None
features['Stride_Time_Sec'] = round(features['Stride_Time_MS'] / 1000, 4) if features['Stride_Time_MS'] else None
features['Initial_Double_Support_Sec'] = round(features['IDS_MS'] / 1000, 4) if features['IDS_MS'] else None
features['Terminal_Double_Support_Sec'] = round(features['TDS_MS'] / 1000, 4) if features['TDS_MS'] else None
features['Single_Limb_Support_Sec'] = round(features['SLS_MS'] / 1000, 4) if features['SLS_MS'] else None
features['Stance_Time_Sec'] = round(features['Stance_MS'] / 1000, 4) if features['Stance_MS'] else None
features['Swing_Time_Sec'] = round(features['Swing_MS'] / 1000, 4) if features['Swing_MS'] else None

# Add metadata
features['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
features['Duration_Seconds'] = round(dataset.iloc[-1]['time_ms'] / 1000, 2)
features['Total_Samples'] = len(dataset)
features['Left_Heel_Strikes'] = hs_left
features['Left_Toe_Offs'] = to_left
features['Right_Heel_Strikes'] = hs_right
features['Right_Toe_Offs'] = to_right

# --------------------------
# 5. Save to CSV (Both Locations)
# --------------------------

features_df = pd.DataFrame([features])

# Save to primary location
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
features_df.to_csv(OUTPUT_FILE, index=False)
print(f"\n✅ Features saved to: {OUTPUT_FILE}")

# Copy to frontend location
os.makedirs(os.path.dirname(FRONTEND_OUTPUT_FILE), exist_ok=True)
shutil.copy2(OUTPUT_FILE, FRONTEND_OUTPUT_FILE)
print(f"✅ Features saved to: {FRONTEND_OUTPUT_FILE}")

# --------------------------
# 6. Display Results
# --------------------------

print("\n" + "="*60)
print("EXTRACTED GAIT FEATURES")
print("="*60)
print(f"\n⏱️  Step Time:                    {features['Step_Time_MS']} ms")
print(f"⏱️  Stride Time:                  {features['Stride_Time_MS']} ms")
print(f"⏱️  Initial Double Support:       {features['IDS_MS']} ms")
print(f"⏱️  Terminal Double Support:      {features['TDS_MS']} ms")
print(f"⏱️  Single Limb Support:          {features['SLS_MS']} ms")
print(f"⏱️  Stance Time:                  {features['Stance_MS']} ms")
print(f"⏱️  Swing Time:                   {features['Swing_MS']} ms")
print("="*60)

if features['Step_Time_MS'] is None:
    print("\n⚠️  WARNING: Could not extract features!")
    print("   Possible causes:")
    print("   - Not enough gait events detected")
    print("   - Data may need longer recording duration")
    print("   - Check sensor placement and threshold settings")
else:
    print(f"\n✅ Feature extraction complete!")
    print(f"📁 Backend CSV:  {OUTPUT_FILE}")
    print(f"📁 Frontend CSV: {FRONTEND_OUTPUT_FILE}")