from polyleven import levenshtein
from text_unidecode import unidecode as uni1
import re

def check_duplicate(idx_s_e_check, list_idx_s_e_pass):
    for item in list_idx_s_e_pass:
        idx_start = item["index_start"]
        idx_end = item["index_end"]
        if idx_s_e_check[0] >= idx_start and idx_s_e_check[1] <= idx_end:
            return False
    return True

def remove_duplicate_idx_key(list_key_idx_pass):
    dict_idx_key = {}
    for item in list_key_idx_pass:
        index_key = item["index_key"]
        if index_key not in dict_idx_key:
            dict_idx_key[index_key] = item
        else:
            if item["score_min"] < dict_idx_key[index_key]["score_min"]:
                dict_idx_key[index_key] = item
    return list(dict_idx_key.values())


def get_score(key_, score):
    if len(key_) > 20:
        thresh = 2
    elif len(key_) > 9:
        thresh = 1
    elif len(key_) > 5:
        thresh = 0.5
    else:
        thresh = 0
    if score <= thresh:
        return True
    else:
        return False

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

def check_text_all(text_ocr_real, key_check):
    text_ocr_real = text_ocr_real.lower()
    key_check = key_check.lower()
    line_, end_, return_, start_, score_, type_ = check_text_editdistance_v1(text_ocr_real, key_check)
    if line_ is None:
        line_, end_, return_, start_, score_, type_ = check_text_in_line_v1(text_ocr_real, key_check)

    return line_, end_, return_, start_, score_, type_

def check_text_editdistance_v1(text_ocr_real, key_check):
    text_ocr_real = text_ocr_real.lower()
    key_check = key_check.lower()

    line_arr = text_ocr_real.split(" ")
    line_encode_arr = uni1(text_ocr_real).split(" ")

    line_check, index_end, index_return, index_start, type_data, score_min = None, None, None, None, "", float('inf')

    len_key_check_split = len(key_check.split(" "))
    if len_key_check_split == 0 or len_key_check_split > len(line_encode_arr):
        return line_check, index_end, index_return, index_start, score_min, type_data

    key_check_unidecode = uni1(key_check)

    for index in range(len(line_encode_arr) - len_key_check_split + 1):
        text = " ".join(line_encode_arr[index:index + len_key_check_split])
        text_real = " ".join(line_arr[index:index + len_key_check_split])

        distance_matching2 = levenshtein(key_check, text_real, 2)
        if distance_matching2 == 0:
            distance_matching1 = 0
        else:
            distance_matching1 = levenshtein(key_check_unidecode, text, 2)

        distance_matching = distance_matching1
        if distance_matching1 == 0 and distance_matching2 != 0:
            distance_matching += 0.5

        if distance_matching < score_min:
            score_min = distance_matching
            type_data = key_check
            line_check = text_ocr_real.lower()
            text_ok = text_real
            index_start = line_check.index(text_ok)
            index_end = index_start + len(text_ok)

        elif distance_matching == score_min and len(key_check) > len(type_data):
            type_data = key_check
            line_check = text_ocr_real.lower()
            text_ok = text_real
            index_start = line_check.index(text_ok)
            index_end = index_start + len(text_ok)

        if distance_matching == 0:
            break

    return line_check, index_end, index_return, index_start, score_min, type_data

# lấy cả những trường hợp score > 2
def check_text_editdistance_all_large(text_ocr_real, key_check, key_check_unidecode, list_text_all, list_text_real_all):
    line_check, index_end, index_return, index_start, type_data, score_min = None, None, None, None, "", 999999
    len_key_check = len(key_check)
    len_key_check_split = len(key_check.split(" "))
    if len_key_check > 20:
        thresh = 2
    elif len_key_check > 9:
        thresh = 1
    else:
        thresh = 0
    if len_key_check_split == 0 or len_key_check_split > len(list_text_all):
        return line_check, index_end, index_return, index_start, score_min, type_data
    # lay ra nhung key trong list text all co len = len cua len_key_check_split
    list_text_split_check, list_text_real_split_check = list_text_all[len_key_check_split - 1], list_text_real_all[len_key_check_split - 1]

    for text, text_real in zip(list_text_split_check, list_text_real_split_check):
        if abs(len(text) - len_key_check) > thresh:
            continue
        distance_matching2 = levenshtein(key_check, text_real, thresh)
        if distance_matching2 == 0:
            distance_matching1 = 0
        else:
            distance_matching1 = levenshtein(key_check_unidecode, text, thresh)
        distance_matching = distance_matching1
        if distance_matching1 == 0 and distance_matching2 != 0:
            distance_matching = distance_matching1 + 0.5
        if distance_matching < score_min:
            type_data = key_check
            score_min = distance_matching
            line_check = text_ocr_real
            text_ok = text_real
            index_start = line_check.index(text_ok)
            index_end = index_start + len(text_ok)
        elif distance_matching == score_min and len(key_check) > len(type_data):
            type_data = key_check
            score_min = distance_matching
            line_check = text_ocr_real
            text_ok = text_real
            index_start = line_check.index(text_ok)
            index_end = index_start + len(text_ok)
        if score_min == 0:
            break
    return line_check, index_end, index_return, index_start, score_min, type_data

def check_text_in_line_v1(text_ocr_real, key_check):
    text_ocr_real = text_ocr_real.lower()
    key_check = key_check.lower()

    if key_check in text_ocr_real:
        index_start = text_ocr_real.index(key_check)
        index_end = index_start + len(key_check)
        index_return = 0
        score_min = 0
        type_data = key_check
        return text_ocr_real, index_end, index_return, index_start, score_min, type_data

    text_ocr_real_decode = uni1(text_ocr_real)
    key_check_decode = uni1(key_check)

    if key_check_decode in text_ocr_real_decode:
        list_word_decode = text_ocr_real_decode.split()
        len_key_check_decode = len(key_check_decode.split())

        if len_key_check_decode > len(list_word_decode):
            return None, None, None, None, 9999, ""

        for index_i in range(len(list_word_decode) - len_key_check_decode + 1):
            candidate_word = ' '.join(list_word_decode[index_i:index_i + len_key_check_decode])
            if key_check_decode in candidate_word:
                if len(candidate_word) - len(key_check_decode) <= 3:
                    index_start = text_ocr_real_decode.index(key_check_decode)
                    index_end = index_start + len(key_check_decode)
                    index_return = 0
                    score_min = 0.5
                    type_data = key_check
                    return text_ocr_real, index_end, index_return, index_start, score_min, type_data

    return None, None, None, None, 9999, ""
