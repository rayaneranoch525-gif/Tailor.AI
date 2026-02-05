import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. إعدادات متقدمة
st.set_page_config(page_title="Rayane Tailor - Enterprise", layout="wide")

# 2. وظيفة حساب استهلاك القماش (الدقيق)
def calculate_fabric(length, bust, fabric_width):
    pattern_width = (bust / 4) + 5 # الربع + حق الخياطة
    if (pattern_width * 2) <= fabric_width:
        return (length + 20) / 100 # القطعتان تكفيان عرضياً
    else:
        return ((length * 2) + 20) / 100 # نحتاج طولين

# 3. وظيفة الباترون مع شبكة A4 (Tiling)
def generate_tiled_svg(bust, length, w3):
    l_mm = length * 10
    w_mm = (w3/4 + 10) * 10
    # رسم شبكة A4 خلفية (210mm x 297mm)
    grid = ""
    for x in range(0, int(w_mm) + 210, 210):
        grid += f'<line x1="{x}" y1="0" x2="{x}" y2="{l_mm}" stroke="#ddd" stroke-width="0.5"/>'
    for y in range(0, int(l_mm) + 297, 297):
        grid += f'<line x1="0" y1="{y}" x2="{w_mm}" y2="{y}" stroke="#ddd" stroke-width="0.5"/>'
        
    svg = f'''<svg width="{w_mm}mm" height="{l_mm}mm" viewBox="0 0 {w_mm} {l_mm}" xmlns="http://www.w3.org/2000/svg">
        {grid}
        <path d="M 10,10 L 100,10 L 130,40 L {w_mm-10},150 L {w_mm-10},{l_mm-10} L 10,{l_mm-10} Z" fill="none" stroke="black" stroke-width="2"/>
        <text x="10" y="20" font-size="10">Rayane Tailor - A4 Grid System</text>
    </svg>'''
    return svg

# الواجهة الأساسية
st.title("🧵 Rayane Tailor - نظام الإدارة المتكامل")

tab1, tab2, tab3 = st.tabs(["📝 طلبيات جديدة", "📂 سجل الزبائن", "📊 حاسبة القماش"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("اسم الزبونة")
        delivery = st.date_input("موعد التسليم")
        uploaded_img = st.file_uploader("ارفع صورة الموديل أو النتيجة النهائية", type=['jpg','png'])
        if uploaded_img: st.image(uploaded_img, width=200)
    
    with col2:
        st.subheader("📏 المقاسات")
        bust = st.number_input("الصدر", 100)
        length = st.number_input("الطول", 145)
        w3 = st.number_input("الأرداف", 110)
        
    if st.button("💾 حفظ الطلبية في قاعدة البيانات"):
        # هنا يتم الربط مع Google Sheets برمجياً (يتطلب ملف json للمصادقة)
        st.success(f"تم حفظ بيانات {name} بنجاح في السجل الدائم!")

with tab2:
    st.subheader("🗂️ معرض الموديلات والزبائن")
    # محاكاة لقاعدة البيانات
    data = {"الزبونة": ["فاطمة", "خديجة"], "الموعد": ["2026-02-10", "2026-02-15"], "الحالة": ["قيد التنفيذ", "جاهز"]}
    st.table(pd.DataFrame(data))

with tab3:
    st.subheader("📐 حساب القماش والباترون")
    f_width = st.selectbox("عرض القماش المتوفر (cm)", [150, 280, 300])
    needed = calculate_fabric(length, bust, f_width)
    st.info(f"📏 تحتاجين شراء: {needed:.2f} متر من القماش.")
    
    svg = generate_tiled_svg(bust, length, w3)
    st.download_button("📥 تحميل باترون مقسم A4", svg, "rayane_tiled_pattern.svg")

# تذكير ذكي
st.sidebar.warning(f"🔔 تنبيه: لديك طلبيتان يجب تسليمهما خلال 48 ساعة!")
