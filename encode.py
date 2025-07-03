import pandas as pd
import json

def smooth_txt(txt):
    txt = txt.lower()
    alphabet = "0123456789abcdđefghijklmnopqrstuvwxyýỳỷỹỵzáàạảãăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữự"
    list_text_new = []
    for char in txt:
        if char in alphabet:
            list_text_new.append(char)
        else:
            list_text_new.append(" ")
    rs_check = "".join(list_text_new).strip()
    list_rs_check = rs_check.split(" ")
    list_rs_final = []
    for text in list_rs_check:
        if len(text.strip()) == 0:
            continue
        list_rs_final.append(text)
    if len(list_rs_final) == 0:
        return ""
    return " ".join(list_rs_final).strip()


df = pd.read_excel("danh-muc-baogiaxe-pvi.xlsx", sheet_name="process")

json_result = {}

ls_ma_hmuc = df['ma_hmuc'].fillna('').tolist()
ls_bo_phan = df['bo_phan'].fillna('').tolist()
ls_key_bo_phan = df['key_bo_phan'].fillna('').tolist()
ls_vi_tri = df['vi_tri'].fillna('').tolist()
ls_ten_hmuc = df['ten_hmuc'].fillna('').tolist()

set_bo_phan = []

count = 0

for idx, bo_phan in enumerate(ls_bo_phan):
    if not bo_phan:
        continue
    if ls_key_bo_phan[idx] == '':
        ls_key = []
    else:
        ls_key = ls_key_bo_phan[idx].split('|')
        ls_key = list(set([smooth_txt(item) for item in ls_key]))

    if ls_vi_tri[idx] == '':
        ls_vitri = []
    else:
        ls_vitri = ls_vi_tri[idx].split('|')
        ls_vitri = list(set([smooth_txt(item) for item in ls_vitri]))

    bo_phan_check = smooth_txt(bo_phan.lower())
    if bo_phan_check not in set_bo_phan:
        json_result[bo_phan_check] = {}
        json_result[bo_phan_check]['list_key'] = ls_key
        json_result[bo_phan_check]['list_vi_tri'] = []
        if ls_vitri:
            for vitri in ls_vitri:
                json_result[bo_phan_check]['list_vi_tri'].append({
                    "key_vi_tri": vitri,
                    "ma_hmuc": ls_ma_hmuc[idx],
                    "ten_hmuc": ls_ten_hmuc[idx]
                })
        else:
            json_result[bo_phan_check]['list_vi_tri'].append({
                "key_vi_tri": '',
                "ma_hmuc": ls_ma_hmuc[idx],
                "ten_hmuc": ls_ten_hmuc[idx]
            })
        json_result[bo_phan_check]['id_bo_phan'] = count
        count += 1
        set_bo_phan.append(bo_phan_check)
    else:
        ls_key_old = json_result[bo_phan_check]['list_key']
        ls_key_old.extend(ls_key)
        ls_key_new = list(set(ls_key_old))
        json_result[bo_phan_check]['list_key'] = ls_key_new
        if ls_vitri:
            for vitri in ls_vitri:
                json_result[bo_phan_check]['list_vi_tri'].append({
                    "key_vi_tri": vitri,
                    "ma_hmuc": ls_ma_hmuc[idx],
                    "ten_hmuc": ls_ten_hmuc[idx]
                })
        else:
            json_result[bo_phan_check]['list_vi_tri'].append({
                "key_vi_tri": '',
                "ma_hmuc": ls_ma_hmuc[idx],
                "ten_hmuc": ls_ten_hmuc[idx]
            })

def process_dict_bo_phan(dict_bo_phan):
    list_key = []
    list_vitri_all = []
    for bo_phan in dict_bo_phan:
        idx = dict_bo_phan[bo_phan]["id_bo_phan"]
        keys = dict_bo_phan[bo_phan]["list_key"]
        vitri = dict_bo_phan[bo_phan]["list_vi_tri"]

        for k in keys:
            if k:
                list_key.append([k, idx])
        list_vitri_all.append(vitri)

    list_key_sorted = sorted(list_key, key=lambda x: len(x[0]), reverse=True)

    with open("weight_map/weight_map_hang_muc_xe/list_key.txt", "w", encoding="utf-8") as f:
        for item in list_key_sorted:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open("weight_map/weight_map_hang_muc_xe/list_vitri_all.txt", "w", encoding="utf-8") as f:
        for item in list_vitri_all:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

process_dict_bo_phan(json_result)