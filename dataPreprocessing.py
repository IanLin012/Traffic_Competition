"""
import pandas as pd
from tqdm import tqdm

print("讀取 CSV 檔案中...")
df_geom = pd.read_csv('C:\\Users\\drlin\\Desktop\\交通部競賽\\114年國道智慧交通管理創意競賽\\道路幾何特性\\2024combine_filtered3.csv')
df_speed = pd.read_csv('C:\\Users\\drlin\\Desktop\\交通部競賽\\114年國道智慧交通管理創意競賽\\車速中位數\\2024.csv')
print("CSV 檔案讀取完成。")

print("開始計算交通狀態...")
traffic_status = []
for i in tqdm(range(len(df_speed)), desc="處理進度"):
    vol = df_speed.loc[i, 'Volume']
    speed = df_speed.loc[i, 'Speed']
    
    if vol == 0:
        status = '無車流'
    elif vol != 0 and speed >= 80:
        status = '正常'
    elif vol != 0 and 0 <= speed < 80:
        status = '壅塞'
    
    traffic_status.append(status)

df_geom['交通狀態'] = traffic_status
print("交通狀態計算完成。")

df_geom.to_csv('2024combine_updated.csv', index=False)
print("輸出 CSV 檔案完成。")
"""

import pandas as pd
from tqdm import tqdm

df = pd.read_csv('原檔案位置')
#df = df[df["交通狀態"] != "無車流"]

lane_cols = ['車道1寬', '車道2寬', '車道3寬', '車道4寬', '車道5寬', '車道6寬']

def calc_avg(row):
    valid_values = [x for x in row[lane_cols] if x != 0]
    if valid_values:
        return sum(valid_values) / len(valid_values)
    else:
        return 0

tqdm.pandas(desc="移除車道寬")

df['平均車道寬'] = df.progress_apply(calc_avg, axis=1)

df.drop(columns=lane_cols, inplace=True)

df.to_csv('目的檔案位置', index=False)
