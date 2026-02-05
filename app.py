import streamlit as st
import pandas as pd
import re
from datetime import datetime, date
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="Rayane Tailor Elite Business Pro", page_icon="🧵", layout="wide")

# --- تحسينات التصميم (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        text-align: right;
    }
    
    .main { background-color: #f8f9fa; }
    
    /* الهيدر الملكي */
    .header-box {
        background: linear-gradient(135deg, #2D0B5A 0%, #4B0D85 100%);
        padding: 35px;
        border-radius: 20px;
        color: white;
        text-align: center;
        border-bottom: 5px solid #D4AF37; 
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .stExpander {
        border-radius: 15px !important;
        border: 1px solid #e0e0e0 !important;
        background: white !important;
        margin-bottom: 10px !important;
    }
    
    .wa-button {
        background-color: #25D366;
        color: white;
        padding: 12px;
        border-radius: 12px;
        text-decoration: none;
        display: block;
        text-align: center;
        font-weight: bold;
        transition: 0.3s;
    }
    .wa-button:hover { background-color: #128C7E; color: white; }

    .login-box {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border-top: 5px solid #2D0B5A;
        text-align: center;
    }

    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- نظام تسجيل الدخول ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def check_login(key, sheet_url):
    # تقبل الروابط التي تحتوي على docs.google.com لضمان المرونة
    if key == "Rano 2912" and "docs.google.com" in sheet_url:
        st.session_state['authenticated'] = True
        st.session_state['user_url'] = sheet_url
        return True
    return False

if not st.session_state['authenticated']:
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3069/3069154.png", width=80)
        st.header("🔑 دخول نظام Rayane Tailor")
        license_key = st.text_input("مفتاح الترخيص", type="password")
        user_sheet = st.text_input("رابط Google Sheet CSV")
        if st.button("دخول آمن", use_container_width=True):
            if check_login(license_key, user_sheet):
                st.rerun()
            else:
                st.error("المعلومات غير صحيحة.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- جلب ومعالجة البيانات ---
@st.cache_data(ttl=60)
def load_data(url):
    try:
        # تحويل رابط الشيت إلى صيغة CSV تلقائياً
        if "edit" in url:
            url = url.replace("edit#gid=", "export?format=csv&gid=").split("?")[0] + "?format=csv"
        
        data = pd.read_csv(url)
        data.columns = [col.strip() for col in data.columns]
        for col in data.columns:
            if any(x in col.lower() for x in ["موعد", "تاريخ", "delivery"]):
                data[col] = pd.to_datetime(data[col], errors='coerce')
        return data
    except Exception as e:
        st.error(f"خطأ في الاتصال: {e}")
        return None

def fix_google_drive_link(url):
    if pd.isna(url): return None
    match = re.search(r'(id=|/d/)([a-zA-Z0-9_-]+)', str(url))
    if match: return f'https://drive.google.com/uc?id={match.group(2)}'
    return url

def get_status_color(delivery_date):
    if pd.isna(delivery_date): return "#eee"
    try:
        days_left = (delivery_date.date() - date.today()).days
        if days_left < 0: return "#ff4b4b" 
        if days_left <= 2: return "#ffa500" 
        return "#28a745"
    except: return "#eee"

# --- اللغات والترجمة ---
lang = st.sidebar.selectbox("🌐 اللغة / Language", ["العربية", "Français", "English"])
t = {
    "العربية": {
        "title": "Rayane Tailor Elite Pro", "tab0": "➕ إضافة طلبية", 
        "tab1": "📊 السجل والإحصائيات", "tab2": "📐 الباترون والمالية",
        "search": "🔍 بحث...", "profit": "صافي الأرباح المتوقعة", "wa_btn": "📱 إرسال فاتورة واتساب"
    },
    "Français": {
        "title": "Rayane Tailor Elite Pro", "tab0": "➕ Ajouter", 
        "tab1": "📊 Registre & Stats", "tab2": "📐 Patronage",
        "search": "🔍 Chercher...", "profit": "Bénéfice Net", "wa_btn": "📱 Facture WhatsApp"
    }
}
txt = t.get(lang, t["العربية"])

# --- الواجهة الرئيسية ---
st.markdown(f'''
    <div class="header-box">
        <h1>{txt["title"]}</h1>
        <p style="opacity: 0.9;">Professional Management & Design System</p>
    </div>
''', unsafe_allow_html=True)

tab0, tab1, tab2 = st.tabs([txt["tab0"], txt["tab1"], txt["tab2"]])

with tab0:
    st.info("💡 يتم إدخال البيانات عبر استمارة Google Forms الخاصة بكِ.")
    st.link_button("🔗 فتح استمارة الإدخال", "https://docs.google.com/forms/", use_container_width=True)

with tab1:
    df = load_data(st.session_state['user_url'])
    if df is not None:
        # الإحصائيات المالية
        price_col = next((c for c in df.columns if any(x in c for x in ["سعر", "Price", "حق يدك"])), None)
        if price_col:
            df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
            st.metric(label=txt["profit"], value=f"{df[price_col].sum():,.2f} DA")
        
        st.divider()
        query = st.text_input(txt["search"])
        if query: 
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]
        
        for idx, row in df[::-1].iterrows():
            d_date = row.get("موعد التسليم") or row.get("Delivery Date")
            color = get_status_color(d_date)
            with st.expander(f"👤 {row.iloc[1]} | 📅 {d_date.date() if hasattr(d_date, 'date') else '---'}"):
                st.markdown(f'<div style="height:5px; background:{color}; border-radius:10px; margin-bottom:10px;"></div>', unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    img = fix_google_drive_link(next((row[c] for c in df.columns if any(x in c for x in ["صورة", "رابط"])), None))
                    if img: st.image(img, use_container_width=True)
                with c2:
                    for c in df.columns[1:6]: st.write(f"**{c}:** {row[c]}")
                    phone = next((row[c] for c in df.columns if any(x in c for x in ["هاتف", "Phone"])), "")
                    msg = f"مرحباً {row.iloc[1]}، فستانك جاهز في ورشة Rayane Tailor."
                    wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-button">{txt["wa_btn"]}</a>', unsafe_allow_html=True)

with tab2:
    st.subheader("📐 هندسة الباترون والمحاسبة")
    df = load_data(st.session_state['user_url'])
    s_bust, s_waist, s_len, s_shoulder = 90.0, 70.0, 140.0, 40.0
    
    if df is not None:
        choice = st.selectbox("اختر الزبونة لسحب المقاسات:", ["---"] + df.iloc[:, 1].tolist())
        if choice != "---":
            c_data = df[df.iloc[:, 1] == choice].iloc[0]
            for col in df.columns:
                val = pd.to_numeric(c_data[col], errors='coerce')
                if not pd.isna(val):
                    if "صدر" in col: s_bust = val
                    if "خصر" in col: s_waist = val
                    if "طول" in col: s_len = val
                    if "كتف" in col: s_shoulder = val

    st.divider()
    cp1, cp2 = st.columns([1.2, 1])
    with cp1:
        b_v = st.number_input("الصدر", value=float(s_bust))
        w_v = st.number_input("الخصر", value=float(s_waist))
        l_v = st.number_input("الطول", value=float(s_len))
        s_v = st.number_input("الكتف", value=float(s_shoulder))
        dart = st.slider("عمق البنسة", 0, 30, 10)
        flare = st.slider("درجة التوسيع (Flare)", 0, 100, 20)
        
        # رسم الباترون الذكي
        svg = f"""<svg width="400" height="600" viewBox="0 0 500 800" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="white" />
            <path d="M 100,50 L {100+s_v*2},50 L {100+b_v},200 L {100+b_v-dart},250 L {100+w_v},400 L {100+w_v+flare*2},700 L 100,700 Z" fill="none" stroke="#2D0B5A" stroke-width="4"/>
            <text x="20" y="780" font-size="14" fill="#666">Rayane Tailor Elite - Professional Design</text>
        </svg>"""
        st.components.v1.html(svg, height=520)
        st.download_button("📥 تحميل الباترون (SVG)", svg, "pattern.svg")

    with cp2:
        st.markdown('<div style="background:#eee; padding:20px; border-radius:15px; border-right: 5px solid #D4AF37;"><h3>💰 حساب التكاليف</h3></div>', unsafe_allow_html=True)
        f_p = st.number_input("سعر القماش", 0)
        a_p = st.number_input("الإكسسوارات", 0)
        l_p = st.number_input("حق اليد (خياطة)", 1500)
        st.success(f"الإجمالي النهائي: {f_p + a_p + l_p:,.2f} DA")
        st.info(f"📏 القماش المطلوب: {(l_v + 50 + flare/2)/100:.2f} متر تقريباً")

st.sidebar.markdown("---")
st.sidebar.button("تسجيل الخروج", on_click=lambda: st.session_state.update({"authenticated": False}))
