import pandas as pd
import unicodedata
import time
from map_general.map_hang_muc_xe.map_hang_muc_xe_final import MapHangMucXe

model = MapHangMucXe()

def normalize_text(text):
    return unicodedata.normalize('NFC', str(text).strip()).lower()

input_file = 'du_lieu_da_mapping.xlsx'
output_file = 'output.xlsx'

df = pd.read_excel(input_file, sheet_name="Xe ô tô con")

for idx, row in df.iterrows():
    print("idx: ", idx, row)
    text_raw = row['TÊN VẬT TƯ, PHỤ TÙNG']
    text = normalize_text(text_raw)

    start = time.time()
    rs = model.map_hang_muc_xe(text)
    duration = time.time() - start

    df.at[idx, 'description_map'] = rs['description_map']
    df.at[idx, 'description_code'] = rs['description_code']

# df.to_excel('Xe ô tô con_1.xlsx', index=False)

