import streamlit as st
import pandas as pd
import qrcode
import urllib.parse
from io import BytesIO
import base64
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعدادات الصفحة والواجهة الملكية
st.set_page_config(page_title="Rayane Tailor Elite Ultimate", layout="wide", initial_sidebar_state="collapsed")

# دالة معالجة النصوص العربية للـ PDF
def ar(text):
    if not text: return ""
    return get_display(reshape(str(text)))

# نظام الترجمة المتكامل
t = {
    "العربية": {
        "title": "إمبراطورية Rayane Tailor Elite",
        "subtitle": "النظام الذكي المتكامل للتفصيل والحياكة الراقية",
        "step1": "🖼️ ميزة البحث والتعرف على الموديل",
        "step2": "👥 بروفايل الزبون ونوع اللباس",
        "step3": "📏 هندسة المقاسات والباترون الذكي",
        "step4": "🧪 الحاسبة الذكية للأقمشة والسلع",
        "step5": "🧾 الإدارة المالية والربط السحابي",
        "upload_btn": "رفع صورة الموديل (من الجهاز، بنترست، أو المتصفح)",
        "gender": "جنس الزبون",
        "style": "تصنيف اللباس العالمي",
        "trad_style": "اللباس التقليدي جزائري",
        "cut": "نوع القصة (الخراطة)",
        "save_cloud": "💾 مزامنة وحفظ (Google Sheets)",
        "load_cloud": "🔄 استيراد قاعدة البيانات",
        "status": "تتبع حالة الطلبية",
        "pdf_inv": "توليد فاتورة PDF احترافية بالعربية",
        "pdf_pat": "توليد كشف الباترون PDF"
    },
    "English": {
        "title": "Rayane Tailor Elite Empire",
        "subtitle": "Smart Integrated System for High-End Couture",
        "step1": "🖼️ Image Search & Model Recognition",
        "step2": "👥 Client Profile & Garment Type",
        "step3": "📏 Measurement Engineering & Smart Pattern",
        "step4": "🧪 Smart Fabric & Supplies Calculator",
        "step5": "🧾 Financial Management & Cloud Sync",
        "upload_btn": "Upload Model (Device, Pinterest, or Web)",
        "gender": "Client Gender",
        "style": "Global Garment Style",
        "trad_style": "Algerian Traditional Wear",
        "cut": "Cut Type",
        "save_cloud": "💾 Sync & Save (Google Sheets)",
        "load_cloud": "🔄 Import Database",
        "status": "Order Status Tracking",
        "pdf_inv": "Generate Arabic PDF Invoice",
        "pdf_pat": "Generate Pattern PDF Sheet"
    }
}

# قاعدة بيانات المقاسات العالمية
size_charts = {
    "S": {"neck": 34, "shoulder": 38, "armhole": 22, "bust": 88, "w1": 68, "w2": 72, "w3": 92, "width": 95, "total": 140, "sleeve": 58, "arm_c": 30},
    "M": {"neck": 36, "shoulder": 40, "armhole": 24, "bust": 96, "w1": 76, "w2": 80, "w3": 100, "width": 105, "total": 142, "sleeve": 59, "arm_c": 32},
    "L": {"neck": 38, "shoulder": 42, "armhole": 26, "bust": 104, "w1": 84, "w2": 88, "w3": 108, "width": 115, "total": 145, "sleeve": 60, "arm_c": 34},
    "XL": {"neck": 40, "shoulder": 44, "armhole": 28, "bust": 112, "w1": 92, "w2": 96, "w3": 116, "width": 125, "total": 148, "sleeve": 61, "arm_c": 36}
}

# CSS الملكي المطور
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #fcfaf7; background-image: url("https://www.transparenttextures.com/patterns/pinstriped-suit.png"); }
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .header-style {
        background: linear-gradient(135deg, #1a0933 0%, #4B0D85 100%);
        padding: 40px; border-radius: 0px 0px 60px 60px; color: white; text-align: center;
        border-bottom: 10px solid #D4AF37; box-shadow: 0 20px 40px rgba(0,0,0,0.4); margin-bottom: 30px;
    }
    .stExpander { background-color: white !important; border-right: 8px solid #D4AF37 !important; border-radius: 15px !important; margin-bottom: 10px !important; }
    .stButton>button { 
        background: linear-gradient(to right, #2D0B5A, #D4AF37); 
        color: white; border-radius: 30px; border: none; padding: 15px; font-weight: bold; transition: 0.5s; width: 100%;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
    </style>
    """, unsafe_allow_html=True)

# 2. نظام الدخول الآمن (Secrets)
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div class="header-style"><h2>🔐 Rayane Tailor Elite Access</h2></div>', unsafe_allow_html=True)
        pwd = st.text_input("License Key", type="password")
        if st.button("Authorize"):
            if pwd == st.secrets.get("PASSWORD", "Rano 2912"):
                st.session_state.auth = True
                st.rerun()
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3050/3050212.png", width=100)
    sel_lang = st.selectbox("Language / اللغة", ["العربية", "English"])
    cur_t = t[sel_lang]
    st.divider()
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.markdown(f'<div class="header-style"><h1>{cur_t["title"]}</h1><p>{cur_t["subtitle"]}</p></div>', unsafe_allow_html=True)

# --- الخطوة 1: البحث والرفع ---
with st.expander(cur_t["step1"], expanded=True):
    img_file = st.file_uploader(cur_t["upload_btn"], type=['png', 'jpg', 'jpeg'])
    if img_file: st.image(img_file, width=300, caption="الموديل المستهدف")

# --- الخطوة 2: نوع اللباس والزبون ---
with st.expander(cur_t["step2"]):
    c1, c2 = st.columns(2)
    with c1:
        gender = st.radio(cur_t["gender"], ["رجل/Man", "امرأة/Woman", "ولد/Boy", "بنت/Girl"], horizontal=True)
        garment_type = st.selectbox(cur_t["style"], 
            ["كاجوال/Casual", "رسمي/Formal", "سروال/Pants", "تريكو/Sweater", "جوب/Skirt", "فستان/Dress", "فاست/Jacket", "ملابس داخلية/Lingerie", "آخر/Other"])
    with c2:
        algerian_trad = st.selectbox(cur_t["trad_style"], 
            ["None", "قندورة", "كاراكو", "قفطان جزائري", "شدة تلمسانية", "كاميزورا", "غليلة", "زدف سطايفي", "جبة قبايلي", "بلوزة وهرانية", "ملحفة عنابية", "شاوي", "نايلي", "بدرون عاصمي"])
        cut_type = st.select_slider(cur_t["cut"], options=["سوغطاي/Slim", "عادي/Regular", "فضفاض/Oversize", "ايفازي/A-Line", "كلوش/Full", "دوبل كلوش/Double Cloch"])

# --- الخطوة 3: المقاسات والباترون الهندسي ---
with st.expander(cur_t["step3"]):
    preset = st.radio("المقياس العالمي:", ["Manual", "S", "M", "L", "XL"], horizontal=True)
    def_vals = size_charts.get(preset, size_charts["M"])
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        m_neck = st.number_input("الرقبة", value=def_vals["neck"])
        m_shoulder = st.number_input("الكتف", value=def_vals["shoulder"])
        m_armhole = st.number_input("حردة الابط", value=def_vals["armhole"])
        m_bust = st.number_input("محيط الصدر", value=def_vals["bust"])
    with col_m2:
        m_w1 = st.number_input("الخصر 1 (العلوي)", value=def_vals["w1"])
        m_w2 = st.number_input("الخصر 2 (الأوسط)", value=def_vals["w2"])
        m_w3 = st.number_input("الخصر 3 (السفلي)", value=def_vals["w3"])
        m_width = st.number_input("العرض الكلي", value=def_vals["width"])
    with col_m3:
        m_total = st.number_input("الطول الكلي", value=def_vals["total"])
        m_arm_l = st.number_input("طول الذراع", value=def_vals["sleeve"])
        m_arm_c = st.number_input("محيط الذراع", value=def_vals["arm_c"])
        m_shoulder_slope = st.slider("ميلان الكتف", 0, 10, 3)

    extra_features = st.multiselect("الإضافات الهندسية:", ["بانسات الصدر", "بانسات الظهر", "كشكشة", "طيات", "قماش مطاطي"])

    # رسم الباترون المطور (SVG)
    pattern_svg = f"""
    <svg width="100%" height="400" viewBox="0 0 500 400" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#fff" stroke="#D4AF37" stroke-width="2" stroke-dasharray="5,5"/>
        <path d="M 150,50 L 250,50 L 280,{50+m_shoulder_slope*5} L 320,150 L 300,350 L 100,350 Z" fill="none" stroke="#2D0B5A" stroke-width="3"/>
        <text x="160" y="45" font-size="12" fill="#2D0B5A">Neck: {m_neck}cm</text>
        <text x="300" y="100" font-size="12" fill="red">Armhole: {m_armhole}cm</text>
        <text x="180" y="200" font-size="12">Bust: {m_bust}cm</text>
        <text x="120" y="380" font-size="14" font-weight="bold">Total: {m_total}cm</text>
        <circle cx="250" cy="50" r="3" fill="red"/>
    </svg>
    """
    st.components.v1.html(pattern_svg, height=410)

# --- الخطوة 4: الحاسبة الذكية ---
with st.expander(cur_t["step4"]):
    c_calc1, c_calc2 = st.columns(2)
    with c_calc1:
        fabric_type = st.selectbox("نوع القماش", ["قطيفة", "حرير", "كتان", "كريب", "ستان", "قماش عسكري", "جينز"])
        unit_price = st.number_input("سعر المتر (DA)", value=1200)
    with c_calc2:
        base_fabric = (m_total + m_arm_l + 30) / 100
        multiplier = 1.0
        if "كلوش" in cut_type: multiplier = 2.5
        elif "دوبل كلوش" in cut_type: multiplier = 4.5
        total_fabric = base_fabric * multiplier
        st.metric("القماش المطلوب", f"{total_fabric:.2f} م")
        labor_cost = st.number_input("حق الخياطة (DA)", value=3000)

# --- الخطوة 5: الفاتورة والسحابة ---
with st.expander(cur_t["step5"]):
    total_price = (total_fabric * unit_price) + labor_cost
    order_status = st.select_slider("تتبع حالة الطلب:", options=["قيد الانتظار", "تم قص القماش", "تحت الماكينة", "جاهز للتسليم", "تم التسليم"])
    
    current_style = algerian_trad if algerian_trad != "None" else garment_type
    inv_data = {
        "Date": datetime.now().strftime("%Y-%m-%d"), "Client": gender, "Style": current_style,
        "Total": f"{total_price} DA", "Status": order_status
    }
    
    st.table(pd.DataFrame([inv_data]))

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button(cur_t["save_cloud"]):
            try:
                new_row = pd.DataFrame([{
                    "Date": inv_data["Date"], "Client": gender, "Style": current_style, 
                    "Fabric": fabric_type, "Total": total_price, "Status": order_status,
                    "Neck": m_neck, "Shoulder": m_shoulder, "Bust": m_bust, "Total_L": m_total
                }])
                existing_data = conn.read(spreadsheet=st.secrets.get("GSHEET_URL"))
                updated_df = pd.concat([existing_data, new_row], ignore_index=True)
                conn.update(spreadsheet=st.secrets.get("GSHEET_URL"), data=updated_df)
                st.success("✅ تم تحديث Google Sheets بنجاح!")
            except Exception as e: st.error(f"فشل الاتصال: {e}")
    
    with col_btn2:
        if st.button(cur_t["pdf_inv"]):
            pdf = FPDF()
            pdf.add_page()
            
            # تطبيق النصيحة الذهبية: إضافة الخط العربي Cairo
            try:
                pdf.add_font('Cairo', '', 'Cairo-Regular.ttf', uni=True)
                pdf.set_font('Cairo', '', 16)
            except:
                # في حالة عدم وجود الملف، يستخدم Arial كاحتياط
                pdf.set_font("Arial", "B", 16)
            
            pdf.cell(200, 10, ar("Rayane Tailor Elite - فاتورة رسمية"), ln=True, align='C')
            pdf.ln(10)
            
            if 'Cairo' in pdf.fonts: pdf.set_font('Cairo', '', 12)
            else: pdf.set_font("Arial", "", 12)
            
            pdf.cell(200, 10, f"{ar('التاريخ')}: {inv_data['Date']}", ln=True, align='R')
            pdf.cell(200, 10, f"{ar('النوع')}: {ar(current_style)}", ln=True, align='R')
            pdf.cell(200, 10, f"{ar('الحالة')}: {ar(order_status)}", ln=True, align='R')
            pdf.cell(200, 10, f"{ar('المبلغ الإجمالي')}: {total_price} DA", ln=True, align='R')
            
            # قسم المقاسات في PDF
            pdf.ln(5)
            pdf.cell(200, 10, ar("--- المقاسات الفنية ---"), ln=True, align='C')
            pdf.cell(200, 10, f"{ar('الرقبة')}: {m_neck} | {ar('الكتف')}: {m_shoulder}", ln=True, align='R')
            pdf.cell(200, 10, f"{ar('الصدر')}: {m_bust} | {ar('الطول')}: {m_total}", ln=True, align='R')
            
            pdf_out = pdf.output()
            st.download_button("Download Arabic PDF Invoice", data=pdf_out, file_name=f"Invoice_{datetime.now().strftime('%H%M%S')}.pdf", mime="application/pdf")

st.caption("Rayane Tailor Elite - جميع الحقوق محفوظة 2026")
