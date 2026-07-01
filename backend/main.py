import serial
import csv
import time

# ---------------- CONFIG ----------------
PORT = "COM3"        # Change if your Arduino is on another port
BAUD = 115200
OUTPUT_FILE = "data/gait_data.csv"
# ----------------------------------------

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)  # allow Arduino to reset
    print(f"Connected to {PORT}")
except Exception as e:
    print("ERROR: Could not open serial port")
    print(e)
    exit()

with open(OUTPUT_FILE, "w", newline="") as file:
    writer = csv.writer(file)

    # CSV Header
    writer.writerow([
        "time_ms",
        "leftY_dps",
        "rightY_dps",
        "left_flag",
        "right_flag"
    ])

    print("Recording data... Press CTRL + C to stop\n")

    try:
        while True:
            line = ser.readline().decode("utf-8").strip()

            if line:
                data = line.split(",")

                if len(data) == 5:
                    writer.writerow(data)
                    print(data)

    except KeyboardInterrupt:
        print("\nStopped by user")

ser.close()
print("Serial port closed")
