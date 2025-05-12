import xml.etree.ElementTree as ET
import os
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

# --- Configurable Variables ---
year, month, day = 2025, 5, 10
static_file = "data/VD/VD_static.xml"
real_time_folder = f"data/VD/{year:04d}/{month:02d}/{day:02d}/"
plot_dir = "plot/"
start_gantry = "0005"
end_gantry = "0050"
direction = "N"
highway_no = "3"

# Ensure plot directory exists
os.makedirs(plot_dir, exist_ok=True)

# Namespace
ns = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}

# --- Step 1: Parse Static File ---
def extract_mile_num(location_mile):
    """Convert LocationMile like '25+000' to float (25.0)."""
    try:
        km, m = location_mile.split('+')
        return int(km)*1000 + int(m)
    except:
        return None

def gantry_in_range(mile, start, end):
    return start <= mile <= end

vdid_info = {}
start_mile = int(start_gantry) * 100
end_mile = int(end_gantry) * 100
# is_north = direction == "N"

tree = ET.parse(static_file)
root = tree.getroot()

for vd in root.findall(".//ns:VD", ns):
    vdid = vd.find("ns:VDID", ns).text
    location_mile = vd.find("ns:LocationMile", ns)
    road_dir_elem = vd.find(".//ns:RoadDirection", ns)
    road_id_elem = vd.find(".//ns:RoadID", ns)
    link_id_elem = vd.find(".//ns:DectionLink/ns:LinkID", ns)
    
    if location_mile is None or road_dir_elem is None or link_id_elem is None:
        continue

    mile_val = extract_mile_num(location_mile.text)
    road_dir = road_dir_elem.text
    road_id = road_id_elem.text[-2]

    if mile_val is not None and road_dir == direction and highway_no == road_id:
        if gantry_in_range(mile_val, start_mile, end_mile):
            vdid_info[vdid] = {
                "LocationMile": location_mile.text,
                "RoadDirection": road_dir,
                "LinkID": link_id_elem.text
            }



# test print
print(f"Filtered VDIDs: {list(vdid_info.keys())}")
print(f"{start_mile} ~ {end_mile}, {direction}, {road_id}")

'''
for vd in root.findall(".//ns:VD", ns):
    location_mile = vd.find("ns:LocationMile", ns)
    road_dir_elem = vd.find(".//ns:RoadDirection", ns)
    if location_mile is not None and road_dir_elem is not None:
        print(vd.find("ns:VDID", ns).text, extract_mile_num(location_mile.text), road_dir_elem.text)
'''


# --- Step 2: Parse Real-Time Files and Collect Metrics ---

vehicle_types = ["S", "L", "T"]
metrics = {vt: {"Speed": [], "Volume": [], "Occupancy": []} for vt in vehicle_types}
timestamps = []

for hour in range(24):
    print(f"Processing hour {hour}...")
    for minute in range(0, 60, 1):
        ts = f"{hour:02d}{minute:02d}"
        file_path = os.path.join(real_time_folder, f"VDLive_{ts}.xml")
        if not os.path.exists(file_path):
            continue

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            timestamps.append(datetime(year, month, day, hour, minute))

            # Temp accumulators for this timestamp
            temp_data = {vt: {"Speed": [], "Volume": [], "Occupancy": []} for vt in vehicle_types}

            for vd in root.findall(".//ns:VDLive", ns):
                vdid = vd.find("ns:VDID", ns).text
                if vdid not in vdid_info:
                    continue


                for lane in vd.findall(".//ns:Lane", ns):
                    occ_elem = lane.find("ns:Occupancy", ns)
                    lane_occupancy = int(occ_elem.text) if occ_elem is not None else 0

                    for veh in lane.findall(".//ns:Vehicle", ns):
                        vt = veh.find("ns:VehicleType", ns).text
                        if vt not in vehicle_types:
                            continue

                        volume = int(veh.find("ns:Volume", ns).text)
                        speed = int(veh.find("ns:Speed", ns).text)
                        
                        temp_data[vt]["Speed"].append(speed)
                        temp_data[vt]["Volume"].append(volume)
                        temp_data[vt]["Occupancy"].append(lane_occupancy)

            for vt in vehicle_types:
                # Average or sum based on metric
                def avg(x): return sum(x) / len(x) if x else 0
                def total(x): return sum(x)

                metrics[vt]["Speed"].append(avg(temp_data[vt]["Speed"]))
                metrics[vt]["Volume"].append(total(temp_data[vt]["Volume"]))
                metrics[vt]["Occupancy"].append(avg(temp_data[vt]["Occupancy"]))

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")



# test print
print(metrics)

# --- Step 3: Plot ---

fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
titles = ["Speed (km/h)", "Volume (vehicles)", "Occupancy (%)"]
fields = ["Speed", "Volume", "Occupancy"]
colors = {"S": "blue", "L": "green", "T": "red"}

for i, field in enumerate(fields):
    ax = axs[i]
    for vt in vehicle_types:
        ax.plot(timestamps, metrics[vt][field], label=f"Type {vt}", color=colors[vt])
    ax.set_ylabel(titles[i])
    ax.legend()
    ax.grid(True)

axs[-1].set_xlabel("Time")
fig.suptitle(f"VD Data - {year:04d}-{month:02d}-{day:02d}")
fig.autofmt_xdate()
plt.tight_layout()

# Save to plot directory
plot_file = os.path.join(plot_dir, f"vd_summary_{year:04d}{month:02d}{day:02d}.png")
plt.savefig(plot_file)
print(f"Plot saved to {plot_file}")

