import os
import xml.etree.ElementTree as ET
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for remote/server
import matplotlib.pyplot as plt
from tqdm import tqdm

# --- Configurable Variables ---
year, month, day = 2025, 5, 9
static_file = "data/VD/VD_static.xml"
real_time_folder = f"data/VD/{year:04d}/{month:02d}/{day:02d}/"
plot_dir = "plot/"
start_gantry = "0217"
end_gantry = "0447"
direction = "N"
highway_no = "3"
interval = 2 # ? min

# Ensure plot directory exists
os.makedirs(plot_dir, exist_ok=True)

# Namespace
ns = {'ns': 'http://traffic.transportdata.tw/standard/traffic/schema/'}

# --- Step 1: Parse Static File and Filter VDIDs ---
def extract_mile_num(location_mile):
    """Convert LocationMile like '25+000' to int meters (e.g., 25000)."""
    try:
        km, m = location_mile.split('+')
        return int(km) * 1000 + int(m)
    except:
        return None

def gantry_in_range(mile, start, end):
    return start <= mile <= end

start_mile = int(start_gantry) * 100
end_mile = int(end_gantry) * 100

vdid_info = {}
try:
    tree = ET.parse(static_file)
    root = tree.getroot()
    for vd in root.findall(".//ns:VD", ns):
        vdid = vd.find("ns:VDID", ns).text
        location_mile = vd.find("ns:LocationMile", ns)
        road_dir_elem = vd.find(".//ns:RoadDirection", ns)
        road_id_elem = vd.find(".//ns:RoadID", ns)
        link_id_elem = vd.find(".//ns:DectionLink/ns:LinkID", ns)

        if location_mile is None or road_dir_elem is None or road_id_elem is None or link_id_elem is None:
            continue

        mile_val = extract_mile_num(location_mile.text)
        road_dir = road_dir_elem.text
        road_id = road_id_elem.text[-2]

        if mile_val is not None and road_dir == direction and road_id == highway_no:
            if gantry_in_range(mile_val, start_mile, end_mile):
                vdid_info[vdid] = {
                    "LocationMile": location_mile.text,
                    "RoadDirection": road_dir,
                    "LinkID": link_id_elem.text
                }

except ET.ParseError as e:
    print(f"Error parsing static file: {e}")
    exit(1)

if not vdid_info:
    print("No VDIDs matched the specified gantry/direction range.")
    exit(0)

print(f"Filtered VDIDs: {list(vdid_info.keys())}")

# --- Step 2: Parse Real-Time Files and Collect Metrics ---

vehicle_types = ["S", "L", "T"]
metrics = {vt: {"Speed": [], "Volume": [], "Occupancy": [], "DataCount": 0} for vt in vehicle_types}
timestamps = []

with tqdm(total=24*60/interval) as pbar:
    for hour in range(24):
        # print(f"Processing hour {hour}...")
        for minute in range(0,60,interval):
            ts = f"{hour:02d}{minute:02d}"
            file_path = os.path.join(real_time_folder, f"VDLive_{ts}.xml")

            if not os.path.exists(file_path) or os.path.getsize(file_path) < 100:
                continue

            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
            except ET.ParseError as e:
                print(f"Parse error in {file_path}: {e}")
                continue

            # Temp accumulators for this timestamp
            temp_data = {vt: {"Speed": [], "Volume": [], "Occupancy": [], "DataCount": 0} for vt in vehicle_types}
            found_data = False

            for vd in root.findall(".//ns:VDLive", ns):
                vdid = vd.find("ns:VDID", ns)
                if vdid is None or vdid.text not in vdid_info:
                    continue

                found_data = True

                for lane in vd.findall(".//ns:Lane", ns):
                    occ_elem = lane.find("ns:Occupancy", ns)
                    try:
                        lane_occupancy = int(occ_elem.text) if occ_elem is not None else 0
                        lane_occupancy = max(lane_occupancy, 0)
                    except:
                        lane_occupancy = 0

                    for veh in lane.findall(".//ns:Vehicle", ns):
                        vt_elem = veh.find("ns:VehicleType", ns)
                        if vt_elem is None:
                            continue
                        vt = vt_elem.text
                        if vt not in vehicle_types:
                            continue

                        try:
                            volume = max(int(veh.find("ns:Volume", ns).text), 0)
                            speed = max(int(veh.find("ns:Speed", ns).text), 0)
                        except:
                            continue

                        temp_data[vt]["DataCount"] += 1 if volume != 0 else 0
                        temp_data[vt]["Speed"].append(speed)
                        temp_data[vt]["Volume"].append(volume)
                        temp_data[vt]["Occupancy"].append(lane_occupancy)

            if found_data:
                timestamps.append(datetime(year, month, day, hour, minute))
                for vt in vehicle_types:
                    def avg(x): return sum(x) / len(x) if x else 0
                    def total(x): return sum(x)

                    metrics[vt]["Speed"].append(total(temp_data[vt]["Speed"]) / temp_data[vt]["DataCount"])
                    metrics[vt]["Volume"].append(total(temp_data[vt]["Volume"]))
                    metrics[vt]["Occupancy"].append(avg(temp_data[vt]["Occupancy"]))
            pbar.update(1)
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
fig.suptitle(f"VD Data (Highway {highway_no}) - {year:04d}-{month:02d}-{day:02d}")
fig.autofmt_xdate()
plt.tight_layout()

plot_file = os.path.join(plot_dir, f"vd_summary_{year:04d}{month:02d}{day:02d}.png")
plt.savefig(plot_file)
print(f"✅ Plot saved to {plot_file}")

