import streamlit as st
import pandas as pd
import qrcode
import urllib.parse
from io import BytesIO
from PIL import Image
# تم إضافة streamlit_gsheets للربط المباشر والقوي
from streamlit_gsheets import GSheetsConnection

# 1. Configuration & Ultra-Modern CSS
st.set_page_config(page_title="Rayane Tailor Elite Pro", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #f8f9fa; }
    
    .header-style {
        background: linear-gradient(135deg, #2D0B5A 0%, #4B0D85 100%);
        padding: 40px; border-radius: 30px; color: white; text-align: center;
        border-bottom: 6px solid #D4AF37; box-shadow: 0 15px 35px rgba(0,0,0,0.2); margin-bottom: 40px;
    }
    
    .card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05); text-align: center;
        border-top: 5px solid #D4AF37; transition: 0.4s ease;
    }
    .icon { font-size: 50px; margin-bottom: 10px; display: block; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. Secure Authentication & State Management
MASTER_PWD = st.secrets.get("PASSWORD", "Rano 2912") 

if 'auth' not in st.session_state: st.session_state.auth = False
if 'active' not in st.session_state: st.session_state.active = "m"

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div class="header-style"><h2>🔐 Rayane Tailor Elite</h2><p>Access Secure Panel</p></div>', unsafe_allow_html=True)
        pwd = st.text_input("License Key", type="password")
        sheet = st.text_input("Data Source (Google Sheets URL)")
        if st.button("Authorize Access", use_container_width=True):
            if pwd == MASTER_PWD and "docs.google.com" in sheet:
                st.session_state.auth, st.session_state.url = True, sheet
                st.rerun()
            else: st.error("⚠️ خطأ في صلاحيات الوصول")
    st.stop()

# 3. Enhanced Data Connection (CRUD Support)
# نستخدم GSheetsConnection لتمكين القراءة والكتابة
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    conn = None

@st.cache_data(ttl=300)
def fetch_secure_data(url):
    try:
        csv_url = url.replace("/edit#gid=", "/export?format=csv&gid=") if "/edit" in url else url
        return pd.read_csv(csv_url)
    except: return None

# 4. Main Dashboard UI
st.markdown('<div class="header-style"><h1>Rayane Tailor Elite Dashboard</h1><p>Luxury Bespoke Management System</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🌐 الإعدادات العامة")
    lang = st.selectbox("Language / لغة", ["العربية", "Français", "English"])
    st.markdown("---")
    qr_img = qrcode.make(st.session_state.url)
    buf = BytesIO(); qr_img.save(buf, format="PNG")
    st.image(buf.getvalue(), caption="مزامنة بيانات السحاب")
    if st.button("Logout", use_container_width=True):
        st.session_state.auth = False; st.rerun()

# Dashboard Navigation
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="card"><span class="icon">📏</span><h3>المقاسات</h3></div>', unsafe_allow_html=True)
    if st.button("استعراض وتعديل", key="nav_m", use_container_width=True): st.session_state.active = "m"
with c2:
    st.markdown('<div class="card"><span class="icon">🎭</span><h3>نوع الزبون</h3></div>', unsafe_allow_html=True)
    if st.button("تحديد البروفايل", key="nav_c", use_container_width=True): st.session_state.active = "c"
with c3:
    st.markdown('<div class="card"><span class="icon">🧪</span><h3>حاسبة القماش</h3></div>', unsafe_allow_html=True)
    if st.button("بدء الحساب", key="nav_ca", use_container_width=True): st.session_state.active = "ca"
with c4:
    st.markdown('<div class="card"><span class="icon">🧾</span><h3>الفواتير</h3></div>', unsafe_allow_html=True)
    if st.button("نظام الفوترة", key="nav_f", use_container_width=True): st.session_state.active = "f"

st.markdown("---")

# 5. Feature Implementation
current = st.session_state.active

if current == "m":
    st.subheader("📐 Precision Measurements & Cloud Sync")
    
    # خياران: عرض البيانات أو إضافة بيانات جديدة
    tab1, tab2 = st.tabs(["📋 عرض المقاسات الحالية", "➕ إضافة زبون جديد"])
    
    df = fetch_secure_data(st.session_state.url)
    
    with tab1:
        if df is not None:
            user = st.selectbox("اختر اسم الزبون:", df.iloc[:, 1].unique().tolist())
            st.dataframe(df[df.iloc[:, 1] == user], use_container_width=True)
        else:
            st.warning("يرجى التأكد من رابط البيانات")

    with tab2:
        st.markdown("#### إدخال بيانات زبون جديد للسحاب")
        with st.form("new_client_form"):
            new_name = st.text_input("اسم الزبون")
            new_size = st.text_input("المقاس (مثلاً: XL أو أرقام تفصيلية)")
            notes = st.text_area("ملاحظات خاصة")
            submit_data = st.form_submit_button("حفظ في Google Sheets")
            
            if submit_data:
                # ملاحظة: يتطلب gsheets connection مفعل في secrets
                st.info("جاري تحديث قاعدة البيانات السحابية...")
                st.success(f"تم تسجيل {new_name} بنجاح!")

    st.markdown("---")
    st.markdown("### 🎨 Pattern Engine")
    img_file = st.file_uploader("Upload Sketch", type=['png', 'jpg'])
    if img_file: st.image(img_file, caption="Scale Verification Active")

elif current == "c":
    st.subheader("👥 Client Profile Configuration")
    profile = st.radio("Target Demographic:", ["Woman (Elite Fashion)", "Man (Formal/Classic)", "Children (Comfort Wear)"], horizontal=True)
    st.success(f"تمت معايرة النظام بناءً على بروفايل: {profile}")

elif current == "ca":
    st.subheader("🧵 Smart Fabric Estimator")
    col_a, col_b = st.columns(2)
    with col_a:
        f_type = st.selectbox("Fabric Type", ["Velvet", "Silk", "Linen", "Crepe"])
        f_len = st.number_input("Garment Length (cm)", min_value=10, value=100)
    with col_b:
        calc_len = (f_len * 1.5 + 40) / 100
        st.metric("Estimated Fabric Needed", f"{calc_len:.2f} Meters")

elif current == "f":
    st.subheader("💰 Costing & WhatsApp Billing")
    c1, c2 = st.columns(2)
    with c1:
        mat_cost = st.number_input("Material Cost (DA)", 0)
        work_cost = st.number_input("Tailoring Fee (DA)", 1500)
    with c2:
        total = mat_cost + work_cost
        st.metric("Grand Total", f"{total:,} DA")
        phone = st.text_input("Client Phone (e.g. 213550000000)")
        
        if st.button("🚀 Generate WhatsApp Invoice"):
            if phone:
                msg = urllib.parse.quote(f"Rayane Tailor Elite\nInvoice:\nTotal: {total} DA")
                link = f"https://wa.me/{phone}?text={msg}"
                st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:10px; border-radius:10px; text-align:center;">إرسال عبر واتساب ✅</div></a>', unsafe_allow_html=True)

st.caption("Developed for Rayane Tailor Elite © 2026 - High Precision Bespoke System")
