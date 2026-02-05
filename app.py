import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. إعدادات الصفحة والهوية البصرية
st.set_page_config(page_title="Rayane Tailor - Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    body, .main { font-family: 'Cairo', sans-serif; background-color: #fcfaf8; }
    .header-box {
        background-color: #4B0082;
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        border-bottom: 5px solid #FFD700;
        margin-bottom: 20px;
    }
    .stButton>button { background-color: #4B0082; color: white; border-radius: 20px; font-weight: bold; width: 100%; }
    .report-card { padding: 20px; border-radius: 15px; background-color: white; border: 2px solid #4B0082; }
    </style>
    """, unsafe_allow_html=True)

# 2. رأس الصفحة (الشعار)
st.markdown('<div class="header-box"><h1>🧵 Rayane Tailor</h1><p>إبداع، دقة، واحترافية</p></div>', unsafe_allow_html=True)

# 3. إعداد الاتصال بـ Google Sheets (للمرحلة القادمة)
# سنتركه الآن لكي لا يظهر خطأ حتى نضبط الـ Secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.info("💡 ملاحظة: نظام الحفظ الدائم قيد الإعداد.")

# 4. تقسيم التبويبات (Tabs)
tab1, tab2, tab3 = st.tabs(["📝 طلبية جديدة", "🗂️ سجل الزبائن", "📐 الباترون والطباعة"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        name = st.text_input("اسم الزبونة", placeholder="السيدة...")
        delivery = st.date_input("موعد التسليم")
        fabric = st.selectbox("نوع القماش", ["قطيفة", "حرير", "كتان", "ليقرا"])
        
    with col2:
        st.subheader("📍 المقاسات (cm)")
        bust = st.number_input("الصدر", value=100)
        waist = st.number_input("الوسط", value=80)
        hips = st.number_input("الأرداف", value=110)
        length = st.number_input("الطول", value=145)

    if st.button("💾 حفظ الطلبية"):
        st.balloons()
        st.success(f"تم تسجيل طلبية {name} بنجاح!")

with tab2:
    st.subheader("📂 سجل الزبائن المحفوظ")
    # هنا ستظهر البيانات من Google Sheets لاحقاً
    st.warning("سجل البيانات سيظهر هنا بعد ربط Google Sheets.")

with tab3:
    st.subheader("📐 الباترون التقني (A4 Grid)")
    # كود الباترون
    svg = f'''<svg width="200mm" height="300mm" viewBox="0 0 200 300" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="none" stroke="#eee" stroke-width="0.5"/>
        <path d="M 20,20 L 80,20 L 100,50 L {bust/4},100 L {waist/4},200 L {hips/4},280 L 20,280 Z" fill="none" stroke="#4B0082" stroke-width="2"/>
        <text x="30" y="250" font-size="10" fill="#4B0082">Rayane Tailor - Pattern</text>
    </svg>'''
    st.components.v1.html(svg, height=500)
    st.download_button("📥 تحميل الباترون للطباعة", svg, "pattern.svg")
