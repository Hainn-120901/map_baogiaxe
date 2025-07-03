from map_general.map_hang_muc_xe.utils import *
import json
from config import *
import os
from text_unidecode import unidecode as uni1


class MapHangMucXe(object):
    def __init__(self):
        with open(os.path.join(folder_weight, "weight_map/weight_map_hang_muc_xe/list_key.txt"), "r", encoding="utf-8") as file_list_key:
            self.list_key = [json.loads(line.strip()) for line in file_list_key]
            self.list_key_uni1 = [[uni1(i[0]), i[1]] for i in self.list_key]

        with open(os.path.join(folder_weight, "weight_map/weight_map_hang_muc_xe/list_vitri_all.txt"), "r", encoding="utf-8") as file_list_vi_tri:
            self.list_vi_tri = [json.loads(line.strip()) for line in file_list_vi_tri]

        self.he_so_editdistance = 1
        self.he_so_chieu_dai_chuoi = -1
        self.he_so_bat_dau = 0.2

    @staticmethod
    def get_cluster_text_with_len(line_encode_arr, line_arr):
        max_len_split_text = len(line_encode_arr)
        list_text_all, list_text_real_all = [], []
        for len_ms in range(max_len_split_text):
            list_text, list_text_real = [], []
            for index in range(max_len_split_text - len_ms):
                list_text.append(" ".join(line_encode_arr[index:index + len_ms + 1]))
                list_text_real.append(" ".join(line_arr[index:index + len_ms + 1]))
            list_text_all.append(list_text)
            list_text_real_all.append(list_text_real)
        return list_text_all, list_text_real_all

    def find_list_key_rs(self, text_ocr, list_key_search, list_key_uni_search, list_text_all, list_text_real_all):

        list_key_idx_pass_cover, list_idx_s_e_pass, list_key_idx_pass = [], [], []
        for key_idx, key_uni_idx in zip(list_key_search, list_key_uni_search):
            line_check_, idx_end_, _, idx_start_, score_, key__ = check_text_editdistance_all_large(text_ocr, key_idx[0], key_uni_idx[0], list_text_all,
                                              list_text_real_all)
            if score_ > 2:
                continue
            if get_score(key__, score_):
                score_tong = self.he_so_editdistance * score_ + self.he_so_chieu_dai_chuoi * (len(key__) - score_) / len(text_ocr) + self.he_so_bat_dau * idx_start_ / len(text_ocr)
                dict_idx = {
                    "text_key": key_idx[0],
                    "index_key": key_idx[1],
                    "score_min": score_tong,
                    "index_start": idx_start_,
                    "index_end": idx_end_
                }
                if check_duplicate([idx_start_, idx_end_], list_idx_s_e_pass):
                    list_key_idx_pass_cover.append(dict_idx)
                    list_idx_s_e_pass.append({"index_start": idx_start_, "index_end": idx_end_})
                else:
                    list_key_idx_pass.append(dict_idx)

        list_exchange = []
        for idx_key_idx_pass_v1, key_idx_pass_v1 in enumerate(list_key_idx_pass_cover):
            score_min = 999
            idx_start_pass_v1 = key_idx_pass_v1["index_start"]
            idx_end_pass_v1 = key_idx_pass_v1["index_end"]
            score_min_pass_v1 = key_idx_pass_v1["score_min"]
            for idx_key_idx_pass_v2, key_idx_pass_v2 in enumerate(list_key_idx_pass):
                idx_start_pass_v2 = key_idx_pass_v2["index_start"]
                idx_end_pass_v2 = key_idx_pass_v2["index_end"]
                score_min_pass_v2 = key_idx_pass_v2["score_min"]

                check_se = idx_start_pass_v2 == idx_start_pass_v1 and idx_end_pass_v2 == idx_end_pass_v1
                check_score_min = score_min_pass_v1 > score_min_pass_v2 and score_min_pass_v2 < score_min

                if check_se and check_score_min:
                    score_min = score_min_pass_v2
                    list_exchange.append([idx_key_idx_pass_v1, idx_key_idx_pass_v2])

        for exchange in list_exchange:
            cache = list_key_idx_pass_cover[exchange[0]]
            list_key_idx_pass_cover[exchange[0]] = list_key_idx_pass[exchange[1]]
            list_key_idx_pass[exchange[1]] = cache
        list_key_idx_pass_cover = remove_duplicate_idx_key(list_key_idx_pass_cover)
        list_key_idx_pass = remove_duplicate_idx_key(list_key_idx_pass)

        list_key_idx_pass_cover = sorted(list_key_idx_pass_cover,
                                      key=lambda x: (x['score_min'], -len(x['text_key']), x['index_start']))
        list_key_idx_pass = sorted(list_key_idx_pass,
                                      key=lambda x: (x['score_min'], -len(x['text_key']), x['index_start']))

        return list_key_idx_pass_cover, list_key_idx_pass

    def find_hang_muc(self, text_ocr, list_pass_cover, list_pass, list_vi_tri, list_text_all, list_text_real_all):
        list_hang_muc = []
        list_hang_muc_phu = []
        list_score = []

        for list_key in [list_pass_cover, list_pass]:
            for item in list_key:
                for dict_vi_tri in list_vi_tri[item['index_key']]:
                    key_check = ' '.join([item['text_key'], dict_vi_tri['key_vi_tri']]).strip()
                    _, idx_end_, _, idx_start_, score_, key__ = check_text_editdistance_all_large(text_ocr, key_check, uni1(key_check), list_text_all, list_text_real_all)

                    if get_score(key__, score_) and dict_vi_tri['key_vi_tri'] != '':
                        score_tong = self.he_so_editdistance * score_ + self.he_so_chieu_dai_chuoi * (len(key__) - score_) / len(text_ocr) + self.he_so_bat_dau * idx_start_ / len(text_ocr)
                        list_hang_muc.append([dict_vi_tri['ma_hmuc'], dict_vi_tri['ten_hmuc'], score_tong])
                        list_score.append(score_tong)
                    else:
                        score_tong = self.he_so_editdistance * score_ + self.he_so_chieu_dai_chuoi * (len(key__) - score_) / len(text_ocr)
                        list_hang_muc_phu.append([dict_vi_tri['ma_hmuc'], dict_vi_tri['ten_hmuc'], score_tong])
                        list_score.append(score_tong)

            if list_hang_muc:
                sorted_lst = sorted(list_hang_muc, key=lambda x: (x[2]))
                ma_hang_muc, ten_hang_muc = sorted_lst[0][0], sorted_lst[0][1]
                return ma_hang_muc, ten_hang_muc

            for idx, item in enumerate(list_key):
                for dict_vi_tri in list_vi_tri[item['index_key']]:
                    text_ocr_vi_tri = text_ocr[item['index_end']:].strip()
                    key_vi_tri = dict_vi_tri['key_vi_tri']
                    if len(text_ocr_vi_tri) < 4 or len(key_vi_tri) - len(text_ocr_vi_tri) > 2 or len(key_vi_tri) < 2:
                        continue

                    line_arr_vi_tri = text_ocr_vi_tri.split(" ")
                    thresh_vi_tri = len(' '.join(line_arr_vi_tri[0:2])) + 2
                    line_encode_arr_vi_tri = uni1(text_ocr_vi_tri).split(" ")
                    list_text_all_vi_tri, list_text_real_all_vi_tri = self.get_cluster_text_with_len(line_encode_arr_vi_tri, line_arr_vi_tri)

                    _, idx_end_, _, idx_start_, score_, key__ = check_text_editdistance_all_large(text_ocr_vi_tri, key_vi_tri, uni1(key_vi_tri), list_text_all_vi_tri, list_text_real_all_vi_tri)

                    score_tong = list_score[idx] + self.he_so_editdistance * score_ + self.he_so_chieu_dai_chuoi * (len(key__) - score_) / len(text_ocr_vi_tri)
                    if idx_start_ is not None:
                        index_start_vi_tri = idx_start_ + len(text_ocr[:item['index_end']]) - 1
                        if get_score(key__, score_) and index_start_vi_tri - item['index_end'] + 1 < thresh_vi_tri:
                            list_hang_muc.append([dict_vi_tri['ma_hmuc'], dict_vi_tri['ten_hmuc'], score_tong])

            if list_hang_muc:
                sorted_lst = sorted(list_hang_muc, key=lambda x: (x[2]))
                ma_hang_muc, ten_hang_muc = sorted_lst[0][0], sorted_lst[0][1]
                return ma_hang_muc, ten_hang_muc
        if list_hang_muc_phu:
            sorted_lst = sorted(list_hang_muc_phu, key=lambda x: (x[2]))
            ma_hang_muc, ten_hang_muc = sorted_lst[0][0], sorted_lst[0][1]
            return ma_hang_muc, ten_hang_muc
        return None, None

    @staticmethod
    def swap_key(list_pass_cover, list_pass, text_ocr):
        list_exchange = []

        for idx_key_idx_pass_cover, key_idx_pass_cover in enumerate(list_pass_cover):
            idx_start_pass_cover = key_idx_pass_cover["index_start"]
            idx_end_pass_cover = key_idx_pass_cover["index_end"]
            score_min_pass_cover = key_idx_pass_cover["score_min"]
            text_split = text_ocr[idx_start_pass_cover:idx_end_pass_cover].split(" ")
            list_text_cover_split = [" ".join(text_split[:-1]), " ".join(text_split[1:-1]), " ".join(text_split[1:])]

            for idx_key_idx_pass, key_idx_pass in enumerate(list_pass):
                idx_start_pass = key_idx_pass["index_start"]
                idx_end_pass = key_idx_pass["index_end"]
                score_min_pass = key_idx_pass["score_min"]
                text_pass = text_ocr[idx_start_pass:idx_end_pass]

                if idx_start_pass_cover <= idx_start_pass and idx_end_pass_cover >= idx_end_pass and score_min_pass_cover > score_min_pass and text_pass in list_text_cover_split:
                    list_exchange.append([idx_key_idx_pass_cover, idx_key_idx_pass])

        for exchange in list_exchange:
            cache = list_pass_cover[exchange[0]]
            list_pass_cover[exchange[0]] = list_pass[exchange[1]]
            list_pass[exchange[1]] = cache

        list_key_idx_pass_cover = remove_duplicate_idx_key(list_pass_cover)
        list_key_idx_pass = remove_duplicate_idx_key(list_pass)

        list_key_idx_pass_cover = sorted(list_key_idx_pass_cover, key=lambda x: (x['score_min'], -len(x['text_key']), x['index_start']))
        list_key_idx_pass = sorted(list_key_idx_pass, key=lambda x: (x['score_min'], -len(x['text_key']), x['index_start']))

        return list_key_idx_pass_cover, list_key_idx_pass

    def map_hang_muc_xe(self, text_ocr):
        result_final = {
            "description_map": "",
            "description_code": ""
        }
        if text_ocr is None or len(text_ocr) <= 2:
            return result_final

        text_ocr = smooth_txt(text_ocr).lower().strip()
        list_key_new_, list_key_uni_new_ = [], []
        for key, key_uni in zip(self.list_key, self.list_key_uni1) :
            if len(key[0]) - len(text_ocr) < 3:
                list_key_new_.append(key)
                list_key_uni_new_.append(key_uni)

        line_arr = text_ocr.split(" ")
        line_encode_arr = uni1(text_ocr).split(" ")
        list_text_all, list_text_real_all = self.get_cluster_text_with_len(line_encode_arr, line_arr)
        list_pass_cover_, list_pass_ = self.find_list_key_rs(text_ocr, list_key_new_, list_key_uni_new_, list_text_all, list_text_real_all)
        list_pass_cover, list_pass = self.swap_key(list_pass_cover_, list_pass_, text_ocr)

        ma_hang_muc, ten_hang_muc = self.find_hang_muc(text_ocr, list_pass_cover, list_pass, self.list_vi_tri, list_text_all, list_text_real_all)

        if ma_hang_muc:
            result_final = {
                "description_map": ten_hang_muc,
                "description_code": ma_hang_muc
            }
        return result_final

