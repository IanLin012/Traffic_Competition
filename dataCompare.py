import pandas as pd
from tqdm import tqdm

# Settings
# Define the range of mileage to be analyzed
min_mileage = 50 #206.6 #021.7
max_mileage = 75 #223.5 #044.7


average_speed_file = 'Data/2024_鶯歌系統-高原假日資料.csv'
route_geometry_file = 'Data/2025_Route_Geometry/N0030_北區_主線.csv'
export_file = 'Data/Export/2024_鶯歌系統-高原假日資料_combined.csv'
temp_file = 'Data/Export/.temp'
# Step 1: Read data from average_speed.csv and route_geometry.csv

average_speed = pd.read_csv(average_speed_file, encoding='utf-8')
# column_names = ['TimeStamp', 'GantryFrom', 'GantryTo', 'VehicleType', 'Speed', 'Volume']
route_geometry = pd.read_csv(route_geometry_file, encoding='big5')
# col: 調查日期,國道名稱,國道編號,方向,樁號,里程,原始坐標E,原始坐標N,經緯度坐標Lon,經緯度坐標Lat,鋪面種類,路幅寬,全路幅寬,車道數,車道1寬,車道2寬,車道3寬,車道4寬,車道5寬,車道6寬,槽化區,槽化區寬,內路肩,內路肩寬,外路肩,外路肩寬,輔助車道1,輔助車道1寬,輔助車道2,輔助車道2寬,輔助車道3,輔助車道3寬,避車彎,曲率半徑,縱向坡度,橫向坡度
# Optimize performance by only selecting necessary mileage
route_dict = {}
with open(temp_file, 'w') as f:
    f.write("調查日期,國道名稱,國道編號,方向,樁號,里程,原始坐標E,原始坐標N,經緯度坐標Lon,經緯度坐標Lat,鋪面種類,路幅寬,全路幅寬,車道數,車道1寬,車道2寬,車道3寬,車道4寬,車道5寬,車道6寬,槽化區,槽化區寬,內路肩,內路肩寬,外路肩,外路肩寬,輔助車道1,輔助車道1寬,輔助車道2,輔助車道2寬,輔助車道3,輔助車道3寬,避車彎,曲率半徑,縱向坡度,橫向坡度\n")
    for index, row in route_geometry.iterrows():
        mileage = (float)(row['里程'])/1000
        if min_mileage <= mileage <= max_mileage:
            f.write(str(row['調查日期']) + "," + str(row['國道名稱']) + "," + str(row['國道編號']) + "," + str(row['方向']) + "," + str(row['樁號']) + "," + str(row['里程']) + "," + str(row['原始坐標E']) + "," + str(row['原始坐標N']) + "," + str(row['經緯度坐標Lon']) + "," + str(row['經緯度坐標Lat']) + "," + str(row['鋪面種類']) + "," + str(row['路幅寬']) + "," + str(row['全路幅寬']) + "," + str(row['車道數']) + "," + str(row['車道1寬']) + "," + str(row['車道2寬']) + "," + str(row['車道3寬']) + "," + str(row['車道4寬']) + "," + str(row['車道5寬']) + "," + str(row['車道6寬']) + "," + str(row['槽化區']) + "," + str(row['槽化區寬']) + "," + str(row['內路肩']) + "," + str(row['內路肩寬']) + "," + str(row['外路肩']) + "," + str(row['外路肩寬']) + "," + str(row['輔助車道1']) + "," + str(row['輔助車道1寬']) + "," + str(row['輔助車道2']) + "," + str(row['輔助車道2寬']) + "," + str(row['輔助車道3']) + "," + str(row['輔助車道3寬']) + "," + str(row['避車彎']) + "," + str(row['曲率半徑']) + "," + str(row['縱向坡度']) + "," + str(row['橫向坡度']) + "\n")
    f.close()
route_geometry = pd.read_csv(temp_file, encoding='utf-8')

# Create new file to store the data
with open(export_file, 'w') as f:
    f.write("時間戳,方向,里程起,里程迄,路段數,鋪面種類,路幅寬,全路幅寬,車道數最小,車道數最大,車道1寬,車道2寬,車道3寬,車道4寬,車道5寬,車道6寬,槽化區,內路肩,內路肩寬,外路肩,外路肩寬,輔助車道最小,輔助車道最大,輔助車道1寬,輔助車道2寬,輔助車道3寬,避車彎,曲率半徑,縱向坡度,橫向坡度")
    f.close()

# Step 2: Get gantry information and record mileage between
column_recored = 0
with tqdm(total=average_speed.shape[0]) as pbar:
    for index, row in average_speed.iterrows():
        time_stamp = row['TimeStamp']
        gantry_from = row['GantryFrom']
        gantry_to = row['GantryTo']
        direction = row['GantryFrom'][-1]
        mileage_from = (float)(gantry_from[3:7])/10
        mileage_to = (float)(gantry_to[3:7])/10
        # Read from dictionary and skip Step 3 if found
        row_data = ""
        if (direction, mileage_from, mileage_to) in route_dict:
            row_data = route_dict[(direction, mileage_from, mileage_to)]
        else: 
    # Step 3: Compare mileage from route_geometry.csv
            # Initialize variables for calculation
            section_count = 0
            rode_type = ''
            rode_width = 0
            all_rode_width = 0
            lane_count = (0,0)
            lane_width = [0,0,0,0,0,0]
            channelized_area = ''
            channelized_area_width = 0
            inner_shoulder = ''
            inner_shoulder_width = 0
            outer_shoulder = ''
            outer_shoulder_width = 0
            assist_lane = (0,0)
            assist_lane_width = [0,0,0]
            avoidance_curve = ''
            curvature_radius = 0
            longitudinal_slope = 0
            lateral_slope = 0
            
            for index, row in route_geometry.iterrows():
                mileage = (float)(row['里程'])/1000
                if (direction == 'N'):
                    if (row['方向'] == '往北') & (mileage_to < mileage < mileage_from):
                        section_count += 1
                    elif (mileage > mileage_from):
                        break
                    else:
                        continue
                elif (direction == 'S'):
                    if (row['方向'] == '往南') & (mileage_from < mileage < mileage_to):
                        section_count += 1
                    elif (row['方向'] == '往南') & (mileage > mileage_from):
                        break
                    else:
                        continue
                else:
                    print("Error: Invalid direction.")
                    break

        # Step 4: Average / Record the data from route_geometry.csv
            # print(direction, mileage_from, "~", mileage_to, " found ", section_count, " sections.")
            # rode type
                if ((rode_type == '') | (rode_type == row['鋪面種類'])):
                    rode_type = row['鋪面種類']
                else:
                    rode_type = '混合'
                # rode width
                if (rode_width == 0):
                    rode_width = row['路幅寬']
                else:
                    rode_width = (rode_width + row['路幅寬'])/2
                # all rode width
                if (all_rode_width == 0):
                    all_rode_width = row['全路幅寬']
                else:
                    all_rode_width = (all_rode_width + row['全路幅寬'])/2
                # lane count
                if (lane_count == (0,0)):
                    lane_count = (row['車道數'], row['車道數'])
                else:
                    lane_count = (min(lane_count[0], row['車道數']), max(lane_count[1], row['車道數'])) 
                # lane width
                if (lane_width == [0,0,0,0,0,0]):
                    lane_width = [row['車道1寬'], row['車道2寬'], row['車道3寬'], row['車道4寬'], row['車道5寬'], row['車道6寬']]
                else:
                    for i in range(6):
                        if (row['車道' + str(i+1) + '寬'] == 0):
                            continue
                        else:
                            lane_width[i] = (row['車道' + str(i+1) + '寬'] + lane_width[i]) / 2
                # channelized area
                if ((channelized_area == '') | (channelized_area == row['槽化區'])):
                    channelized_area = row['槽化區']
                else:
                    channelized_area = '部分'
                # channelized area width
                if (channelized_area_width == 0):
                    channelized_area_width = row['槽化區寬']
                else:
                    channelized_area_width = (channelized_area_width + row['槽化區寬'])
                # inner shoulder 
                if ((inner_shoulder == '') | (inner_shoulder == row['內路肩'])):
                    inner_shoulder = row['內路肩']
                else:
                    inner_shoulder = '部分'
                # inner shoulder width
                if (inner_shoulder_width == 0):
                    inner_shoulder_width = row['內路肩寬']
                else:
                    inner_shoulder_width = (inner_shoulder_width + row['內路肩寬'])/2
                # outer shoulder
                if ((outer_shoulder == '') | (outer_shoulder == row['外路肩'])):
                    outer_shoulder = row['外路肩']
                else:
                    outer_shoulder = '部分'
                # outer shoulder width
                if (outer_shoulder_width == 0):
                    outer_shoulder_width = row['外路肩寬']
                else:
                    outer_shoulder_width = (outer_shoulder_width + row['外路肩寬'])/2
                # assist lane
                if ((row['輔助車道1'] == '無') & (row['輔助車道2'] == '無') & (row['輔助車道3'] == '無')):
                    assist_lane = (0, assist_lane[1])
                if (row['輔助車道1'] != '無'):
                    assist_lane = (min(1, assist_lane[0]), max(1, assist_lane[1]))
                if (row['輔助車道2'] != '無'):
                    assist_lane = (min(2, assist_lane[0]), max(2, assist_lane[1]))
                if (row['輔助車道3'] != '無'):
                    assist_lane = (min(3, assist_lane[0]), max(3, assist_lane[1])) 
                # assist lane width
                if (assist_lane_width == [0,0,0]):
                    assist_lane_width = [row['輔助車道1寬'], row['輔助車道2寬'], row['輔助車道3寬']]
                else:
                    for i in range(3):
                        if (row['輔助車道' + str(i+1) + '寬'] == 0):
                            continue
                        else:
                            assist_lane_width[i] = (assist_lane_width[i] + row['輔助車道' + str(i+1) + '寬'])/2
                    # assist_lane_width = ((assist_lane_width[0] + row['輔助車道1寬'])/2, (assist_lane_width[1] + row['輔助車道2寬'])/2, (assist_lane_width[2] + row['輔助車道3寬'])/2)
                # avoidance curve
                if ((avoidance_curve == '') | (avoidance_curve == row['避車彎'])):
                    avoidance_curve = row['避車彎']
                else:
                    avoidance_curve = '部分'
                # curvature radius
                if (curvature_radius == 0):
                    curvature_radius = row['曲率半徑']
                else:
                    curvature_radius = (curvature_radius + row['曲率半徑'])/2
                # longitudinal slope
                if (longitudinal_slope == 0):
                    longitudinal_slope = row['縱向坡度']
                else:
                    longitudinal_slope = (longitudinal_slope + row['縱向坡度'])/2
                # lateral slope
                if (lateral_slope == 0):
                    lateral_slope = row['橫向坡度']
                else:
                    lateral_slope = (lateral_slope + row['橫向坡度'])/2
                
                row_data = direction + "," + str(mileage_from) + "," + str(mileage_to) + "," + str(section_count) + "," + rode_type + "," + str(round(rode_width, 4)) + "," + str(round(all_rode_width, 4)) + "," + str(lane_count[0]) + "," + str(lane_count[1]) + "," + str(round(lane_width[0], 4)) + "," + str(round(lane_width[1], 4)) + "," + str(round(lane_width[2], 4)) + "," + str(round(lane_width[3], 4)) + "," + str(round(lane_width[4], 4)) + "," + str(round(lane_width[5], 4)) + "," + str(channelized_area) + "," + str(inner_shoulder) + "," + str(round(inner_shoulder_width, 4)) + "," + str(outer_shoulder) + "," + str(round(outer_shoulder_width, 4)) + "," + str(assist_lane[0]) + "," + str(assist_lane[1]) + "," + str(round(assist_lane_width[0], 4)) + "," + str(round(assist_lane_width[1], 4)) + "," + str(round(assist_lane_width[2], 4)) + "," + str(avoidance_curve) + "," + str(round(curvature_radius, 4)) + "," + str(round(longitudinal_slope, 4)) + "," + str(round(lateral_slope, 4))
                route_dict[(direction, mileage_from, mileage_to)] = row_data

    # Step 5: Write the data to a new file
        with open(export_file, 'a') as f:
            column_recored += 1
            f.write(time_stamp + "," + row_data + "\n")
            f.close()
        
        pbar.update(1)
        #if ((column_recored % 5000 == 0) or (column_recored == average_speed.shape[0])):
        #   print(column_recored, " / ", average_speed.shape[0], end="")
        #   print(" -------- ", f"{column_recored/average_speed.shape[0]*100:.2f}", "%")
