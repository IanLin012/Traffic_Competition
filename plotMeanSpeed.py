import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import os
from datetime import datetime

# variables
year = 2025
month = 5
day = 10
# gatePairId = "01F0029N-01F0017N"
highway_no = "3"
start_gantry = "0217"
end_gantry = "0447"
direction = "N"

def extract_gantry_id(tag):
    return tag[3:7]

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
            current_time = datetime(year, month, day, hour, minute)
            timestamps.append(current_time)

            speed_sum = {vt: 0 for vt in vehicle_types}
            speed_count = {vt: 0 for vt in vehicle_types}

            # Loop through each ETagPairLive
            for pair in root.findall(".//ns:ETagPairLive", ns):
                pair_id_elem = pair.find("ns:ETagPairId", ns)
                if pair_id_elem is None:
                    continue
                pair_id = pair_id_elem.text

                try:
                    start, end = pair_id.split("-")
                    # Check direction and gantry range
                    if start[1] == highway_no and start[-1] == direction and end[-1] == direction:
                        start_id = extract_gantry_id(start)
                        end_id = extract_gantry_id(end)

                        if direction == "N":
                            in_range = start_gantry <= start_id <= end_gantry and start_gantry <= end_id <= end_gantry and start_id > end_id
                        elif direction == "S":
                            in_range = start_gantry <= start_id <= end_gantry and start_gantry <= end_id <= end_gantry and start_id < end_id
                        else:
                            in_range = False

                        if in_range:
                            # Process this pair
                            for flow in pair.findall("ns:Flows/ns:Flow", ns):
                                vt_elem = flow.find("ns:VehicleType", ns)
                                spd_elem = flow.find("ns:SpaceMeanSpeed", ns)

                                if vt_elem is not None and spd_elem is not None:
                                    vt = vt_elem.text
                                    if vt in vehicle_types:
                                        try:
                                            spd = float(spd_elem.text)
                                            speed_sum[vt] += spd
                                            speed_count[vt] += 1
                                        except ValueError:
                                            continue

                except ValueError:
                    continue  # malformed ID

            for vt in vehicle_types:
                if speed_count[vt] > 0:
                    avg = speed_sum[vt] / speed_count[vt]
                else:
                    avg = None
                time_series[vt].append(avg)

        except (FileNotFoundError, ET.ParseError):
            timestamps.append(datetime(year, month, day, hour, minute))
            for vt in vehicle_types:
                time_series[vt].append(None)


# Plotting
plt.figure(figsize=(14, 7))
for vt in vehicle_types:
    plt.plot(timestamps, time_series[vt], label=f"Vehicle Type {vt}")

plt.title(f"Space Mean Speed at Highway No.{highway_no}, Gate {start_gantry}~{end_gantry}({direction}) — {year:04d}-{month:02d}-{day:02d}")
plt.xlabel("Time")
plt.ylabel("Mean Speed (km/h)")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
# plt.show()

os.makedirs("plot", exist_ok=True)
plt.savefig(f"plot/mean_speed_{highway_no}_{start_gantry}_{end_gantry}_{direction}_{year:04d}{month:02d}{day:02d}.png", dpi=300)
