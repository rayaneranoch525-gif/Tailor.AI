import streamlit as st
import pandas as pd
from datetime import datetime, date
import re

# 1. إعدادات الهوية البصرية
st.set_page_config(page_title="Rayane Tailor Elite v3.6", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    body, .main { font-family: 'Cairo', sans-serif; background-color: #fcfaf8; direction: rtl; }
    .header-box {
        background-color: #4B0082; padding: 25px; border-radius: 15px;
        color: white; text-align: center; border-bottom: 5px solid #FFD700; margin-bottom: 20px;
    }
    .add-button {
        background-color: #FFD700; color: #4B0082 !important; padding: 12px;
        text-align: center; border-radius: 10px; font-weight: bold;
        text-decoration: none; display: block; margin-bottom: 20px; border: 2px solid #4B0082;
    }
    .stExpander { border: 1px solid #4B0082; border-radius: 10px; background: white; }
    </style>
    """, unsafe_allow_html=True)

# دالة ذكية لتحويل روابط جوجل درايف لتظهر كصور
def fix_google_drive_link(url):
    if pd.isna(url): return None
    url = str(url)
    if 'drive.google.com' in url:
        # استخراج الـ ID الخاص بالصورة
        match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
        if not match:
            match = re.search(r'file/d/([a-zA-Z0-9_-]+)', url)
        if match:
            return f'https://drive.google.com/uc?id={match.group(1)}'
    return url

st.markdown('<div class="header-box"><h1>🧵 Rayane Tailor Elite</h1><p>نظام ذكي يدعم تحميل الصور والروابط</p></div>', unsafe_allow_html=True)

# املئي رابط الـ Form الخاص بك هنا
google_form_url = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform" 

st.markdown(f'<a href="{google_form_url}" target="_blank" class="add-button">➕ إضافة زبونة أو رفع صورة من الهاتف (Google Form)</a>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 سجل الزبائن الذكي", "📐 حاسبة الأمتار والباترون"])

with tab1:
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSRmUvTS_TWoFVJ3cesd8UfvW4WPe4Y0hyoEm8uzIv_b2ct38H48gWVWTXSWXBAT4dk8r2JDJk023_h/pub?output=csv"
    
    try:
        df = pd.read_csv(csv_url)
        df.columns = [col.strip() for col in df.columns]

        for index, row in df.iterrows():
            cust_name = row.iloc[1] if len(row) > 1 else "زبونة"
            
            with st.expander(f"👤 {cust_name}"):
                c1, c2 = st.columns([1, 2])
                
                with c1:
                    # البحث عن خانة الصورة (سواء كانت رابط أو ملف مرفوع)
                    img_link = ""
                    for col in df.columns:
                        if any(x in col for x in ["صورة", "Image", "File", "رابط"]):
                            img_link = fix_google_drive_link(row[col])
                    
                    if img_link and str(img_link).startswith('http'):
                        st.image(img_link, caption="الموديل", use_container_width=True)
                    else:
                        st.info("📷 لا توجد صورة مرفقة")

                with c2:
                    st.write("**📝 التفاصيل والمقاسات:**")
                    # عرض البيانات بشكل أنيق
                    cols_to_show = df.columns[1:]
                    for col in cols_to_show:
                        if not str(row[col]).startswith('http'): # إخفاء الروابط الطويلة من النص
                            st.write(f"**{col}:** {row[col]}")
    except:
        st.error("بانتظار الإدخال الأول من النموذج...")

with tab2:
    st.subheader("📐 حسابات ورشة إيليت")
    length = st.number_input("طول الموديل (cm)", 140)
    needed = (length + 20) / 100
    st.metric("كمية القماش المطلوبة (متر)", f"{needed:.2f}")
    
    st.divider()
    st.write("💡 **نصيحة تقنية:** عند رفع صورة من الهاتف عبر Google Form، تأكدي من ضبط إعدادات المجلد في Google Drive ليكون 'أي شخص لديه الرابط يمكنه العرض' لكي تظهر الصورة هنا.")
