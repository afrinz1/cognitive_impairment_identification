# ==================================
# GENERATE DEMO GAIT DATA - COGNITIVE IMPAIRMENT
# Simulates gait patterns of a person with cognitive decline
# ==================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

print("="*60)
print("GENERATING DEMO GAIT DATA - COGNITIVE IMPAIRMENT")
print("="*60)

# --------------------------
# Configuration - Select Cognitive Level
# --------------------------

# Choose one: 'normal', 'mci', 'mild', 'moderate', 'severe'
COGNITIVE_LEVEL = 'mild'  # ⚠️ CHANGE THIS TO TEST DIFFERENT LEVELS

COGNITIVE_PROFILES = {
    'normal': {
        'name': 'Normal Cognition',
        'expected_mmse': 28,
        'stride_time_ms': 1100,
        'step_time_ms': 550,
        'stance_ratio': 0.60,
        'swing_ratio': 0.40,
        'gyro_swing_amplitude': 250,
        'gyro_stance_amplitude': 30,
        'variability': 0.05,  # Low variability
        'asymmetry': 0.02,    # Minimal asymmetry
        'threshold': 40
    },
    'mci': {
        'name': 'Mild Cognitive Impairment (MCI)',
        'expected_mmse': 24,
        'stride_time_ms': 1250,  # Slower
        'step_time_ms': 625,
        'stance_ratio': 0.63,     # More time on ground
        'swing_ratio': 0.37,
        'gyro_swing_amplitude': 220,  # Reduced swing speed
        'gyro_stance_amplitude': 35,
        'variability': 0.10,      # Increased variability
        'asymmetry': 0.08,        # Some asymmetry
        'threshold': 40
    },
    'mild': {
        'name': 'Mild Dementia',
        'expected_mmse': 18,
        'stride_time_ms': 1400,   # Noticeably slower
        'step_time_ms': 700,
        'stance_ratio': 0.66,     # More cautious
        'swing_ratio': 0.34,
        'gyro_swing_amplitude': 180,  # Reduced movement
        'gyro_stance_amplitude': 40,
        'variability': 0.15,      # High variability
        'asymmetry': 0.12,        # Noticeable asymmetry
        'threshold': 35
    },
    'moderate': {
        'name': 'Moderate Dementia',
        'expected_mmse': 12,
        'stride_time_ms': 1600,   # Very slow
        'step_time_ms': 800,
        'stance_ratio': 0.70,     # Extended stance
        'swing_ratio': 0.30,
        'gyro_swing_amplitude': 140,  # Shuffling gait
        'gyro_stance_amplitude': 50,
        'variability': 0.22,      # Very high variability
        'asymmetry': 0.18,        # Significant asymmetry
        'threshold': 30
    },
    'severe': {
        'name': 'Severe Dementia',
        'expected_mmse': 6,
        'stride_time_ms': 1900,   # Extremely slow
        'step_time_ms': 950,
        'stance_ratio': 0.75,     # Maximum double support
        'swing_ratio': 0.25,
        'gyro_swing_amplitude': 100,  # Minimal swing
        'gyro_stance_amplitude': 60,  # Unstable stance
        'variability': 0.30,      # Extreme variability
        'asymmetry': 0.25,        # Severe asymmetry
        'threshold': 25
    }
}

# Get selected profile
profile = COGNITIVE_PROFILES[COGNITIVE_LEVEL]

print(f"\n🧠 Simulating: {profile['name']}")
print(f"📊 Expected MMSE: ~{profile['expected_mmse']}/30")
print(f"⏱️  Stride Time: {profile['stride_time_ms']} ms")
print(f"🚶 Gait Characteristics:")
print(f"   - Stance/Swing Ratio: {profile['stance_ratio']:.0%}/{profile['swing_ratio']:.0%}")
print(f"   - Variability: {profile['variability']:.0%}")
print(f"   - Asymmetry: {profile['asymmetry']:.0%}")

# --------------------------
# Simulation Parameters
# --------------------------
DURATION_SECONDS = 30
SAMPLE_RATE_HZ = 100

np.random.seed(42)

# --------------------------
# Generate Time Series
# --------------------------
total_samples = DURATION_SECONDS * SAMPLE_RATE_HZ
time_ms = np.arange(0, total_samples * 10, 10)

print(f"\n⚙️  Generating {total_samples} samples...")
print(f"Duration: {DURATION_SECONDS}s at {SAMPLE_RATE_HZ}Hz")

# --------------------------
# Advanced Gait Generator with Impairment Features
# --------------------------

leftY_dps = []
rightY_dps = []

left_cycle_start = 0
right_cycle_start = profile['step_time_ms']

current_time = 0

print("\n🚶 Simulating impaired gait pattern...")

while current_time < DURATION_SECONDS * 1000:
    
    # Add stride-to-stride variability (increases with impairment)
    stride_variation = np.random.normal(0, profile['stride_time_ms'] * profile['variability'])
    current_stride_time = profile['stride_time_ms'] + stride_variation
    current_stride_time = max(800, min(2500, current_stride_time))  # Physiological limits
    
    # Phase calculations
    left_phase_time = (current_time - left_cycle_start) % current_stride_time
    right_phase_time = (current_time - right_cycle_start) % current_stride_time
    
    # Calculate stance and swing durations
    stance_duration = current_stride_time * profile['stance_ratio']
    swing_duration = current_stride_time * profile['swing_ratio']
    
    # LEFT FOOT
    if left_phase_time < stance_duration:
        # Stance phase
        # Add freezing of gait episodes (common in dementia)
        if COGNITIVE_LEVEL in ['moderate', 'severe'] and np.random.random() < 0.05:
            left_gyro = 0  # Freezing episode
        else:
            left_gyro = np.random.uniform(-profile['gyro_stance_amplitude'], 
                                         profile['gyro_stance_amplitude'])
    else:
        # Swing phase
        swing_progress = (left_phase_time - stance_duration) / swing_duration
        left_gyro = profile['gyro_swing_amplitude'] * np.sin(swing_progress * np.pi)
        # Add noise (increases with impairment)
        noise_amplitude = 30 * (1 + profile['variability'])
        left_gyro += np.random.uniform(-noise_amplitude, noise_amplitude)
    
    # RIGHT FOOT (with asymmetry)
    asymmetry_factor = 1 + np.random.uniform(-profile['asymmetry'], profile['asymmetry'])
    
    if right_phase_time < stance_duration:
        # Stance phase
        if COGNITIVE_LEVEL in ['moderate', 'severe'] and np.random.random() < 0.05:
            right_gyro = 0  # Freezing episode
        else:
            right_gyro = np.random.uniform(-profile['gyro_stance_amplitude'], 
                                          profile['gyro_stance_amplitude'])
            right_gyro *= asymmetry_factor  # Apply asymmetry
    else:
        # Swing phase
        swing_progress = (right_phase_time - stance_duration) / swing_duration
        right_gyro = profile['gyro_swing_amplitude'] * np.sin(swing_progress * np.pi)
        right_gyro *= asymmetry_factor  # Apply asymmetry
        noise_amplitude = 30 * (1 + profile['variability'])
        right_gyro += np.random.uniform(-noise_amplitude, noise_amplitude)
    
    # Add tremor (common in some dementias)
    if COGNITIVE_LEVEL in ['moderate', 'severe']:
        tremor = 15 * np.sin(current_time * 0.05)  # 5 Hz tremor
        left_gyro += tremor
        right_gyro += tremor
    
    leftY_dps.append(left_gyro)
    rightY_dps.append(right_gyro)
    
    current_time += 10

# Trim to exact length
leftY_dps = leftY_dps[:len(time_ms)]
rightY_dps = rightY_dps[:len(time_ms)]

# --------------------------
# Apply Threshold Flags
# --------------------------

left_flag = [1 if abs(x) > profile['threshold'] else 0 for x in leftY_dps]
right_flag = [1 if abs(x) > profile['threshold'] else 0 for x in rightY_dps]

# --------------------------
# Create DataFrame
# --------------------------

demo_data = pd.DataFrame({
    'time_ms': time_ms,
    'leftY_dps': np.round(leftY_dps, 3),
    'rightY_dps': np.round(rightY_dps, 3),
    'left_flag': left_flag,
    'right_flag': right_flag
})

# --------------------------
# Save to CSV
# --------------------------

os.makedirs('data', exist_ok=True)
os.makedirs('results', exist_ok=True)

filename = f'data/gait_data_{COGNITIVE_LEVEL}.csv'
demo_data.to_csv(filename, index=False)

# Also save as default for pipeline
demo_data.to_csv('data/gait_data_session1.csv', index=False)

print(f"\n✅ Generated {len(demo_data)} samples")
print(f"✅ Saved to '{filename}'")
print(f"✅ Saved to 'data/gait_data_session1.csv' (for pipeline)")

# --------------------------
# Statistics
# --------------------------

print("\n" + "="*60)
print(f"DEMO DATA STATISTICS - {profile['name'].upper()}")
print("="*60)

left_active = sum(left_flag)
right_active = sum(right_flag)
left_active_pct = (left_active / len(left_flag)) * 100
right_active_pct = (right_active / len(right_flag)) * 100

print(f"\n📊 Expected MMSE Score: ~{profile['expected_mmse']}/30")
print(f"\n📊 Left foot activity:  {left_active}/{len(left_flag)} samples ({left_active_pct:.1f}%)")
print(f"📊 Right foot activity: {right_active}/{len(right_flag)} samples ({right_active_pct:.1f}%)")
print(f"\n📊 Left gyro range:  {min(leftY_dps):.2f} to {max(leftY_dps):.2f} deg/s")
print(f"📊 Right gyro range: {min(rightY_dps):.2f} to {max(rightY_dps):.2f} deg/s")

# Calculate gait metrics preview
left_mean = np.mean(np.abs(leftY_dps))
right_mean = np.mean(np.abs(rightY_dps))
asymmetry_actual = abs(left_mean - right_mean) / ((left_mean + right_mean) / 2) * 100

print(f"\n📊 Gait Symmetry:")
print(f"   Left mean |gyro|:  {left_mean:.2f} deg/s")
print(f"   Right mean |gyro|: {right_mean:.2f} deg/s")
print(f"   Asymmetry Index:   {asymmetry_actual:.1f}%")

# --------------------------
# Visualize
# --------------------------

fig, axes = plt.subplots(4, 1, figsize=(15, 12))

# Plot 1: Raw gyro data
axes[0].plot(demo_data['time_ms'] / 1000, demo_data['leftY_dps'], 
             label='Left Gyro Y', alpha=0.7, linewidth=0.8, color='blue')
axes[0].plot(demo_data['time_ms'] / 1000, demo_data['rightY_dps'], 
             label='Right Gyro Y', alpha=0.7, linewidth=0.8, color='red')
axes[0].axhline(y=profile['threshold'], color='green', linestyle='--', alpha=0.5, label='Threshold')
axes[0].axhline(y=-profile['threshold'], color='green', linestyle='--', alpha=0.5)
axes[0].set_xlabel('Time (seconds)')
axes[0].set_ylabel('Angular Velocity (deg/s)')
axes[0].set_title(f'Simulated Gait Data - {profile["name"]} (Expected MMSE: ~{profile["expected_mmse"]}/30)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Flags (activity detection)
axes[1].fill_between(demo_data['time_ms'] / 1000, 0, demo_data['left_flag'], 
                      alpha=0.6, label='Left Active', color='blue')
axes[1].fill_between(demo_data['time_ms'] / 1000, 0, demo_data['right_flag'], 
                      alpha=0.6, label='Right Active', color='red')
axes[1].set_xlabel('Time (seconds)')
axes[1].set_ylabel('Activity Flag')
axes[1].set_title('Movement Detection (Threshold-based)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].set_ylim(-0.1, 1.5)

# Plot 3: Zoom on 3-second window
zoom_start = 10000  # 10 seconds
zoom_end = 13000    # 13 seconds
zoom_data = demo_data[(demo_data['time_ms'] >= zoom_start) & 
                      (demo_data['time_ms'] <= zoom_end)]

axes[2].plot(zoom_data['time_ms'] / 1000, zoom_data['leftY_dps'], 
             label='Left Gyro Y', linewidth=1.5, marker='o', markersize=3, color='blue')
axes[2].plot(zoom_data['time_ms'] / 1000, zoom_data['rightY_dps'], 
             label='Right Gyro Y', linewidth=1.5, marker='o', markersize=3, color='red')
axes[2].axhline(y=profile['threshold'], color='green', linestyle='--', alpha=0.5, label='Threshold')
axes[2].axhline(y=-profile['threshold'], color='green', linestyle='--', alpha=0.5)
axes[2].set_xlabel('Time (seconds)')
axes[2].set_ylabel('Angular Velocity (deg/s)')
axes[2].set_title('Zoomed View: Individual Gait Cycles')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

# Plot 4: Comparison with normal gait
normal_stride = 1100
impaired_stride = profile['stride_time_ms']
categories = ['Normal', profile['name'].split()[0]]
stride_times = [normal_stride, impaired_stride]
colors_bar = ['green', 'orange' if COGNITIVE_LEVEL in ['mci', 'mild'] else 'red']

axes[3].bar(categories, stride_times, color=colors_bar, alpha=0.7)
axes[3].axhline(y=1100, color='green', linestyle='--', alpha=0.5, label='Normal Range')
axes[3].set_ylabel('Stride Time (ms)')
axes[3].set_title('Stride Time Comparison')
axes[3].legend()
axes[3].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
viz_filename = f'results/demo_gait_{COGNITIVE_LEVEL}.png'
plt.savefig(viz_filename, dpi=300, bbox_inches='tight')
print(f"\n✅ Visualization saved to '{viz_filename}'")
plt.show()

# --------------------------
# Sample Output
# --------------------------

print("\n" + "="*60)
print("SAMPLE DATA (first 20 rows)")
print("="*60)
print(demo_data.head(20).to_string(index=False))

# --------------------------
# Create Info File
# --------------------------

info = f"""
{'='*60}
GENERATED GAIT DATA INFORMATION
{'='*60}

Cognitive Level: {profile['name']}
Expected MMSE: ~{profile['expected_mmse']}/30

Gait Characteristics:
  - Stride Time: {profile['stride_time_ms']} ms
  - Step Time: {profile['step_time_ms']} ms
  - Stance Ratio: {profile['stance_ratio']:.0%}
  - Swing Ratio: {profile['swing_ratio']:.0%}
  
Impairment Features:
  - Variability: {profile['variability']:.0%}
  - Asymmetry: {profile['asymmetry']:.0%}
  - Swing Amplitude: {profile['gyro_swing_amplitude']} deg/s
  - Stance Amplitude: {profile['gyro_stance_amplitude']} deg/s

Data Statistics:
  - Total Samples: {len(demo_data)}
  - Duration: {DURATION_SECONDS} seconds
  - Sample Rate: {SAMPLE_RATE_HZ} Hz
  - Left Active: {left_active_pct:.1f}%
  - Right Active: {right_active_pct:.1f}%
  - Asymmetry Index: {asymmetry_actual:.1f}%

Next Steps:
  1. Run: python run_analysis.py
  2. Check predicted MMSE score
  3. Compare with expected: ~{profile['expected_mmse']}/30

{'='*60}
"""

with open(f'data/gait_info_{COGNITIVE_LEVEL}.txt', 'w') as f:
    f.write(info)

print("\n" + "="*60)
print("DEMO DATA GENERATION COMPLETE!")
print("="*60)
print(f"\n📁 Files created:")
print(f"   1. {filename}")
print(f"   2. data/gait_data_session2.csv (for pipeline)")
print(f"   3. {viz_filename}")
print(f"   4. data/gait_info_{COGNITIVE_LEVEL}.txt")
print(f"\n🧠 Expected MMSE: ~{profile['expected_mmse']}/30")
print(f"\n✅ Ready to run analysis!")
print("\n💡 Next step:")
print("   python run_analysis.py")
print("\n💡 To try different cognitive levels, change COGNITIVE_LEVEL to:")
print("   'normal', 'mci', 'mild', 'moderate', or 'severe'")