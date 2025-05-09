import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from model import goi_y_cong_viec_tu_cv, goi_y_cong_viec_tu_khoa
from PyPDF2 import PdfReader
import docx

# --------------------
# Cấu hình Streamlit
# --------------------
st.set_page_config(page_title=" Hệ thống đề xuất công việc", layout="wide")

# --------------------
# Đọc nội dung từ file upload
# --------------------
def doc_noi_dung_file(file):
    if file.type == "application/pdf":
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.type == "text/plain":
        return str(file.read(), "utf-8")
    else:
        return ""

# --------------------
# Hàm cache gọi mô hình
# --------------------
@st.cache_data(show_spinner="⏳ Đang xử lý dữ liệu...")
def goi_y_cv_cached(text, so_luong):
    return goi_y_cong_viec_tu_cv(text, so_luong=so_luong)

@st.cache_data(show_spinner="⏳ Đang xử lý dữ liệu...")
def goi_y_tu_khoa_cached(keyword, so_luong):
    return goi_y_cong_viec_tu_khoa(keyword, so_luong=so_luong)

# --------------------
# Biểu đồ phân bố thành phố
# --------------------
def ve_bieu_do_thanh_pho(dataframe):
    if "Thành phố" in dataframe.columns:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.countplot(data=dataframe, y='Thành phố',
                      order=dataframe['Thành phố'].value_counts().index,
                      palette='viridis')
        plt.xlabel("Số lượng", color="#4a5568")
        plt.ylabel("Thành phố", color="#4a5568")
        plt.title("Phân bố công việc theo thành phố", color="#2c3e50")
        plt.tick_params(axis='both', colors='#718096')
        st.pyplot(fig)
    else:
        st.warning("⚠️ Không có thông tin về thành phố trong dữ liệu.")

# --------------------
# Giao diện điều hướng
# --------------------
if "trang" not in st.session_state:
    st.session_state.trang = "Trang chủ"

if st.session_state.trang == "Trang chủ":
    st.title("✨🧠 SMARTJOB: ĐỀ XUẤT VIỆC LÀM DỰA TRÊN PHÂN TÍCH HỒ SƠ & TỪ KHÓA ✨")
    
    # Nội dung giới thiệu hệ thống
    st.markdown("""
    <div style='font-size:16px; line-height:1.8; color:#2c3e50; background-color:#f7fafc; padding:15px; border-left:5px solid #3182ce; border-radius:8px; margin-bottom:20px;'>
        <strong>🔍 Nền tảng tư vấn nghề nghiệp tiên tiến</strong> được phát triển nhằm tối ưu hóa quá trình tìm kiếm việc làm cho người dùng – đặc biệt là đối tượng <strong>lao động mới</strong> và <strong>sinh viên tốt nghiệp</strong>.
        <br><br>
        Hệ thống đóng vai trò <strong>cầu nối hiệu quả</strong> giữa ứng viên và cơ hội nghề nghiệp phù hợp với <strong>năng lực</strong>, <strong>chuyên môn</strong> và <strong>định hướng phát triển cá nhân</strong>.
        <br><br>
        ✅ Thông qua <strong>trí tuệ nhân tạo</strong>, hệ thống phân tích chuyên sâu <strong>hồ sơ ứng viên</strong> hoặc <strong>từ khóa ngành nghề</strong> được cung cấp, từ đó đề xuất những vị trí việc làm có độ tương thích cao – đáp ứng chính xác nhu cầu thực tế.
        <br><br>
        🚀 <strong>Tính ứng dụng vượt trội</strong>: Nền tảng dễ dàng tích hợp vào các <strong>cổng tuyển dụng</strong>, <strong>hệ thống quản trị đại học</strong> hoặc <strong>trung tâm tư vấn hướng nghiệp</strong>.
        <br><br>
        🎯 <strong>Sứ mệnh cốt lõi:</strong> Nâng cao hiệu quả tìm kiếm việc làm, rút ngắn thời gian ứng tuyển, đồng thời tạo <strong>kênh kết nối chiến lược</strong> giữa nhà tuyển dụng và <strong>nguồn nhân lực tiềm năng</strong> – góp phần <strong>tối ưu hóa thị trường lao động</strong>.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🚀 Vui lòng chọn phương thức đề xuất")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Đề xuất theo CV / Kỹ năng"):
            st.session_state.trang = "Theo CV"
    with col2:
        if st.button("🔍 Đề xuất theo từ khóa"):
            st.session_state.trang = "Theo từ khóa"

# --------------------
# Trang đề xuất theo CV
# --------------------
elif st.session_state.trang == "Theo CV":
    st.title("📄 Đề xuất việc làm từ CV hoặc kỹ năng")

    so_luong_goi_y = st.slider("🔢 Số lượng công việc đề xuất:", 1, 100, 5)

    cv_text = st.text_area("📝 Nhập nội dung CV hoặc kỹ năng:")
    file_cv = st.file_uploader("📁 Hoặc tải lên file CV (.pdf, .docx, .txt):", type=["pdf", "docx", "txt"])

    if st.button("🚀 Đề xuất công việc từ CV hoặc kỹ năng"):
        if file_cv is not None:
            noi_dung = doc_noi_dung_file(file_cv)
        else:
            noi_dung = cv_text.strip()

        if noi_dung == "":
            st.warning("⚠️ Vui lòng nhập nội dung CV hoặc tải lên file.")
        else:
            with st.spinner("🔍 Đang phân tích..."):
                ket_qua = goi_y_cv_cached(noi_dung, so_luong_goi_y)
            if not ket_qua.empty:
                st.success(f"✅ Tìm thấy {len(ket_qua)} công việc phù hợp:")
                st.dataframe(ket_qua, use_container_width=True)
                st.subheader("📊 Phân bố công việc phù hợp theo địa điểm làm việc")
                ve_bieu_do_thanh_pho(ket_qua)
            else:
                st.info("😥 Không tìm thấy công việc phù hợp. Vui lòng thử nội dung khác.")

    if st.button("⬅️ Quay lại trang chủ"):
        st.session_state.trang = "Trang chủ"

# --------------------
# Trang đề xuất theo từ khóa
# --------------------
elif st.session_state.trang == "Theo từ khóa":
    st.title("🔑 Đề xuất việc làm theo từ khóa ngành nghề")

    so_luong_goi_y = st.slider("🔢 Số lượng công việc đề xuất:", 1, 100, 5)
    tu_khoa = st.text_input("🧩 Nhập từ khóa ngành nghề (VD: 'Data Analyst', 'Marketing'):")

    if st.button("✨ Đề xuất công việc theo từ khóa"):
        if tu_khoa.strip() == "":
            st.warning("⚠️ Vui lòng nhập từ khóa.")
        else:
            with st.spinner("🔍 Đang tìm kiếm..."):
                ket_qua = goi_y_tu_khoa_cached(tu_khoa, so_luong_goi_y)
            if not ket_qua.empty:
                st.success(f"✅ Tìm thấy {len(ket_qua)} công việc phù hợp:")
                st.dataframe(ket_qua, use_container_width=True)
                st.subheader("📊 Phân bố công việc theo địa điểm")
                ve_bieu_do_thanh_pho(ket_qua)
            else:
                st.info("😥 Không tìm thấy công việc với từ khóa này.")

    if st.button("⬅️ Quay lại trang chủ"):
        st.session_state.trang = "Trang chủ"
