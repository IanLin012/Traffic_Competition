import os
import requests
import gzip
import shutil

# Step 1: Assign date variables
year = 2025
month = 5
day = 9

# Format date components
date_str = f"{year:04d}{month:02d}{day:02d}"
base_url = "https://tisvcloud.freeway.gov.tw/history/motc20/ETag"
save_dir = os.path.join("data", "eTag", f"{year:04d}", f"{month:02d}", f"{day:02d}")
os.makedirs(save_dir, exist_ok=True)

# Step 2: Check if .gz files already exist
existing_gz_files = [f for f in os.listdir(save_dir) if f.endswith(".gz")]

if existing_gz_files:
    print(f"Data for {date_str} already exists in '{save_dir}'. Skipping download.")
else:
    print(f"Downloading data for {date_str}...")

    # Step 3: Download all hourly files for the day
    for hour in range(24):
        for minute in range(0, 60, 5):  # Assuming data every 5 minutes
            timestamp = f"{hour:02d}{minute:02d}"
            filename = f"ETagPairLive_{timestamp}.xml.gz"
            file_url = f"{base_url}/{date_str}/{filename}"
            file_path = os.path.join(save_dir, filename)

            # Skip download if file already exists
            if os.path.exists(file_path):
                continue

            try:
                response = requests.get(file_url, timeout=10)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {filename}")
                else:
                    print(f"File not found on server: {filename}")
            except requests.RequestException as e:
                print(f"Error downloading {filename}: {e}")

# Step 4: Extract .gz files to .xml
print(f"Extracting .gz files in '{save_dir}'...")
for gz_file in os.listdir(save_dir):
    if gz_file.endswith('.gz'):
        gz_path = os.path.join(save_dir, gz_file)
        xml_filename = gz_file.replace('.gz', '')
        xml_path = os.path.join(save_dir, xml_filename)

        # Skip extraction if .xml already exists
        if os.path.exists(xml_path):
            continue

        try:
            with gzip.open(gz_path, 'rb') as f_in:
                with open(xml_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"Extracted: {gz_file} → {xml_filename}")
        except Exception as e:
            print(f"Error extracting {gz_file}: {e}")

print("All done!")

