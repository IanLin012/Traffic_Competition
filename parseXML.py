import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import os
from datetime import datetime

# variables
year = 2025
month = 5
day = 10
gatePairId = "01F0029N-01F0017N"

fileLoc = f"data/eTag/{year:04d}/{month:02d}/{day:02d}/"

# Namespace
ns = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}
vehicle_types = ["31", "32", "41", "42", "5"]

# Data storage
timestamps = []
time_series = {vt: [] for vt in vehicle_types}

for hour in range(24):
    for minute in range(0, 60, 5):
        timestamp = f"{hour:02d}{minute:02d}"
        file = f"{fileLoc}ETagPairLive_{timestamp}.xml"

        try:
            tree = ET.parse(file)
            root = tree.getroot()

            # Find matching ETagPairLive
            matched_pair = None
            for pair in root.findall(".//ns:ETagPairLive", ns):
                pair_id_elem = pair.find("ns:ETagPairId", ns)
                if pair_id_elem is not None and pair_id_elem.text == gatePairId:
                    matched_pair = pair
                    break

            # Prepare time entry
            current_time = datetime(year, month, day, hour, minute)
            timestamps.append(current_time)

            if matched_pair:
                # Sum and count for averaging
                speed_sum = {vt: 0 for vt in vehicle_types}
                speed_count = {vt: 0 for vt in vehicle_types}

                for flow in matched_pair.findall("ns:Flows/ns:Flow", ns):
                    vt_elem = flow.find("ns:VehicleType", ns)
                    spd_elem = flow.find("ns:SpaceMeanSpeed", ns)
                    if vt_elem is not None and spd_elem is not None:
                        vt = vt_elem.text
                        if vt in vehicle_types:
                            try:
                                speed = float(spd_elem.text)
                                speed_sum[vt] += speed
                                speed_count[vt] += 1
                            except ValueError:
                                continue

                for vt in vehicle_types:
                    if speed_count[vt] > 0:
                        avg = speed_sum[vt] / speed_count[vt]
                    else:
                        avg = None
                    time_series[vt].append(avg)
            else:
                # No match — fill with None
                for vt in vehicle_types:
                    time_series[vt].append(None)

        except (FileNotFoundError, ET.ParseError):
            # Still log timestamp and fill None for all types
            current_time = datetime(year, month, day, hour, minute)
            timestamps.append(current_time)
            for vt in vehicle_types:
                time_series[vt].append(None)

# Plotting
plt.figure(figsize=(14, 7))
for vt in vehicle_types:
    plt.plot(timestamps, time_series[vt], label=f"Vehicle Type {vt}")

plt.title(f"Space Mean Speed at Gate {gatePairId} — {year:04d}-{month:02d}-{day:02d}")
plt.xlabel("Time")
plt.ylabel("Mean Speed (km/h)")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
# plt.show()

os.makedirs("plot", exist_ok=True)
plt.savefig(f"plot/mean_speed_{gatePairId}_{year:04d}{month:02d}{day:02d}.png", dpi=300)
