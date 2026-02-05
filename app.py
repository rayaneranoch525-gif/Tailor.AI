import streamlit as st
import pandas as pd
from datetime import datetime 

# 1. إعدادات الهوية البصرية (Rayane Tailor)
st.set_page_config(page_title="Rayane Tailor Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    body, .main { font-family: 'Cairo', sans-serif; background-color: #fcfaf8; direction: rtl; }
    .header-box {
        background-color: #4B0082;
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        border-bottom: 5px solid #FFD700;
        margin-bottom: 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #4B0082 !important; color: white !important; }
    .stDataFrame { border: 1px solid #4B0082; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-box"><h1>🧵 Rayane Tailor v2.1</h1><p>دقة الخصر الثلاثي والإدارة الاحترافية</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["✨ تسجيل طلبية", "📊 سجل الزبائن", "📐 الباترون والطباعة"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("اسم الزبونة", placeholder="مثال: السيدة مريم")
        delivery = st.date_input("موعد التسليم المتوقع")
        fabric_type = st.selectbox("نوع القماش", ["قطيفة", "ساتان", "جينز", "ليقرا", "كتان", "شيفون"])
        
        # منطق الإبر المعتمد على ملاحظاتك (12, 14, 16, 18)
        if fabric_type in ["ساتان", "ليقرا", "شيفون"]:
            needle = "12 (للأقمشة الرفيعة)"
        elif fabric_type in ["قطيفة", "كتان"]:
            needle = "14 (للأقمشة المتوسطة)"
        elif fabric_type == "جينز":
            needle = "16 أو 18 (للأقمشة الغليظة)"
        else:
            needle = "14"
            
        st.info(f"🧵 **نصيحة الماكنة:** استخدمي إبرة رقم **{needle}**")

    with col2:
        st.subheader("📍 المقاسات الاحترافية (cm)")
        bust = st.number_input("محيط الصدر", value=100)
        waist_1 = st.number_input("الخصر 1 (العلوي)", value=85)
        waist_2 = st.number_input("الخصر 2 (الحقيقي - البنسة)", value=80)
        waist_3 = st.number_input("الخصر 3 (الأرداف)", value=110)
        length = st.number_input("الطول الكلي", value=145)

with tab2:
    st.subheader("🗂️ قاعدة البيانات (مزامنة مع Google Sheets)")
    
    # ضعي رابط الـ CSV الذي استخرجتيه من جدولك هنا مكان النجوم
    # ملاحظة: تأكدي أن الرابط ينتهي بـ export=csv أو output=csv
    google_sheet_csv_url = "ضعي_رابط_الـCSV_هنا"
    
    if "ضعي_رابط" in google_sheet_csv_url:
        st.warning("⚠️ الخطوة المتبقية: يرجى لصق رابط الـ CSV من Google Sheets في الكود أعلاه.")
        st.info("الجدول يجب أن يحتوي على الأعمدة: (الاسم، الصدر، الخصر1، الخصر2، الخصر3، الطول، السعر)")
    else:
        try:
            df = pd.read_csv(google_sheet_csv_url)
            st.dataframe(df, use_container_width=True)
            st.success(f"✅ تم تحديث البيانات. عدد السجلات الحالية: {len(df)}")
        except Exception as e:
            st.error(f"خطأ في الاتصال: تأكدي من 'نشر الجدول على الويب' بصيغة CSV.")

with tab3:
    st.subheader("📐 الباترون الهندسي (نظام الخصر الثلاثي)")
    
    # حسابات الرسم (تقسيم على 4 مع إضافة 2 سم لحق الخياطة)
    b_draw = (bust / 4) + 2
    w1_draw = (waist_1 / 4) + 2
    w2_draw = (waist_2 / 4) + 2
    w3_draw = (waist_3 / 4) + 2
    l_draw = length / 5 # تصغير الطول للعرض فقط
    
    # رسم باترون يعكس الانحناءات الثلاثة للخصر
    svg = f'''<svg width="210mm" height="297mm" viewBox="0 0 210 297" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="none" stroke="#eee" stroke-width="0.5"/>
        <path d="M 40,20 L 100,20 L 115,35 
                 L {b_draw + 40},70 
                 L {w1_draw + 40},120 
                 L {w2_draw + 40},170 
                 L {w3_draw + 40},230 
                 L 40,280 Z" fill="none" stroke="#4B0082" stroke-width="2"/>
        <text x="45" y="270" font-family="Arial" font-size="7" fill="#4B0082">Rayane Tailor - Triple Waist System v2.1</text>
    </svg>'''
    
    st.components.v1.html(svg, height=450)
    st.download_button("📥 تحميل الباترون للطباعة (A4 Ready)", svg, "Rayane_Pro_Pattern.svg")
