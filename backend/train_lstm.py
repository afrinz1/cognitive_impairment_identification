# ==================================
# TRAIN LSTM MODEL ON SYNTHETIC DATA
# ==================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input
from sklearn.model_selection import train_test_split
import os

print("="*60)
print("LSTM MODEL TRAINING")
print("="*60)

# Create directories if they don't exist
os.makedirs('models', exist_ok=True)
os.makedirs('results', exist_ok=True)

# --------------------------
# 1. Load Training Data
# --------------------------
print("\n📂 Loading training data...")
mmsedata = pd.read_csv("dataset/MMSE_DATA.csv")

target = np.array(mmsedata['MMSE'], dtype=float)
del mmsedata['MMSE']
data = np.array(mmsedata, dtype=float)

print(f"✅ Loaded {len(data)} training samples")

# Normalize
target = target / 30.0  # ✅ Changed: normalize to 0-1 properly

# Reshape for LSTM: [samples, timesteps, features]
dat = []
for i in range(len(data)):
    lt = []
    for j in range(len(data[i])):
        lt.append([data[i][j]])  # ✅ Changed: remove /1000 normalization
    dat.append(lt)
data = np.array(dat, dtype=float)

# --------------------------
# 2. Train-Test Split
# --------------------------
print("\n🔀 Splitting data...")
x_train, x_test, y_train, y_test = train_test_split(
    data, target, 
    test_size=0.25, 
    random_state=42
)

print(f"Training samples: {len(x_train)}")
print(f"Testing samples: {len(x_test)}")
print(f"Input shape: {x_train.shape}")

# --------------------------
# 3. Build LSTM Model (FIXED FOR KERAS 3.x)
# --------------------------
print("\n🏗️  Building LSTM model...")
model = Sequential([
    Input(shape=(x_train.shape[1], 1)),  #  Use Input layer instead
    LSTM(64, return_sequences=True),      #  Increased units for better learning
    LSTM(32, return_sequences=False),     #  Second layer
    Dense(16, activation='relu'),         #  Added dense layer
    Dense(1, activation='sigmoid')        #  Output layer (0-1 range)
])

model.compile(
    loss='mean_squared_error',            #  Better for regression
    optimizer='adam',
    metrics=['mae']                        #  Track Mean Absolute Error
)

model.summary()

# --------------------------
# 4. Train Model
# --------------------------
print("\n🎯 Training model...")
history = model.fit(
    x_train, y_train, 
    epochs=100,                            #  Reduced for faster testing
    batch_size=32,
    validation_data=(x_test, y_test),
    verbose=1
)

# --------------------------
# 5. Evaluate Model
# --------------------------
print("\n📊 Evaluating model...")
results = model.predict(x_test)

# Calculate metrics
mae = np.mean(np.abs(results.flatten() * 30 - y_test * 30))
rmse = np.sqrt(np.mean((results.flatten() * 30 - y_test * 30) ** 2))

print(f"\n✅ Mean Absolute Error: {mae:.2f} MMSE points")
print(f"✅ Root Mean Squared Error: {rmse:.2f} MMSE points")

# --------------------------
# 6. Visualizations
# --------------------------
plt.figure(figsize=(15, 5))

# Plot 1: Training history
plt.subplot(1, 3, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Model Loss Over Time')
plt.legend()
plt.grid(True)

# Plot 2: MAE over time
plt.subplot(1, 3, 2)
plt.plot(history.history['mae'], label='Training MAE')
plt.plot(history.history['val_mae'], label='Validation MAE')
plt.xlabel('Epoch')
plt.ylabel('MAE')
plt.title('Mean Absolute Error Over Time')
plt.legend()
plt.grid(True)

# Plot 3: Predictions vs Actual
plt.subplot(1, 3, 3)
plt.scatter(y_test * 30, results.flatten() * 30, alpha=0.5)
plt.plot([0, 30], [0, 30], 'r--', linewidth=2, label='Perfect Prediction')
plt.xlabel('Actual MMSE')
plt.ylabel('Predicted MMSE')
plt.title(f'Predictions vs Actual (MAE: {mae:.2f})')
plt.legend()
plt.grid(True)
plt.xlim(0, 30)
plt.ylim(0, 30)

plt.tight_layout()
plt.savefig('results/training_results.png', dpi=300, bbox_inches='tight')
print("\n✅ Training plots saved to 'results/training_results.png'")
plt.show()

# --------------------------
# 7. Save Model
# --------------------------
model.save('models/lstm_mmse_model.keras')  # ✅ Use .keras extension for Keras 3
print("\n✅ Model saved to 'models/lstm_mmse_model.keras'")

# Save model info
model_info = {
    'mae': mae,
    'rmse': rmse,
    'training_samples': len(x_train),
    'test_samples': len(x_test),
    'epochs': len(history.history['loss']),
    'final_loss': history.history['loss'][-1],
    'final_val_loss': history.history['val_loss'][-1]
}

import json
with open('models/model_info.json', 'w') as f:
    json.dump(model_info, f, indent=4)

print("✅ Model info saved to 'models/model_info.json'")

print("\n" + "="*60)
print("TRAINING COMPLETE!")
print("="*60)
print(f"\n📊 Final Metrics:")
print(f"   MAE: {mae:.2f} points")
print(f"   RMSE: {rmse:.2f} points")
print(f"   Training samples: {len(x_train)}")
print(f"   Test samples: {len(x_test)}")