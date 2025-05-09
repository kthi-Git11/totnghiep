import pandas as pd
import numpy as np
import difflib
import string
import joblib 
from underthesea import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ============================
# 1. Tiền xử lý và tải dữ liệu
# ============================
df = pd.read_excel("/Users/thinguyen/Downloads/app/data_processed.xlsx")
stopwords = open("/Users/thinguyen/Downloads/app/vietnamese-stopwords.txt", encoding="utf-8").read().splitlines()

# Gộp nội dung mô tả công việc, yêu cầu, kỹ năng thành một cột duy nhất
def tien_xu_ly(df):
    df = df.copy()
    df["Noi_dung_cv"] = df["Ten_cong_viec"].fillna("") + ", " + df["Mo_ta_cv"] + ", " + df["Ki_nang_can_co"]
    return df

df = tien_xu_ly(df)

# Hàm xử lý văn bản tiếng Việt
def chuan_hoa(text):
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = word_tokenize(text, format="text")
    tokens = [tu for tu in tokens.split() if tu not in stopwords and len(tu) > 1]
    return " ".join(tokens)

# Áp dụng xử lý cho toàn bộ nội dung
df["Noi_dung_cv"] = df["Noi_dung_cv"].apply(chuan_hoa)

# Vector hóa nội dung công việc
vectorizer = TfidfVectorizer()
vector_tfidf = vectorizer.fit_transform(df["Noi_dung_cv"])
cosine_sim = cosine_similarity(vector_tfidf, vector_tfidf)

# ============================
# 2. Gợi ý từ CV (hoặc kỹ năng)
# ============================
def goi_y_cong_viec_tu_cv(cv_text, so_luong=10):
    text = chuan_hoa(cv_text)
    vec_cv = vectorizer.transform([text])
    diem = cosine_similarity(vec_cv, vector_tfidf)
    diem = list(enumerate(diem[0]))
    diem = sorted(diem, key=lambda x: x[1], reverse=True)
    chi_so_goi_y = [i[0] for i in diem[:so_luong]]
    ket_qua = df.loc[chi_so_goi_y, ['Ten_cong_viec', 'Ten_cty', 'Thanh_pho', 'Quan/Huyen','Mo_ta_cv', 'Ki_nang_can_co']].reset_index(drop=True)
 # Đổi tên cột sang tiếng Việt
    ket_qua = ket_qua.rename(columns={
        'Ten_cong_viec': 'Tên công việc',
        'Ten_cty': 'Tên công ty',
        'Thanh_pho': 'Thành phố',
        'Quan/Huyen': 'Quận/Huyện',
        'Mo_ta_cv': 'Mô tả công việc',
        'Ki_nang_can_co': 'Kỹ năng cần có'
    })

    return ket_qua
    return ket_qua

# ============================
# 3. Gợi ý từ khóa
# ============================
def goi_y_cong_viec_tu_khoa(tu_khoa, so_luong=10):
    ket_qua_khop = df[df['Ten_cong_viec'].str.contains(tu_khoa, case=False, na=False)]
    danh_sach_khop = list(ket_qua_khop['Ten_cong_viec'])

    tieu_de = df['Ten_cong_viec'].tolist()
    tieu_de_gan_dung = difflib.get_close_matches(tu_khoa, tieu_de)

    danh_sach_ket_hop = list(set(danh_sach_khop + tieu_de_gan_dung))
    if not danh_sach_ket_hop:
        return pd.DataFrame(columns=['Ten_cong_viec', 'Ten_cty', 'Thanh_pho','Quan/Huyen','Mo_ta_cv', 'Ki_nang_can_co'])

    cong_viec_dau = danh_sach_ket_hop[0]
    chi_so_cong_viec = df[df['Ten_cong_viec'] == cong_viec_dau].index[0]
    diem_tuong_dong = list(enumerate(cosine_sim[chi_so_cong_viec]))
    diem_tuong_dong = sorted(diem_tuong_dong, key=lambda x: x[1], reverse=True)

    chi_so_goi_y = [i[0] for i in diem_tuong_dong[:so_luong]]
    ket_qua = df.loc[chi_so_goi_y, ['Ten_cong_viec', 'Ten_cty', 'Thanh_pho','Quan/Huyen','Mo_ta_cv', 'Ki_nang_can_co']].reset_index(drop=True)

        
    # Đổi tên cột sang tiếng Việt
    ket_qua = ket_qua.rename(columns={
        'Ten_cong_viec': 'Tên công việc',
        'Ten_cty': 'Tên công ty',
        'Thanh_pho': 'Thành phố',
        'Quan/Huyen': 'Quận/Huyện',
        'Mo_ta_cv': 'Mô tả công việc',
        'Ki_nang_can_co': 'Kĩ năng cần có'
    }) 

    return ket_qua
    