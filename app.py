import streamlit as st
import pandas as pd
import qrcode
import urllib.parse
from io import BytesIO
import base64

# 1. Configuration & Ultra-Modern CSS
st.set_page_config(page_title="Rayane Tailor Elite Pro", layout="wide", initial_sidebar_state="collapsed")

# نظام الترجمة (Dictionary for Dual Language)
t = {
    "العربية": {
        "title": "لوحة تحكم Rayane Tailor Elite",
        "subtitle": "نظام إدارة التفصيل الفاخر",
        "step1": "🖼️ الخطوة 1: مصدر الإلهام",
        "step2": "👥 الخطوة 2: نوع الزبون واللباس",
        "step3": "📏 الخطوة 3: المقاسات والباترون",
        "step4": "🧪 الخطوة 4: حاسبة السلع",
        "step5": "🧾 الخطوة 5: الفاتورة النهائية",
        "upload_btn": "تحميل صورة (من المتصفح، فيسبوك، أو بانترست)",
        "gender": "جنس الزبون",
        "style": "نوع اللباس",
        "cut": "نوع القصة",
        "calc_btn": "حساب القماش والسلع",
        "print_pat": "تحميل وطباعة الباترون (PDF/Image)",
        "print_inv": "تحميل وطباعة الفاتورة",
        "wa_send": "إرسال عبر واتساب",
        "lang_label": "تغيير اللغة / Switch Language",
        "trad": "لباس تقليدي جزائري",
        "size_preset": "اختيار مقاس جاهز (اختياري)"
    },
    "English": {
        "title": "Rayane Tailor Elite Dashboard",
        "subtitle": "Luxury Bespoke Management System",
        "step1": "🖼️ Step 1: Inspiration",
        "step2": "👥 Step 2: Client & Style",
        "step3": "📏 Step 3: Measurements & Pattern",
        "step4": "🧪 Step 4: Fabric Calculator",
        "step5": "🧾 Step 5: Final Invoice",
        "upload_btn": "Upload Image (Browser, FB, Pinterest)",
        "gender": "Client Gender",
        "style": "Garment Style",
        "cut": "Cut Type",
        "calc_btn": "Calculate Fabric & Supplies",
        "print_pat": "Download & Print Pattern",
        "print_inv": "Download & Print Invoice",
        "wa_send": "Send via WhatsApp",
        "lang_label": "Switch Language / تغيير اللغة",
        "trad": "Algerian Traditional",
        "size_preset": "Choose Preset Size (Optional)"
    }
}

# قاعدة بيانات المقاسات العالمية (Values based on standard charts)
size_charts = {
    "S": {"neck": 34, "shoulder": 38, "armhole": 22, "bust": 88, "w1": 68, "w2": 72, "w3": 92, "width": 95, "total": 140, "sleeve": 58, "arm_c": 30},
    "M": {"neck": 36, "shoulder": 40, "armhole": 24, "bust": 96, "w1": 76, "w2": 80, "w3": 100, "width": 105, "total": 142, "sleeve": 59, "arm_c": 32},
    "L": {"neck": 38, "shoulder": 42, "armhole": 26, "bust": 104, "w1": 84, "w2": 88, "w3": 108, "width": 115, "total": 145, "sleeve": 60, "arm_c": 34},
    "XL": {"neck": 40, "shoulder": 44, "armhole": 28, "bust": 112, "w1": 92, "w2": 96, "w3": 116, "width": 125, "total": 148, "sleeve": 61, "arm_c": 36}
}

# CSS الملكي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .header-style {
        background: linear-gradient(135deg, #2D0B5A 0%, #4B0D85 100%);
        padding: 40px; border-radius: 30px; color: white; text-align: center;
        border-bottom: 6px solid #D4AF37; box-shadow: 0 15px 35px rgba(0,0,0,0.2); margin-bottom: 30px;
    }
    .stButton>button { background: #2D0B5A; color: white; border-radius: 10px; border: none; padding: 10px 20px; transition: 0.3s; width: 100%;}
    .stButton>button:hover { background: #D4AF37; color: #2D0B5A; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# 2. Secure Authentication System
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div class="header-style"><h2>🔐 Rayane Tailor Elite</h2><p>Access Secure Panel</p></div>', unsafe_allow_html=True)
        pwd = st.text_input("License Key", type="password")
        sheet = st.text_input("Data Source (Google Sheets URL)")
        if st.button("Authorize Access"):
            if pwd == "Rano 2912" and "docs" in sheet:
                st.session_state.auth, st.session_state.url = True, sheet
                st.rerun()
    st.stop()

# 3. Sidebar Settings
with st.sidebar:
    st.markdown("### 🌐 Settings")
    sel_lang = st.selectbox("Language / اللغة", ["العربية", "English"])
    cur_t = t[sel_lang]
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

# 4. Main Dashboard Header
st.markdown(f'<div class="header-style"><h1>{cur_t["title"]}</h1><p>{cur_t["subtitle"]}</p></div>', unsafe_allow_html=True)

# الخطوة 1: الصورة
with st.expander(cur_t["step1"], expanded=True):
    img_file = st.file_uploader(cur_t["upload_btn"], type=['png', 'jpg', 'jpeg'])
    if img_file: st.image(img_file, width=300)

# الخطوة 2: النوع واللباس
with st.expander(cur_t["step2"]):
    c1, c2, c3 = st.columns(3)
    with c1:
        gender = st.radio(cur_t["gender"], ["رجل/Man", "امرأة/Woman", "طفل/Boy", "طفلة/Girl"])
    with c2:
        category = st.selectbox(cur_t["style"], ["كاجوال/Casual", "رسمي/Formal", "سواري/Soirée", cur_t["trad"]])
        if category == cur_t["trad"]:
            trad_style = st.selectbox("Type:", ["كاراكو", "قفطان", "قندورة", "زدف سطايفي", "الشدة", "جابادور"])
    with c3:
        cut = st.selectbox(cur_t["cut"], ["سوغطاي", "ايفازي", "كلوش", "دوبل كلوش"])

# الخطوة 3: المقاسات والباترون
with st.expander(cur_t["step3"]):
    st.info(f"📏 {cur_t['size_preset']}")
    preset = st.radio("Sizes:", ["Manual/يدوي", "S", "M", "L", "XL"], horizontal=True)
    
    # تحميل المقاسات المختارة أو الافتراضية
    defaults = size_charts.get(preset, {"neck": 35, "shoulder": 40, "armhole": 25, "bust": 90, "w1": 70, "w2": 75, "w3": 80, "width": 100, "total": 145, "sleeve": 60, "arm_c": 35})
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        neck = st.number_input("الرقبة/Neck", value=defaults["neck"])
        shoulder = st.number_input("الكتف/Shoulder", value=defaults["shoulder"])
        armhole = st.number_input("حردة الابط/Armhole", value=defaults["armhole"])
    with m_col2:
        bust = st.number_input("الصدر/Bust", value=defaults["bust"])
        w1 = st.number_input("الخصر 1/Waist 1", value=defaults["w1"])
        w2 = st.number_input("الخصر 2/Waist 2", value=defaults["w2"])
    with m_col3:
        w3 = st.number_input("الخصر 3/Waist 3", value=defaults["w3"])
        width_val = st.number_input("العرض/Width", value=defaults["width"])
        total_l = st.number_input("الطول/Total Length", value=defaults["total"])
    with m_col4:
        arm_l = st.number_input("طول الذراع/Sleeve", value=defaults["sleeve"])
        arm_c = st.number_input("محيط الذراع/Arm Circ.", value=defaults["arm_c"])
        ease = st.number_input("حق الخياطة/Ease", 4)

    details = st.multiselect("Details:", ["كشكشة/Fronces", "طيات/Plis", "بانسات الصدر", "بانسات الظهر", "لاديكوب"])

    # رسم الباترون الذكي (SVG)
    svg_code = f"""
    <svg width="600" height="450" viewBox="0 0 600 450" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="white" stroke="#2D0B5A" stroke-width="3"/>
        <path d="M 100,30 L 250,30 L 280,120 L 240,400 L 100,400 Z" fill="none" stroke="black" stroke-width="2"/>
        <text x="110" y="25" font-family="Arial" font-size="10" fill="red">Shoulder: {shoulder}cm</text>
        <text x="110" y="140" font-family="Arial" font-size="10">Bust: {bust}cm</text>
        <text x="110" y="220" font-family="Arial" font-size="10">Waist(1): {w1}cm | (2): {w2}cm</text>
        <text x="110" y="380" font-family="Arial" font-size="10">Total Length: {total_l}cm</text>
        <text x="400" y="430" font-family="Arial" font-size="10" fill="gray">Rayane Tailor - Scale 1:1</text>
    </svg>
    """
    
    st.components.v1.html(svg_code, height=460)
    st.download_button(cur_t["print_pat"], data=svg_code, file_name="pattern_rayane.svg", mime="image/svg+xml")

# الخطوة 4: حاسبة السلع
with st.expander(cur_t["step4"]):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        f_name = st.selectbox("Fabric Type", ["قطيفة", "حرير", "كتان", "كريب", "ستان"])
        f_price = st.number_input("Price/Meter (DA)", 800)
    with f_col2:
        m_needed = (total_l + arm_l + 25) / 100
        if cut == "كلوش": m_needed *= 2.0
        elif cut == "دوبل كلوش": m_needed *= 4.0
        st.metric("Needed Meters", f"{m_needed:.2f} m")
    acc = st.text_area("Accessories", "Matching Thread, Zippers, Buttons...")

# الخطوة 5: الفاتورة
with st.expander(cur_t["step5"]):
    mat_cost = m_needed * f_price
    labor = st.number_input("Tailoring Fee (DA)", 2500)
    total_bill = mat_cost + labor
    
    invoice_html = f"""
    <div style="padding:30px; border:4px solid #D4AF37; border-radius:15px; background:white; color:black; font-family:sans-serif; direction:ltr;">
        <h1 style="text-align:center; color:#2D0B5A;">RAYANE TAILOR ELITE</h1>
        <p style="text-align:center;">Luxury Bespoke & Couture</p>
        <hr>
        <table style="width:100%;">
            <tr><td><b>Category:</b> {category}</td><td><b>Cut:</b> {cut}</td></tr>
            <tr><td><b>Total Fabric:</b> {m_needed:.2f}m</td><td><b>Price:</b> {mat_cost:.2f} DA</td></tr>
            <tr><td><b>Tailoring Fee:</b></td><td><b>{labor:.2f} DA</b></td></tr>
        </table>
        <h2 style="background:#2D0B5A; color:white; padding:10px; text-align:center;">GRAND TOTAL: {total_bill:.2f} DA</h2>
    </div>
    """
    
    st.markdown(invoice_html, unsafe_allow_html=True)
    st.download_button(cur_t["print_inv"], data=invoice_html, file_name="invoice_rayane.html", mime="text/html")
    
    phone = st.text_input("WhatsApp (Ex: 213555...)")
    if st.button(cur_t["wa_send"]):
        msg = urllib.parse.quote(f"Rayane Tailor Elite Invoice\nTotal: {total_bill} DA")
        st.markdown(f'<a href="https://wa.me/{phone}?text={msg}" target="_blank">Click to Open WhatsApp</a>', unsafe_allow_html=True)

st.caption("Developed for Rayane Tailor Elite © 2026")
