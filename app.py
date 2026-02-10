import streamlit as st
import pandas as pd
import qrcode
import urllib.parse
from io import BytesIO
import base64
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Configuration & Ultra-Modern CSS
st.set_page_config(page_title="Rayane Tailor Elite Pro", layout="wide", initial_sidebar_state="collapsed")

# نظام الترجمة
t = {
    "العربية": {
        "title": "أتيليه Rayane Tailor Elite",
        "subtitle": "إبداع الأنامل في عالم التفصيل الراقي",
        "step1": "🖼️ المعرض: مصدر الإلهام والموديل",
        "step2": "👥 العميل: تحديد نوع القصة والزبون",
        "step3": "📏 الورشة: هندسة المقاسات والباترون",
        "step4": "🧪 التجهيز: حاسبة الأقمشة واللوازم",
        "step5": "🧾 الحساب: الفاتورة النهائية والربط السحابي",
        "upload_btn": "رفع صورة التصميم (من الجهاز أو المتصفح)",
        "gender": "جنس الزبون",
        "style": "تصنيف اللباس",
        "cut": "نوع القصة (الخراطة)",
        "calc_btn": "حساب متطلبات الورشة",
        "print_pat": "تحميل وطباعة الباترون الهندسي",
        "print_inv": "تحميل وطباعة الفاتورة الفاخرة",
        "wa_send": "إرسال الفاتورة عبر الواتساب",
        "lang_label": "تغيير اللغة / Switch Language",
        "trad": "لباس تقليدي جزائري",
        "size_preset": "تطبيق مقاس عالمي جاهز",
        "save_cloud": "💾 حفظ وإرسال للجدول السحابي",
        "load_cloud": "🔄 استيراد آخر البيانات من الجدول"
    },
    "English": {
        "title": "Rayane Tailor Elite Atelier",
        "subtitle": "Bespoke Elegance & High-End Couture",
        "step1": "🖼️ Gallery: Design & Inspiration",
        "step2": "👥 Client: Profile & Style Selection",
        "step3": "📏 Workshop: Measurement Engineering",
        "step4": "🧪 Preparation: Fabric & Supplies Calc",
        "step5": "🧾 Billing: Final Luxury Invoice & Cloud Sync",
        "upload_btn": "Upload Design Sketch (Device or Web)",
        "gender": "Client Gender",
        "style": "Garment Category",
        "cut": "Cut Type",
        "calc_btn": "Calculate Workshop Needs",
        "print_pat": "Download & Print Technical Pattern",
        "print_inv": "Download & Print Luxury Invoice",
        "wa_send": "Send Invoice via WhatsApp",
        "lang_label": "Switch Language / تغيير اللغة",
        "trad": "Algerian Traditional",
        "size_preset": "Apply International Size Preset",
        "save_cloud": "💾 Save & Sync to Cloud Sheet",
        "load_cloud": "🔄 Load Latest Data from Sheet"
    }
}

size_charts = {
    "S": {"neck": 34, "shoulder": 38, "armhole": 22, "bust": 88, "w1": 68, "w2": 72, "w3": 92, "width": 95, "total": 140, "sleeve": 58, "arm_c": 30},
    "M": {"neck": 36, "shoulder": 40, "armhole": 24, "bust": 96, "w1": 76, "w2": 80, "w3": 100, "width": 105, "total": 142, "sleeve": 59, "arm_c": 32},
    "L": {"neck": 38, "shoulder": 42, "armhole": 26, "bust": 104, "w1": 84, "w2": 88, "w3": 108, "width": 115, "total": 145, "sleeve": 60, "arm_c": 34},
    "XL": {"neck": 40, "shoulder": 44, "armhole": 28, "bust": 112, "w1": 92, "w2": 96, "w3": 116, "width": 125, "total": 148, "sleeve": 61, "arm_c": 36}
}

# CSS الملكي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #fcfaf7; background-image: url("https://www.transparenttextures.com/patterns/pinstriped-suit.png"); }
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .header-style {
        background: linear-gradient(135deg, #2D0B5A 0%, #4B0D85 100%);
        padding: 50px; border-radius: 0px 0px 50px 50px; color: white; text-align: center;
        border-bottom: 8px solid #D4AF37; box-shadow: 0 15px 35px rgba(0,0,0,0.3); margin-bottom: 40px;
        position: relative; overflow: hidden;
    }
    .header-style::after { content: "✂️"; position: absolute; right: 20px; bottom: 10px; opacity: 0.2; font-size: 80px; transform: rotate(-20deg); }
    .stExpander { background-color: white !important; border: 1px solid #e0e0e0 !important; border-right: 5px solid #D4AF37 !important; border-radius: 15px !important; margin-bottom: 15px !important; }
    .stButton>button { 
        background: linear-gradient(to right, #2D0B5A, #4B0D85); 
        color: white; border-radius: 25px; border: 2px solid #D4AF37; 
        padding: 12px 25px; font-weight: bold; transition: 0.4s; width: 100%;
    }
    .stButton>button:hover { background: #D4AF37; color: #2D0B5A; transform: translateY(-3px); }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; }
    .invoice-card { background: #fff; border: 2px solid #D4AF37; padding: 40px; border-radius: 10px; background-image: url("https://www.transparenttextures.com/patterns/paper-fibers.png"); }
    </style>
    """, unsafe_allow_html=True)

# 2. Secure Authentication & Sheet Connection
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div class="header-style"><h2>🔐 Rayane Tailor Elite</h2><p>Exclusive Fashion Access</p></div>', unsafe_allow_html=True)
        pwd = st.text_input("License Key", type="password")
        sheet_url = st.text_input("Google Sheets URL")
        if st.button("Authorize Access"):
            if pwd == "Rano 2912" and "docs" in sheet_url:
                st.session_state.auth, st.session_state.url = True, sheet_url
                st.rerun()
    st.stop()

# إنشاء اتصال حقيقي بجدول بيانات جوجل مع معالجة الاستثناءات الاحترافية
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn = None

# 3. Sidebar Settings
with st.sidebar:
    st.markdown("### 🧵 Atelier Settings")
    sel_lang = st.selectbox("Language / اللغة", ["العربية", "English"])
    cur_t = t[sel_lang]
    st.markdown("---")
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

# 4. Main Dashboard Header
st.markdown(f'<div class="header-style"><h1>{cur_t["title"]}</h1><p style="font-style: italic; font-size: 1.2rem;">{cur_t["subtitle"]}</p></div>', unsafe_allow_html=True)

# الخطوات 1-4 (نفس الكود الأصلي تماماً دون حذف أي حرف)
with st.expander(cur_t["step1"], expanded=True):
    img_file = st.file_uploader(cur_t["upload_btn"], type=['png', 'jpg', 'jpeg'])
    if img_file: 
        st.markdown("#### 👗 التصميم المختار:")
        st.image(img_file, width=400)

with st.expander(cur_t["step2"]):
    c1, c2, c3 = st.columns(3)
    with c1: gender = st.radio(cur_t["gender"], ["رجل/Man", "امرأة/Woman", "طفل/Boy", "طفلة/Girl"])
    with c2:
        category = st.selectbox(cur_t["style"], ["كاجوال/Casual", "رسمي/Formal", "سواري/Soirée", cur_t["trad"]])
        trad_style = ""
        if category == cur_t["trad"]: trad_style = st.selectbox("Type:", ["كاراكو", "قفطان", "قندورة", "زدف سطايفي", "الشدة", "جابادور"])
    with c3: cut = st.selectbox(cur_t["cut"], ["سوغطاي", "ايفازي", "كلوش", "دوبل كلوش"])

with st.expander(cur_t["step3"]):
    st.markdown("#### 📏 لوحة القياسات الدقيقة")
    preset = st.radio(cur_t['size_preset'], ["Manual/يدوي", "S", "M", "L", "XL"], horizontal=True)
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
    details = st.multiselect("الإضافات الفنية:", ["كشكشة/Fronces", "طيات/Plis", "بانسات الصدر", "بانسات الظهر", "لاديكوب برانساس"])
    svg_code = f"""<svg width="600" height="450" viewBox="0 0 600 450" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#fff" stroke="#2D0B5A" stroke-width="2" stroke-dasharray="10,5"/><path d="M 100,30 L 250,30 L 280,120 L 240,400 L 100,400 Z" fill="#f9f3ff" stroke="#4B0D85" stroke-width="2"/><text x="110" y="25" font-family="Cairo" font-size="12" fill="#2D0B5A" font-weight="bold">Shoulder: {shoulder}cm</text><text x="110" y="140" font-family="Cairo" font-size="12">Bust: {bust}cm</text><text x="110" y="220" font-family="Cairo" font-size="12">Waist (Mid): {w2}cm</text><text x="110" y="380" font-family="Cairo" font-size="12" fill="red">Total: {total_l}cm</text><circle cx="280" cy="120" r="4" fill="#D4AF37"/><text x="400" y="430" font-family="Cairo" font-size="10" fill="gray">Rayane Tailor Elite - Technical Pattern</text></svg>"""
    st.components.v1.html(svg_code, height=460)
    st.download_button(cur_t["print_pat"], data=svg_code, file_name="Rayane_Pattern.svg", mime="image/svg+xml")

with st.expander(cur_t["step4"]):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        f_name = st.selectbox("نوع القماش المختارة:", ["قطيفة", "حرير", "كتان", "كريب", "ستان", "قماش السهرة"])
        f_price = st.number_input("سعر المتر (DA):", 800)
    with f_col2:
        m_needed = (total_l + arm_l + 25) / 100
        if cut == "كلوش": m_needed *= 2.0
        elif cut == "دوبل كلوش": m_needed *= 4.0
        st.metric("كمية القماش المطلوبة", f"{m_needed:.2f} m")
    acc = st.text_area("لوازم الخياطة المطلوبة:", "Matching Thread, Luxury Buttons, Zippers...")

# الخطوة 5: الفاتورة والربط السحابي المزدوج (قراءة وكتابة)
with st.expander(cur_t["step5"]):
    mat_cost = m_needed * f_price
    labor = st.number_input("تكلفة التفصيل واليد (DA):", 2500)
    total_bill = mat_cost + labor
    
    invoice_html = f"""<div class="invoice-card" style="direction:ltr;"><h1 style="text-align:center; color:#2D0B5A; margin:0;">RAYANE TAILOR ELITE</h1><p style="text-align:center; font-style:italic; border-bottom:1px solid #D4AF37; padding-bottom:10px;">Luxury Custom Tailoring</p><table style="width:100%; margin-top:20px; font-family:sans-serif;"><tr><td style="padding:10px;"><b>Category:</b></td><td>{category} ({cut})</td></tr><tr><td style="padding:10px;"><b>Fabric Type:</b></td><td>{f_name} ({m_needed:.2f} meters)</td></tr><tr><td style="padding:10px;"><b>Materials Cost:</b></td><td>{mat_cost:.2f} DA</td></tr><tr><td style="padding:10px;"><b>Tailoring Labor:</b></td><td>{labor:.2f} DA</td></tr><tr style="background:#2D0B5A; color:white;"><td style="padding:15px;"><b>TOTAL AMOUNT:</b></td><td style="padding:15px;"><b>{total_bill:.2f} DA</b></td></tr></table></div>"""
    st.markdown(invoice_html, unsafe_allow_html=True)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button(cur_t["save_cloud"]):
            new_data = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Client": gender, "Category": category, "Cut": cut,
                "Neck": neck, "Shoulder": shoulder, "Armhole": armhole, "Bust": bust,
                "W1": w1, "W2": w2, "W3": w3, "Total Length": total_l,
                "Fabric": f_name, "Meters": m_needed, "Total DA": total_bill
            }
            if conn:
                try:
                    existing_data = conn.read(spreadsheet=st.session_state.url)
                    updated_df = pd.concat([existing_data, pd.DataFrame([new_data])], ignore_index=True)
                    conn.update(spreadsheet=st.session_state.url, data=updated_df)
                    st.success("✅ تم التزامن والحفظ في الجدول فوراً!")
                except Exception as e:
                    st.error(f"⚠️ خطأ في الاتصال السحابي: {e}")
            else:
                st.warning("يرجى إعداد st.connection في ملف الأسرار للربط الفعلي.")

    with c2:
        if st.button(cur_t["load_cloud"]):
            if conn:
                try:
                    cloud_data = conn.read(spreadsheet=st.session_state.url)
                    st.markdown("#### 📜 سجل العمليات الأخير:")
                    st.dataframe(cloud_data.tail(5))
                except Exception as e:
                    st.error(f"⚠️ تعذر استيراد البيانات: {e}")
            else:
                st.info("الجدول فارغ أو غير مرتبط.")

    st.download_button(cur_t["print_inv"], data=invoice_html, file_name="Rayane_Invoice.html", mime="text/html")
    phone = st.text_input("رقم واتساب العميل (Ex: 213...):")
    if st.button(cur_t["wa_send"]):
        msg = urllib.parse.quote(f"Rayane Tailor Elite Atelier\nFinal Invoice Details:\nTotal Amount: {total_bill} DA")
        st.markdown(f'<a href="https://wa.me/{phone}?text={msg}" target="_blank">Confirm and Send via WhatsApp</a>', unsafe_allow_html=True)

st.caption("Rayane Tailor Elite Atelier - Bespoke Couture System 2026")

Le mar. 10 févr. 2026 à 14:41, rayane ranoch <rayaneranoch525@gmail.com> a écrit :
import streamlit as st
import pandas as pd
import qrcode
import urllib.parse
from io import BytesIO
import base64
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Configuration & Ultra-Modern CSS
st.set_page_config(page_title="Rayane Tailor Elite Pro", layout="wide", initial_sidebar_state="collapsed")

# نظام الترجمة
t = {
    "العربية": {
        "title": "أتيليه Rayane Tailor Elite",
        "subtitle": "إبداع الأنامل في عالم التفصيل الراقي",
        "step1": "🖼️ المعرض: مصدر الإلهام والموديل",
        "step2": "👥 العميل: تحديد نوع القصة والزبون",
        "step3": "📏 الورشة: هندسة المقاسات والباترون",
        "step4": "🧪 التجهيز: حاسبة الأقمشة واللوازم",
        "step5": "🧾 الحساب: الفاتورة النهائية والربط السحابي",
        "upload_btn": "رفع صورة التصميم (من الجهاز أو المتصفح)",
        "gender": "جنس الزبون",
        "style": "تصنيف اللباس",
        "cut": "نوع القصة (الخراطة)",
        "calc_btn": "حساب متطلبات الورشة",
        "print_pat": "تحميل وطباعة الباترون الهندسي",
        "print_inv": "تحميل وطباعة الفاتورة الفاخرة",
        "wa_send": "إرسال الفاتورة عبر الواتساب",
        "lang_label": "تغيير اللغة / Switch Language",
        "trad": "لباس تقليدي جزائري",
        "size_preset": "تطبيق مقاس عالمي جاهز",
        "save_cloud": "💾 حفظ وإرسال للجدول السحابي",
        "load_cloud": "🔄 استيراد آخر البيانات من الجدول"
    },
    "English": {
        "title": "Rayane Tailor Elite Atelier",
        "subtitle": "Bespoke Elegance & High-End Couture",
        "step1": "🖼️ Gallery: Design & Inspiration",
        "step2": "👥 Client: Profile & Style Selection",
        "step3": "📏 Workshop: Measurement Engineering",
        "step4": "🧪 Preparation: Fabric & Supplies Calc",
        "step5": "🧾 Billing: Final Luxury Invoice & Cloud Sync",
        "upload_btn": "Upload Design Sketch (Device or Web)",
        "gender": "Client Gender",
        "style": "Garment Category",
        "cut": "Cut Type",
        "calc_btn": "Calculate Workshop Needs",
        "print_pat": "Download & Print Technical Pattern",
        "print_inv": "Download & Print Luxury Invoice",
        "wa_send": "Send Invoice via WhatsApp",
        "lang_label": "Switch Language / تغيير اللغة",
        "trad": "Algerian Traditional",
        "size_preset": "Apply International Size Preset",
        "save_cloud": "💾 Save & Sync to Cloud Sheet",
        "load_cloud": "🔄 Load Latest Data from Sheet"
    }
}

size_charts = {
    "S": {"neck": 34, "shoulder": 38, "armhole": 22, "bust": 88, "w1": 68, "w2": 72, "w3": 92, "width": 95, "total": 140, "sleeve": 58, "arm_c": 30},
    "M": {"neck": 36, "shoulder": 40, "armhole": 24, "bust": 96, "w1": 76, "w2": 80, "w3": 100, "width": 105, "total": 142, "sleeve": 59, "arm_c": 32},
    "L": {"neck": 38, "shoulder": 42, "armhole": 26, "bust": 104, "w1": 84, "w2": 88, "w3": 108, "width": 115, "total": 145, "sleeve": 60, "arm_c": 34},
    "XL": {"neck": 40, "shoulder": 44, "armhole": 28, "bust": 112, "w1": 92, "w2": 96, "w3": 116, "width": 125, "total": 148, "sleeve": 61, "arm_c": 36}
}

# CSS الملكي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #fcfaf7; background-image: url("https://www.transparenttextures.com/patterns/pinstriped-suit.png"); }
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .header-style {
        background: linear-gradient(135deg, #2D0B5A 0%, #4B0D85 100%);
        padding: 50px; border-radius: 0px 0px 50px 50px; color: white; text-align: center;
        border-bottom: 8px solid #D4AF37; box-shadow: 0 15px 35px rgba(0,0,0,0.3); margin-bottom: 40px;
        position: relative; overflow: hidden;
    }
    .header-style::after { content: "✂️"; position: absolute; right: 20px; bottom: 10px; opacity: 0.2; font-size: 80px; transform: rotate(-20deg); }
    .stExpander { background-color: white !important; border: 1px solid #e0e0e0 !important; border-right: 5px solid #D4AF37 !important; border-radius: 15px !important; margin-bottom: 15px !important; }
    .stButton>button { 
        background: linear-gradient(to right, #2D0B5A, #4B0D85); 
        color: white; border-radius: 25px; border: 2px solid #D4AF37; 
        padding: 12px 25px; font-weight: bold; transition: 0.4s; width: 100%;
    }
    .stButton>button:hover { background: #D4AF37; color: #2D0B5A; transform: translateY(-3px); }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; }
    .invoice-card { background: #fff; border: 2px solid #D4AF37; padding: 40px; border-radius: 10px; background-image: url("https://www.transparenttextures.com/patterns/paper-fibers.png"); }
    </style>
    """, unsafe_allow_html=True)

# 2. Secure Authentication & Sheet Connection
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div class="header-style"><h2>🔐 Rayane Tailor Elite</h2><p>Exclusive Fashion Access</p></div>', unsafe_allow_html=True)
        pwd = st.text_input("License Key", type="password")
        sheet_url = st.text_input("Google Sheets URL")
        if st.button("Authorize Access"):
            if pwd == "Rano 2912" and "docs" in sheet_url:
                st.session_state.auth, st.session_state.url = True, sheet_url
                st.rerun()
    st.stop()

# إنشاء اتصال حقيقي بجدول بيانات جوجل مع معالجة الاستثناءات الاحترافية
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn = None

# 3. Sidebar Settings
with st.sidebar:
    st.markdown("### 🧵 Atelier Settings")
    sel_lang = st.selectbox("Language / اللغة", ["العربية", "English"])
    cur_t = t[sel_lang]
    st.markdown("---")
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

# 4. Main Dashboard Header
st.markdown(f'<div class="header-style"><h1>{cur_t["title"]}</h1><p style="font-style: italic; font-size: 1.2rem;">{cur_t["subtitle"]}</p></div>', unsafe_allow_html=True)

# الخطوات 1-4 (نفس الكود الأصلي تماماً دون حذف أي حرف)
with st.expander(cur_t["step1"], expanded=True):
    img_file = st.file_uploader(cur_t["upload_btn"], type=['png', 'jpg', 'jpeg'])
    if img_file: 
        st.markdown("#### 👗 التصميم المختار:")
        st.image(img_file, width=400)

with st.expander(cur_t["step2"]):
    c1, c2, c3 = st.columns(3)
    with c1: gender = st.radio(cur_t["gender"], ["رجل/Man", "امرأة/Woman", "طفل/Boy", "طفلة/Girl"])
    with c2:
        category = st.selectbox(cur_t["style"], ["كاجوال/Casual", "رسمي/Formal", "سواري/Soirée", cur_t["trad"]])
        trad_style = ""
        if category == cur_t["trad"]: trad_style = st.selectbox("Type:", ["كاراكو", "قفطان", "قندورة", "زدف سطايفي", "الشدة", "جابادور"])
    with c3: cut = st.selectbox(cur_t["cut"], ["سوغطاي", "ايفازي", "كلوش", "دوبل كلوش"])

with st.expander(cur_t["step3"]):
    st.markdown("#### 📏 لوحة القياسات الدقيقة")
    preset = st.radio(cur_t['size_preset'], ["Manual/يدوي", "S", "M", "L", "XL"], horizontal=True)
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
    details = st.multiselect("الإضافات الفنية:", ["كشكشة/Fronces", "طيات/Plis", "بانسات الصدر", "بانسات الظهر", "لاديكوب برانساس"])
    svg_code = f"""<svg width="600" height="450" viewBox="0 0 600 450" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#fff" stroke="#2D0B5A" stroke-width="2" stroke-dasharray="10,5"/><path d="M 100,30 L 250,30 L 280,120 L 240,400 L 100,400 Z" fill="#f9f3ff" stroke="#4B0D85" stroke-width="2"/><text x="110" y="25" font-family="Cairo" font-size="12" fill="#2D0B5A" font-weight="bold">Shoulder: {shoulder}cm</text><text x="110" y="140" font-family="Cairo" font-size="12">Bust: {bust}cm</text><text x="110" y="220" font-family="Cairo" font-size="12">Waist (Mid): {w2}cm</text><text x="110" y="380" font-family="Cairo" font-size="12" fill="red">Total: {total_l}cm</text><circle cx="280" cy="120" r="4" fill="#D4AF37"/><text x="400" y="430" font-family="Cairo" font-size="10" fill="gray">Rayane Tailor Elite - Technical Pattern</text></svg>"""
    st.components.v1.html(svg_code, height=460)
    st.download_button(cur_t["print_pat"], data=svg_code, file_name="Rayane_Pattern.svg", mime="image/svg+xml")

with st.expander(cur_t["step4"]):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        f_name = st.selectbox("نوع القماش المختارة:", ["قطيفة", "حرير", "كتان", "كريب", "ستان", "قماش السهرة"])
        f_price = st.number_input("سعر المتر (DA):", 800)
    with f_col2:
        m_needed = (total_l + arm_l + 25) / 100
        if cut == "كلوش": m_needed *= 2.0
        elif cut == "دوبل كلوش": m_needed *= 4.0
        st.metric("كمية القماش المطلوبة", f"{m_needed:.2f} m")
    acc = st.text_area("لوازم الخياطة المطلوبة:", "Matching Thread, Luxury Buttons, Zippers...")

# الخطوة 5: الفاتورة والربط السحابي المزدوج (قراءة وكتابة)
with st.expander(cur_t["step5"]):
    mat_cost = m_needed * f_price
    labor = st.number_input("تكلفة التفصيل واليد (DA):", 2500)
    total_bill = mat_cost + labor
    
    invoice_html = f"""<div class="invoice-card" style="direction:ltr;"><h1 style="text-align:center; color:#2D0B5A; margin:0;">RAYANE TAILOR ELITE</h1><p style="text-align:center; font-style:italic; border-bottom:1px solid #D4AF37; padding-bottom:10px;">Luxury Custom Tailoring</p><table style="width:100%; margin-top:20px; font-family:sans-serif;"><tr><td style="padding:10px;"><b>Category:</b></td><td>{category} ({cut})</td></tr><tr><td style="padding:10px;"><b>Fabric Type:</b></td><td>{f_name} ({m_needed:.2f} meters)</td></tr><tr><td style="padding:10px;"><b>Materials Cost:</b></td><td>{mat_cost:.2f} DA</td></tr><tr><td style="padding:10px;"><b>Tailoring Labor:</b></td><td>{labor:.2f} DA</td></tr><tr style="background:#2D0B5A; color:white;"><td style="padding:15px;"><b>TOTAL AMOUNT:</b></td><td style="padding:15px;"><b>{total_bill:.2f} DA</b></td></tr></table></div>"""
    st.markdown(invoice_html, unsafe_allow_html=True)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button(cur_t["save_cloud"]):
            new_data = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Client": gender, "Category": category, "Cut": cut,
                "Neck": neck, "Shoulder": shoulder, "Armhole": armhole, "Bust": bust,
                "W1": w1, "W2": w2, "W3": w3, "Total Length": total_l,
                "Fabric": f_name, "Meters": m_needed, "Total DA": total_bill
            }
            if conn:
                try:
                    existing_data = conn.read(spreadsheet=st.session_state.url)
                    updated_df = pd.concat([existing_data, pd.DataFrame([new_data])], ignore_index=True)
                    conn.update(spreadsheet=st.session_state.url, data=updated_df)
                    st.success("✅ تم التزامن والحفظ في الجدول فوراً!")
                except Exception as e:
                    st.error(f"⚠️ خطأ في الاتصال السحابي: {e}")
            else:
                st.warning("يرجى إعداد st.connection في ملف الأسرار للربط الفعلي.")

    with c2:
        if st.button(cur_t["load_cloud"]):
            if conn:
                try:
                    cloud_data = conn.read(spreadsheet=st.session_state.url)
                    st.markdown("#### 📜 سجل العمليات الأخير:")
                    st.dataframe(cloud_data.tail(5))
                except Exception as e:
                    st.error(f"⚠️ تعذر استيراد البيانات: {e}")
            else:
                st.info("الجدول فارغ أو غير مرتبط.")

    st.download_button(cur_t["print_inv"], data=invoice_html, file_name="Rayane_Invoice.html", mime="text/html")
    phone = st.text_input("رقم واتساب العميل (Ex: 213...):")
    if st.button(cur_t["wa_send"]):
        msg = urllib.parse.quote(f"Rayane Tailor Elite Atelier\nFinal Invoice Details:\nTotal Amount: {total_bill} DA")
        st.markdown(f'<a href="https://wa.me/{phone}?text={msg}" target="_blank">Confirm and Send via WhatsApp</a>', unsafe_allow_html=True)

st.caption("Rayane Tailor Elite Atelier - Bespoke Couture System 2026")

Le mar. 10 févr. 2026 à 14:23, rayane ranoch <rayaneranoch525@gmail.com> a écrit :
import streamlit as st
import pandas as pd
import qrcode
import urllib.parse
from io import BytesIO
import base64
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 1. Configuration & Ultra-Modern CSS
st.set_page_config(page_title="Rayane Tailor Elite Pro", layout="wide", initial_sidebar_state="collapsed")

# نظام الترجمة
t = {
    "العربية": {
        "title": "أتيليه Rayane Tailor Elite",
        "subtitle": "إبداع الأنامل في عالم التفصيل الراقي",
        "step1": "🖼️ المعرض: مصدر الإلهام والموديل",
        "step2": "👥 العميل: تحديد نوع القصة والزبون",
        "step3": "📏 الورشة: هندسة المقاسات والباترون",
        "step4": "🧪 التجهيز: حاسبة الأقمشة واللوازم",
        "step5": "🧾 الحساب: الفاتورة النهائية والربط السحابي",
        "upload_btn": "رفع صورة التصميم (من الجهاز أو المتصفح)",
        "gender": "جنس الزبون",
        "style": "تصنيف اللباس",
        "cut": "نوع القصة (الخراطة)",
        "calc_btn": "حساب متطلبات الورشة",
        "print_pat": "تحميل وطباعة الباترون الهندسي",
        "print_inv": "تحميل وطباعة الفاتورة الفاخرة",
        "wa_send": "إرسال الفاتورة عبر الواتساب",
        "lang_label": "تغيير اللغة / Switch Language",
        "trad": "لباس تقليدي جزائري",
        "size_preset": "تطبيق مقاس عالمي جاهز",
        "save_cloud": "💾 حفظ وإرسال للجدول السحابي",
        "load_cloud": "🔄 استيراد آخر البيانات من الجدول"
    },
    "English": {
        "title": "Rayane Tailor Elite Atelier",
        "subtitle": "Bespoke Elegance & High-End Couture",
        "step1": "🖼️ Gallery: Design & Inspiration",
        "step2": "👥 Client: Profile & Style Selection",
        "step3": "📏 Workshop: Measurement Engineering",
        "step4": "🧪 Preparation: Fabric & Supplies Calc",
        "step5": "🧾 Billing: Final Luxury Invoice & Cloud Sync",
        "upload_btn": "Upload Design Sketch (Device or Web)",
        "gender": "Client Gender",
        "style": "Garment Category",
        "cut": "Cut Type",
        "calc_btn": "Calculate Workshop Needs",
        "print_pat": "Download & Print Technical Pattern",
        "print_inv": "Download & Print Luxury Invoice",
        "wa_send": "Send Invoice via WhatsApp",
        "lang_label": "Switch Language / تغيير اللغة",
        "trad": "Algerian Traditional",
        "size_preset": "Apply International Size Preset",
        "save_cloud": "💾 Save & Sync to Cloud Sheet",
        "load_cloud": "🔄 Load Latest Data from Sheet"
    }
}

size_charts = {
    "S": {"neck": 34, "shoulder": 38, "armhole": 22, "bust": 88, "w1": 68, "w2": 72, "w3": 92, "width": 95, "total": 140, "sleeve": 58, "arm_c": 30},
    "M": {"neck": 36, "shoulder": 40, "armhole": 24, "bust": 96, "w1": 76, "w2": 80, "w3": 100, "width": 105, "total": 142, "sleeve": 59, "arm_c": 32},
    "L": {"neck": 38, "shoulder": 42, "armhole": 26, "bust": 104, "w1": 84, "w2": 88, "w3": 108, "width": 115, "total": 145, "sleeve": 60, "arm_c": 34},
    "XL": {"neck": 40, "shoulder": 44, "armhole": 28, "bust": 112, "w1": 92, "w2": 96, "w3": 116, "width": 125, "total": 148, "sleeve": 61, "arm_c": 36}
}

# CSS الملكي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
    .stApp { background-color: #fcfaf7; background-image: url("https://www.transparenttextures.com/patterns/pinstriped-suit.png"); }
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .header-style {
        background: linear-gradient(135deg, #2D0B5A 0%, #4B0D85 100%);
        padding: 50px; border-radius: 0px 0px 50px 50px; color: white; text-align: center;
        border-bottom: 8px solid #D4AF37; box-shadow: 0 15px 35px rgba(0,0,0,0.3); margin-bottom: 40px;
        position: relative; overflow: hidden;
    }
    .header-style::after { content: "✂️"; position: absolute; right: 20px; bottom: 10px; opacity: 0.2; font-size: 80px; transform: rotate(-20deg); }
    .stExpander { background-color: white !important; border: 1px solid #e0e0e0 !important; border-right: 5px solid #D4AF37 !important; border-radius: 15px !important; margin-bottom: 15px !important; }
    .stButton>button { 
        background: linear-gradient(to right, #2D0B5A, #4B0D85); 
        color: white; border-radius: 25px; border: 2px solid #D4AF37; 
        padding: 12px 25px; font-weight: bold; transition: 0.4s; width: 100%;
    }
    .stButton>button:hover { background: #D4AF37; color: #2D0B5A; transform: translateY(-3px); }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; }
    .invoice-card { background: #fff; border: 2px solid #D4AF37; padding: 40px; border-radius: 10px; background-image: url("https://www.transparenttextures.com/patterns/paper-fibers.png"); }
    </style>
    """, unsafe_allow_html=True)

# 2. Secure Authentication & Sheet Connection
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div class="header-style"><h2>🔐 Rayane Tailor Elite</h2><p>Exclusive Fashion Access</p></div>', unsafe_allow_html=True)
        pwd = st.text_input("License Key", type="password")
        sheet_url = st.text_input("Google Sheets URL")
        if st.button("Authorize Access"):
            if pwd == "Rano 2912" and "docs" in sheet_url:
                st.session_state.auth, st.session_state.url = True, sheet_url
                st.rerun()
    st.stop()

# إنشاء اتصال حقيقي بجدول بيانات جوجل
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

# 3. Sidebar Settings
with st.sidebar:
    st.markdown("### 🧵 Atelier Settings")
    sel_lang = st.selectbox("Language / اللغة", ["العربية", "English"])
    cur_t = t[sel_lang]
    st.markdown("---")
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

# 4. Main Dashboard Header
st.markdown(f'<div class="header-style"><h1>{cur_t["title"]}</h1><p style="font-style: italic; font-size: 1.2rem;">{cur_t["subtitle"]}</p></div>', unsafe_allow_html=True)

# الخطوات 1-4 (نفس الكود الأصلي تماماً دون حذف أي حرف)
with st.expander(cur_t["step1"], expanded=True):
    img_file = st.file_uploader(cur_t["upload_btn"], type=['png', 'jpg', 'jpeg'])
    if img_file: 
        st.markdown("#### 👗 التصميم المختار:")
        st.image(img_file, width=400)

with st.expander(cur_t["step2"]):
    c1, c2, c3 = st.columns(3)
    with c1: gender = st.radio(cur_t["gender"], ["رجل/Man", "امرأة/Woman", "طفل/Boy", "طفلة/Girl"])
    with c2:
        category = st.selectbox(cur_t["style"], ["كاجوال/Casual", "رسمي/Formal", "سواري/Soirée", cur_t["trad"]])
        trad_style = ""
        if category == cur_t["trad"]: trad_style = st.selectbox("Type:", ["كاراكو", "قفطان", "قندورة", "زدف سطايفي", "الشدة", "جابادور"])
    with c3: cut = st.selectbox(cur_t["cut"], ["سوغطاي", "ايفازي", "كلوش", "دوبل كلوش"])

with st.expander(cur_t["step3"]):
    st.markdown("#### 📏 لوحة القياسات الدقيقة")
    preset = st.radio(cur_t['size_preset'], ["Manual/يدوي", "S", "M", "L", "XL"], horizontal=True)
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
    details = st.multiselect("الإضافات الفنية:", ["كشكشة/Fronces", "طيات/Plis", "بانسات الصدر", "بانسات الظهر", "لاديكوب برانساس"])
    svg_code = f"""<svg width="600" height="450" viewBox="0 0 600 450" xmlns="http://www.w3.org/2000/svg"><rect width="100%" height="100%" fill="#fff" stroke="#2D0B5A" stroke-width="2" stroke-dasharray="10,5"/><path d="M 100,30 L 250,30 L 280,120 L 240,400 L 100,400 Z" fill="#f9f3ff" stroke="#4B0D85" stroke-width="2"/><text x="110" y="25" font-family="Cairo" font-size="12" fill="#2D0B5A" font-weight="bold">Shoulder: {shoulder}cm</text><text x="110" y="140" font-family="Cairo" font-size="12">Bust: {bust}cm</text><text x="110" y="220" font-family="Cairo" font-size="12">Waist (Mid): {w2}cm</text><text x="110" y="380" font-family="Cairo" font-size="12" fill="red">Total: {total_l}cm</text><circle cx="280" cy="120" r="4" fill="#D4AF37"/><text x="400" y="430" font-family="Cairo" font-size="10" fill="gray">Rayane Tailor Elite - Technical Pattern</text></svg>"""
    st.components.v1.html(svg_code, height=460)
    st.download_button(cur_t["print_pat"], data=svg_code, file_name="Rayane_Pattern.svg", mime="image/svg+xml")

with st.expander(cur_t["step4"]):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        f_name = st.selectbox("نوع القماش المختارة:", ["قطيفة", "حرير", "كتان", "كريب", "ستان", "قماش السهرة"])
        f_price = st.number_input("سعر المتر (DA):", 800)
    with f_col2:
        m_needed = (total_l + arm_l + 25) / 100
        if cut == "كلوش": m_needed *= 2.0
        elif cut == "دوبل كلوش": m_needed *= 4.0
        st.metric("كمية القماش المطلوبة", f"{m_needed:.2f} m")
    acc = st.text_area("لوازم الخياطة المطلوبة:", "Matching Thread, Luxury Buttons, Zippers...")

# الخطوة 5: الفاتورة والربط السحابي المزدوج (قراءة وكتابة)
with st.expander(cur_t["step5"]):
    mat_cost = m_needed * f_price
    labor = st.number_input("تكلفة التفصيل واليد (DA):", 2500)
    total_bill = mat_cost + labor
    
    invoice_html = f"""<div class="invoice-card" style="direction:ltr;"><h1 style="text-align:center; color:#2D0B5A; margin:0;">RAYANE TAILOR ELITE</h1><p style="text-align:center; font-style:italic; border-bottom:1px solid #D4AF37; padding-bottom:10px;">Luxury Custom Tailoring</p><table style="width:100%; margin-top:20px; font-family:sans-serif;"><tr><td style="padding:10px;"><b>Category:</b></td><td>{category} ({cut})</td></tr><tr><td style="padding:10px;"><b>Fabric Type:</b></td><td>{f_name} ({m_needed:.2f} meters)</td></tr><tr><td style="padding:10px;"><b>Materials Cost:</b></td><td>{mat_cost:.2f} DA</td></tr><tr><td style="padding:10px;"><b>Tailoring Labor:</b></td><td>{labor:.2f} DA</td></tr><tr style="background:#2D0B5A; color:white;"><td style="padding:15px;"><b>TOTAL AMOUNT:</b></td><td style="padding:15px;"><b>{total_bill:.2f} DA</b></td></tr></table></div>"""
    st.markdown(invoice_html, unsafe_allow_html=True)
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        # وظيفة الحفظ (إرسال للجدول)
        if st.button(cur_t["save_cloud"]):
            new_data = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Client": gender, "Category": category, "Cut": cut,
                "Neck": neck, "Shoulder": shoulder, "Armhole": armhole, "Bust": bust,
                "W1": w1, "W2": w2, "W3": w3, "Total Length": total_l,
                "Fabric": f_name, "Meters": m_needed, "Total DA": total_bill
            }
            if conn:
                existing_data = conn.read(spreadsheet=st.session_state.url, usecols=list(range(15)))
                updated_df = pd.concat([existing_data, pd.DataFrame([new_data])], ignore_index=True)
                conn.update(spreadsheet=st.session_state.url, data=updated_df)
                st.success("✅ تم التزامن والحفظ في الجدول فوراً!")
            else:
                st.warning("يرجى إعداد st.connection في ملف الأسرار للربط الفعلي.")

    with c2:
        # وظيفة الاستيراد (قراءة من الجدول)
        if st.button(cur_t["load_cloud"]):
            if conn:
                cloud_data = conn.read(spreadsheet=st.session_state.url)
                st.markdown("#### 📜 سجل العمليات الأخير:")
                st.dataframe(cloud_data.tail(5)) # عرض آخر 5 عمليات
            else:
                st.info("الجدول فارغ أو غير مرتبط.")

    st.download_button(cur_t["print_inv"], data=invoice_html, file_name="Rayane_Invoice.html", mime="text/html")
    phone = st.text_input("رقم واتساب العميل (Ex: 213...):")
    if st.button(cur_t["wa_send"]):
        msg = urllib.parse.quote(f"Rayane Tailor Elite Atelier\nFinal Invoice Details:\nTotal Amount: {total_bill} DA")
        st.markdown(f'<a href="https://wa.me/{phone}?text={msg}" target="_blank">Confirm and Send via WhatsApp</a>', unsafe_allow_html=True)

st.caption("Rayane Tailor Elite Atelier - Bespoke Couture System 2026")

Le mar. 10 févr. 2026 à 12:54, rayane ranoch <rayaneranoch525@gmail.com> a écrit :
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
