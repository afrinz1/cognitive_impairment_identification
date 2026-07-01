import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed for reproducibility
np.random.seed(42)

# ==================================
# CONFIGURATION
# ==================================

N_SAMPLES = 1000  # More samples = better LSTM training

# Define MMSE categories with realistic gait characteristics
MMSE_CATEGORIES = {
    'Normal': {
        'mmse_range': (27, 30),
        'stride_time': (1.00, 1.15),      # Fast, regular gait
        'step_time': (0.50, 0.58),
        'stance_time': (0.60, 0.70),
        'swing_time': (0.38, 0.45),
        'sls_time': (0.38, 0.45),         # Good balance
        'ids_time': (0.10, 0.13),         # Short double support
        'tds_time': (0.10, 0.13),
        'variability': 0.02               # Low variability
    },
    'MCI': {  # Mild Cognitive Impairment
        'mmse_range': (21, 26),
        'stride_time': (1.10, 1.30),      # Slightly slower
        'step_time': (0.55, 0.65),
        'stance_time': (0.65, 0.78),
        'swing_time': (0.35, 0.42),
        'sls_time': (0.35, 0.42),         # Reduced balance confidence
        'ids_time': (0.12, 0.16),         # Longer double support
        'tds_time': (0.12, 0.16),
        'variability': 0.04               # Moderate variability
    },
    'Mild_Dementia': {
        'mmse_range': (15, 20),
        'stride_time': (1.25, 1.50),      # Noticeably slower
        'step_time': (0.62, 0.75),
        'stance_time': (0.75, 0.90),
        'swing_time': (0.32, 0.38),
        'sls_time': (0.32, 0.38),         # Poor balance
        'ids_time': (0.15, 0.20),         # Much longer double support
        'tds_time': (0.15, 0.20),
        'variability': 0.06               # High variability
    },
    'Moderate_Dementia': {
        'mmse_range': (10, 14),
        'stride_time': (1.45, 1.80),      # Very slow
        'step_time': (0.72, 0.90),
        'stance_time': (0.85, 1.05),
        'swing_time': (0.28, 0.35),
        'sls_time': (0.28, 0.35),         # Very poor balance
        'ids_time': (0.18, 0.25),         # Extended double support
        'tds_time': (0.18, 0.25),
        'variability': 0.08               # Very high variability
    },
    'Severe_Dementia': {
        'mmse_range': (0, 9),
        'stride_time': (1.70, 2.20),      # Extremely slow/shuffling
        'step_time': (0.85, 1.10),
        'stance_time': (1.00, 1.30),
        'swing_time': (0.25, 0.32),
        'sls_time': (0.25, 0.32),         # Minimal single limb support
        'ids_time': (0.22, 0.30),         # Maximum double support
        'tds_time': (0.22, 0.30),
        'variability': 0.10               # Extreme variability
    }
}

# ==================================
# DATA GENERATION FUNCTION
# ==================================

def generate_correlated_gait_data(n_samples):
    """
    Generate synthetic gait data with strong correlations to MMSE
    Based on research literature on gait-cognition relationships
    """
    
    data = []
    
    # Distribute samples across categories
    samples_per_category = n_samples // len(MMSE_CATEGORIES)
    
    for category_name, params in MMSE_CATEGORIES.items():
        
        for _ in range(samples_per_category):
            
            # Generate base MMSE score for this sample
            mmse = np.random.uniform(*params['mmse_range'])
            
            # Generate stride time (primary feature)
            stride = np.random.uniform(*params['stride_time'])
            
            # Add individual variability
            stride += np.random.normal(0, params['variability'])
            
            # Step time ≈ stride time / 2 (with small variation)
            step = stride / 2 + np.random.normal(0, 0.02)
            
            # Swing time
            swing = np.random.uniform(*params['swing_time'])
            swing += np.random.normal(0, params['variability'] / 2)
            
            # Stance time = stride time - swing time (gait cycle constraint)
            stance = stride - swing
            
            # Single limb support ≈ swing time of opposite limb
            sls = swing + np.random.normal(0, 0.01)
            
            # Initial double support
            ids = np.random.uniform(*params['ids_time'])
            ids += np.random.normal(0, params['variability'] / 2)
            
            # Terminal double support (should be similar to IDS)
            tds = ids + np.random.normal(0, 0.01)
            
            # Add physiological constraints
            # Double support time cannot exceed stance time
            total_ds = ids + tds
            if total_ds > stance:
                scale = stance * 0.4 / total_ds
                ids *= scale
                tds *= scale
            
            # Ensure all values are positive
            ids = max(0.05, ids)
            sls = max(0.20, sls)
            tds = max(0.05, tds)
            stance = max(0.40, stance)
            swing = max(0.20, swing)
            step = max(0.30, step)
            stride = max(0.80, stride)
            
            data.append({
                'IDS': ids,
                'SLS': sls,
                'TDS': tds,
                'Stance': stance,
                'Swing': swing,
                'Step': step,
                'Stride': stride,
                'MMSE': mmse,
                'Category': category_name
            })
    
    return pd.DataFrame(data)

# ==================================
# GENERATE DATA
# ==================================

print("Generating high-accuracy synthetic MMSE training data...")
df = generate_correlated_gait_data(N_SAMPLES)

# ==================================
# ADD REALISTIC NOISE & CORRELATIONS
# ==================================

# Add subtle inter-feature correlations based on biomechanics
for idx in df.index:
    # Older/impaired individuals have more asymmetry
    if df.loc[idx, 'MMSE'] < 20:
        asymmetry = np.random.uniform(0.95, 1.05)
        df.loc[idx, 'IDS'] *= asymmetry
        df.loc[idx, 'TDS'] *= (2 - asymmetry)  # Opposite effect

# ==================================
# VALIDATE GAIT CYCLE CONSTRAINTS
# ==================================

print("\nValidating gait cycle constraints...")
for idx in df.index:
    # Ensure stride = stance + swing (within tolerance)
    calculated_stride = df.loc[idx, 'Stance'] + df.loc[idx, 'Swing']
    if abs(calculated_stride - df.loc[idx, 'Stride']) > 0.1:
        df.loc[idx, 'Stride'] = calculated_stride

# ==================================
# SHUFFLE DATA
# ==================================

df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# ==================================
# SAVE TRAINING DATA
# ==================================

# Save without category column (only for analysis)
training_data = df[['IDS', 'SLS', 'TDS', 'Stance', 'Swing', 'Step', 'Stride', 'MMSE']]
training_data.to_csv('MMSE_DATA.csv', index=False)

print(f"\n✅ Generated {len(df)} samples")
print(f"✅ Saved to 'MMSE_DATA.csv'")

# ==================================
# STATISTICS & VALIDATION
# ==================================

print("\n" + "="*60)
print("DATASET STATISTICS")
print("="*60)

print("\n📊 MMSE Distribution:")
print(df.groupby('Category')['MMSE'].describe()[['count', 'mean', 'std', 'min', 'max']])

print("\n📊 Gait Feature Ranges:")
print(df[['Stride', 'Step', 'Stance', 'Swing', 'SLS', 'IDS', 'TDS']].describe())

print("\n📊 Correlation with MMSE:")
correlations = df[['IDS', 'SLS', 'TDS', 'Stance', 'Swing', 'Step', 'Stride', 'MMSE']].corr()['MMSE'].sort_values(ascending=False)
print(correlations)

# ==================================
# VISUALIZATION
# ==================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. MMSE distribution
axes[0, 0].hist(df['MMSE'], bins=30, color='skyblue', edgecolor='black')
axes[0, 0].set_xlabel('MMSE Score')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].set_title('MMSE Score Distribution')
axes[0, 0].axvline(df['MMSE'].mean(), color='red', linestyle='--', label=f'Mean: {df["MMSE"].mean():.1f}')
axes[0, 0].legend()

# 2. Stride Time vs MMSE (strongest correlation expected)
scatter = axes[0, 1].scatter(df['Stride'], df['MMSE'], c=df['MMSE'], cmap='RdYlGn', alpha=0.6)
axes[0, 1].set_xlabel('Stride Time (s)')
axes[0, 1].set_ylabel('MMSE Score')
axes[0, 1].set_title('Stride Time vs MMSE (Expected Strong Correlation)')
plt.colorbar(scatter, ax=axes[0, 1], label='MMSE')

# Add trend line
z = np.polyfit(df['Stride'], df['MMSE'], 1)
p = np.poly1d(z)
axes[0, 1].plot(df['Stride'].sort_values(), p(df['Stride'].sort_values()), "r--", alpha=0.8, label='Trend')
axes[0, 1].legend()

# 3. Category-wise boxplot
df.boxplot(column='MMSE', by='Category', ax=axes[1, 0])
axes[1, 0].set_xlabel('Cognitive Category')
axes[1, 0].set_ylabel('MMSE Score')
axes[1, 0].set_title('MMSE by Cognitive Category')
plt.sca(axes[1, 0])
plt.xticks(rotation=45)

# 4. Correlation heatmap
corr_matrix = df[['IDS', 'SLS', 'TDS', 'Stance', 'Swing', 'Step', 'Stride', 'MMSE']].corr()
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=axes[1, 1], cbar_kws={'label': 'Correlation'})
axes[1, 1].set_title('Feature Correlation Matrix')

plt.tight_layout()
plt.savefig('synthetic_data_analysis.png', dpi=300, bbox_inches='tight')
print("\n✅ Visualization saved to 'synthetic_data_analysis.png'")
plt.show()

# ==================================
# ADDITIONAL VALIDATION PLOTS
# ==================================

fig2, axes2 = plt.subplots(2, 3, figsize=(15, 8))
axes2 = axes2.flatten()

features = ['IDS', 'SLS', 'TDS', 'Stance', 'Swing', 'Step']
for idx, feature in enumerate(features):
    axes2[idx].scatter(df[feature], df['MMSE'], alpha=0.5, c=df['MMSE'], cmap='viridis')
    axes2[idx].set_xlabel(f'{feature} (s)')
    axes2[idx].set_ylabel('MMSE')
    axes2[idx].set_title(f'{feature} vs MMSE (r={correlations[feature]:.3f})')
    
    # Trend line
    z = np.polyfit(df[feature], df['MMSE'], 1)
    p = np.poly1d(z)
    axes2[idx].plot(df[feature].sort_values(), p(df[feature].sort_values()), "r--", alpha=0.8)

plt.tight_layout()
plt.savefig('feature_correlations.png', dpi=300, bbox_inches='tight')
print("✅ Feature correlation plots saved to 'feature_correlations.png'")
plt.show()

# ==================================
# SAVE ANALYSIS REPORT
# ==================================

with open('dataset_report.txt', 'w') as f:
    f.write("="*60 + "\n")
    f.write("SYNTHETIC MMSE TRAINING DATA REPORT\n")
    f.write("="*60 + "\n\n")
    
    f.write(f"Total Samples: {len(df)}\n\n")
    
    f.write("MMSE Distribution by Category:\n")
    f.write(str(df.groupby('Category')['MMSE'].describe()) + "\n\n")
    
    f.write("Feature Statistics:\n")
    f.write(str(df.describe()) + "\n\n")
    
    f.write("Correlations with MMSE:\n")
    f.write(str(correlations) + "\n\n")
    
    f.write("Expected Model Performance:\n")
    f.write("- Strong negative correlation between stride time and MMSE\n")
    f.write("- Strong negative correlation between double support times and MMSE\n")
    f.write("- Strong positive correlation between SLS and MMSE\n")
    f.write("- Expected LSTM accuracy: 85-95% (MAE < 2 points)\n")

print("✅ Analysis report saved to 'dataset_report.txt'")

print("\n" + "="*60)
print("HIGH-ACCURACY SYNTHETIC DATA GENERATION COMPLETE!")
print("="*60)
print("\n📁 Files created:")
print("  1. MMSE_DATA.csv (training data)")
print("  2. synthetic_data_analysis.png (overview plots)")
print("  3. feature_correlations.png (detailed correlations)")
print("  4. dataset_report.txt (statistical summary)")
print("\n🚀 Ready to train your LSTM model!")

import os
import pandas as pd

# Check if file exists
if os.path.exists('MMSE_DATA.csv'):
    print(f"✅ File found at: {os.path.abspath('MMSE_DATA.csv')}")
    df = pd.read_csv('MMSE_DATA.csv')
    print(f"✅ Contains {len(df)} samples")
    print(df.head())
else:
    print("❌ File not found in current directory")
    print(f"Current directory: {os.getcwd()}")
    