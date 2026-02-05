import streamlit as st
import pandas as pd

# 1. إعدادات الصفحة واللغة
st.set_page_config(page_title="TailorAI Professional", layout="wide")

# قاموس الترجمة الاحترافي للمصطلحات التقنية
texts = {
    "ar": {
        "header": "منصة خياط الذكاء الاصطناعي العالمية",
        "sub": "تحويل التصاميم إلى باترونات دقيقة (بناءً على جداولك المعتمدة)",
        "sidebar": "إعدادات التحكم",
        "lang_label": "اختر اللغة / Language",
        "phase1": "📊 جداول القياسات",
        "phase2": "✂️ توليد الباترون",
        "phase3": "👗 معاينة 3D",
        "upload_btn": "ارفع صورة الموديل",
        "generate_btn": "استخراج الباترون الهندسي",
        "sizing_cat": "اختر الفئة المستهدفة",
        "size_label": "المقاس (Size)",
        "results": "المواصفات الفنية للقص"
    },
    "en": {
        "header": "AI Fashion Platform",
        "sub": "Image-to-Pattern Generation based on Global Sizing Charts",
        "sidebar": "Control Panel",
        "lang_label": "Select Language",
        "phase1": "📊 Sizing Charts",
        "phase2": "✂️ Pattern Generator",
        "phase3": "👗 3D Simulation",
        "upload_btn": "Upload Design Image",
        "generate_btn": "Generate CAD Pattern",
        "sizing_cat": "Select Category",
        "size_label": "Size",
        "results": "Technical Cutting Specs"
    }
}

# منطق تبديل اللغة
lang_choice = st.sidebar.selectbox("Language / اللغة", ["العربية", "English"])
ln = "ar" if lang_choice == "العربية" else "en"
t = texts[ln]

# تنسيق الواجهة (RTL للعربي)
if ln == "ar":
    st.markdown("""<style> div[direction="ltr"] { direction: rtl; text-align: right; } p, h1, h2, h3, label { text-align: right; direction: rtl; } </style>""", unsafe_allow_html=True)

# 2. جسم التطبيق
st.title(t["header"])
st.caption(t["sub"])

# تقسيم الشاشة لتبويبات (المراحل الأربعة من ملفك)
tab1, tab2, tab3 = st.tabs([t["phase1"], t["phase2"], t["phase3"]])

with tab1:
    st.subheader("تصفح جداول القياسات الرقمية")
    # محاكاة البيانات التي استخرجناها من صورك
    sample_data = {
        "Bust (الصدر)": [84, 88, 92, 96, 100],
        "Waist (الخصر)": [64, 68, 72, 76, 80],
        "Hip (الأرداف)": [90, 94, 98, 102, 106]
    }
    df = pd.DataFrame(sample_data, index=["T36", "T38", "T40", "T42", "T44"])
    st.table(df)

with tab2:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.selectbox(t["sizing_cat"], ["Women (فرنسي)", "Children (أطفال)", "Plus Size", "Unisex"])
        st.selectbox(t["size_label"], ["T36", "T40", "T44", "6Y", "10Y", "XL"])
        st.file_uploader(t["upload_btn"], type=["jpg", "png"])
        if st.button(t["generate_btn"]):
            with col2:
                st.info(t["results"])
                # رسم باترون SVG احترافي
                svg_code = '<svg width="200" height="300"><path d="M 50 10 L 150 10 L 140 250 L 60 250 Z" fill="none" stroke="black" stroke-width="2"/></svg>'
                st.components.v1.html(svg_code, height=350)

with tab3:
    st.warning("المعاينة ثلاثية الأبعاد قيد التحميل... (Phase 3)")
    st.image("https://via.placeholder.com/500x300.png?text=3D+Avatar+Simulation", caption="محاكاة الجسم بناءً على مقاسات الجدول")
