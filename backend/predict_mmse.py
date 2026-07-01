# ==================================
# PREDICT MMSE FROM EXTRACTED FEATURES
# ==================================

import pandas as pd
import numpy as np
from keras.models import load_model
import os
import shutil

print("="*60)
print("MMSE PREDICTION")
print("="*60)

# --------------------------
# Configuration - Using absolute paths based on script location
# --------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_RESULTS = os.path.join(SCRIPT_DIR, "results")
FRONTEND_RESULTS = os.path.join(SCRIPT_DIR, "..", "frontend", "results")

# --------------------------
# 1. Load Trained Model
# --------------------------
print("\n🔄 Loading trained LSTM model...")
model = load_model(os.path.join(SCRIPT_DIR, 'models/lstm_mmse_model.keras'))
print("✅ Model loaded successfully")

# --------------------------
# 2. Load Extracted Features
# --------------------------
print("\n📂 Loading extracted features...")
features_df = pd.read_csv(os.path.join(BACKEND_RESULTS, 'extract1.csv'))

# Get feature values (in seconds)
IDS = features_df['Initial_Double_Support_Sec'].values[0]
SLS = features_df['Single_Limb_Support_Sec'].values[0]
TDS = features_df['Terminal_Double_Support_Sec'].values[0]
STN = features_df['Stance_Time_Sec'].values[0]
SWN = features_df['Swing_Time_Sec'].values[0]
STP = features_df['Step_Time_Sec'].values[0]
STR = features_df['Stride_Time_Sec'].values[0]

# Check for None values
if None in [IDS, SLS, TDS, STN, SWN, STP, STR]:
    print("\n❌ ERROR: Some features are missing (None values)")
    print("   Cannot make prediction without all features.")
    print("\n   Feature values:")
    print(f"   IDS: {IDS}, SLS: {SLS}, TDS: {TDS}")
    print(f"   STN: {STN}, SWN: {SWN}, STP: {STP}, STR: {STR}")
    exit(1)

print("✅ Features loaded")
print(f"   IDS: {IDS:.4f}s, SLS: {SLS:.4f}s, TDS: {TDS:.4f}s")
print(f"   STN: {STN:.4f}s, SWN: {SWN:.4f}s, STP: {STP:.4f}s, STR: {STR:.4f}s")

# --------------------------
# 3. Prepare Input for LSTM
# --------------------------

# Create input in same format as training data
# Shape: [1, 7, 1] - one sample, 7 features, 1 value each
input_features = np.array([
    [[IDS], [SLS], [TDS], [STN], [SWN], [STP], [STR]]
], dtype=float)

print(f"\n📊 Input shape: {input_features.shape}")

# --------------------------
# 4. Predict MMSE
# --------------------------

print("\n🎯 Predicting MMSE score...")
prediction = model.predict(input_features, verbose=0)
predicted_mmse = round(prediction[0][0] * 30)

# Clip to valid MMSE range
predicted_mmse = max(0, min(30, predicted_mmse))

print(f"\n✅ Prediction complete!")

# --------------------------
# 5. Interpret Results
# --------------------------

def interpret_mmse(score):
    """Interpret MMSE score"""
    if score >= 27:
        return "Normal Cognition", "green", "Low Risk"
    elif score >= 21:
        return "Mild Cognitive Impairment", "yellow", "Medium Risk"
    elif score >= 10:
        return "Moderate Dementia", "orange", "High Risk"
    else:
        return "Severe Dementia", "red", "Critical Risk"

category, color, risk = interpret_mmse(predicted_mmse)

# --------------------------
# 6. Calculate Confidence Metrics
# --------------------------

# Simple confidence based on feature consistency
feature_std = np.std([IDS, SLS, TDS, STN, SWN, STP, STR])
confidence = max(50, min(95, 95 - feature_std * 100))

# --------------------------
# 7. Update Features CSV with Prediction
# --------------------------

features_df['Predicted_MMSE'] = predicted_mmse
features_df['Cognitive_Status'] = category
features_df['Risk_Level'] = color
features_df['Confidence_Percent'] = round(confidence, 1)

# Also create a separate prediction results file
results = {
    'Timestamp': features_df['Timestamp'].values[0],
    'Predicted_MMSE': predicted_mmse,
    'Max_MMSE': 30,
    'Percentage': round((predicted_mmse / 30) * 100, 1),
    'Cognitive_Status': category,
    'Risk_Level': color,
    'Risk_Category': risk,
    'Confidence_Percent': round(confidence, 1),
    'Step_Time_MS': features_df['Step_Time_MS'].values[0],
    'Stride_Time_MS': features_df['Stride_Time_MS'].values[0],
    'IDS_MS': features_df['IDS_MS'].values[0],
    'TDS_MS': features_df['TDS_MS'].values[0],
    'SLS_MS': features_df['SLS_MS'].values[0],
    'Stance_MS': features_df['Stance_MS'].values[0],
    'Swing_MS': features_df['Swing_MS'].values[0]
}

results_df = pd.DataFrame([results])

# --------------------------
# 8. Generate Clinical Report
# --------------------------

report = f"""
{'='*60}
GAIT ANALYSIS & COGNITIVE ASSESSMENT REPORT
{'='*60}

Date/Time: {features_df['Timestamp'].values[0]}
Duration: {features_df['Duration_Seconds'].values[0]} seconds

PREDICTED MMSE SCORE: {predicted_mmse}/30 ({results['Percentage']}%)

COGNITIVE STATUS: {category}
RISK ASSESSMENT: {risk}
CONFIDENCE LEVEL: {round(confidence, 1)}%

{'='*60}
GAIT PARAMETERS (Bilateral Average)
{'='*60}

Temporal Parameters:
  • Step Time:              {features_df['Step_Time_MS'].values[0]:.1f} ms
  • Stride Time:            {features_df['Stride_Time_MS'].values[0]:.1f} ms
  
Stance/Swing Distribution:
  • Stance Phase:           {features_df['Stance_MS'].values[0]:.1f} ms
  • Swing Phase:            {features_df['Swing_MS'].values[0]:.1f} ms
  
Balance Parameters:
  • Single Limb Support:    {features_df['SLS_MS'].values[0]:.1f} ms
  • Initial Double Support: {features_df['IDS_MS'].values[0]:.1f} ms
  • Terminal Double Supp.:  {features_df['TDS_MS'].values[0]:.1f} ms

{'='*60}
GAIT EVENTS DETECTED
{'='*60}

Left Foot:
  • Heel Strikes: {features_df['Left_Heel_Strikes'].values[0]}
  • Toe Offs:     {features_df['Left_Toe_Offs'].values[0]}

Right Foot:
  • Heel Strikes: {features_df['Right_Heel_Strikes'].values[0]}
  • Toe Offs:     {features_df['Right_Toe_Offs'].values[0]}

{'='*60}

Note: This is a computational prediction based on gait analysis.
Clinical diagnosis should be made by qualified healthcare professionals.

{'='*60}
"""

# --------------------------
# 9. Save All Files to BOTH Locations
# --------------------------

# Debug: Show paths being used
print(f"\n🔍 Script location: {SCRIPT_DIR}")
print(f"🔍 Backend results: {os.path.abspath(BACKEND_RESULTS)}")
print(f"🔍 Frontend results: {os.path.abspath(FRONTEND_RESULTS)}")

# Ensure both directories exist
os.makedirs(BACKEND_RESULTS, exist_ok=True)
os.makedirs(FRONTEND_RESULTS, exist_ok=True)

# Define file paths
backend_files = {
    'extracted_features': os.path.join(BACKEND_RESULTS, 'extracted_features.csv'),
    'prediction_results': os.path.join(BACKEND_RESULTS, 'prediction_results.csv'),
    'clinical_report': os.path.join(BACKEND_RESULTS, 'clinical_report.txt')
}

frontend_files = {
    'extracted_features': os.path.join(FRONTEND_RESULTS, 'extracted_features.csv'),
    'prediction_results': os.path.join(FRONTEND_RESULTS, 'prediction_results.csv'),
    'clinical_report': os.path.join(FRONTEND_RESULTS, 'clinical_report.txt')
}

# Save extracted_features.csv to both locations
features_df.to_csv(backend_files['extracted_features'], index=False)
shutil.copy2(backend_files['extracted_features'], frontend_files['extracted_features'])

# Save prediction_results.csv to both locations
results_df.to_csv(backend_files['prediction_results'], index=False)
shutil.copy2(backend_files['prediction_results'], frontend_files['prediction_results'])

# Save clinical_report.txt to both locations
with open(backend_files['clinical_report'], 'w') as f:
    f.write(report)
shutil.copy2(backend_files['clinical_report'], frontend_files['clinical_report'])

# --------------------------
# 10. Verify Files & Display Results
# --------------------------

print("\n" + "="*60)
print("PREDICTION RESULTS")
print("="*60)
print(f"\n🧠 Predicted MMSE Score: {predicted_mmse}/30 ({results['Percentage']}%)")
print(f"📊 Cognitive Status: {category}")
print(f"🚦 Risk Level: {risk}")
print(f"💯 Confidence: {round(confidence, 1)}%")
print("\n" + "-"*60)
print("GAIT PARAMETERS:")
print("-"*60)
print(f"Step Time:       {features_df['Step_Time_MS'].values[0]:.1f} ms")
print(f"Stride Time:     {features_df['Stride_Time_MS'].values[0]:.1f} ms")
print(f"Stance Time:     {features_df['Stance_MS'].values[0]:.1f} ms")
print(f"Swing Time:      {features_df['Swing_MS'].values[0]:.1f} ms")
print(f"Single Limb:     {features_df['SLS_MS'].values[0]:.1f} ms")
print(f"Double Support:  {features_df['IDS_MS'].values[0]:.1f} ms (initial)")
print(f"                 {features_df['TDS_MS'].values[0]:.1f} ms (terminal)")
print("="*60)

# Verify all files exist
print(f"\n✅ Files saved and verified:")
print(f"\n📂 Backend ({BACKEND_RESULTS}):")
for name, path in backend_files.items():
    status = "✅" if os.path.exists(path) else "❌"
    print(f"   {status} {os.path.basename(path)}")

print(f"\n📂 Frontend ({os.path.abspath(FRONTEND_RESULTS)}):")
for name, path in frontend_files.items():
    status = "✅" if os.path.exists(path) else "❌"
    print(f"   {status} {os.path.basename(path)}")

print("\n🌐 Ready for frontend integration!")