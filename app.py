import streamlit as st
import pandas as pd
import re
import math
from datetime import datetime, date
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="Rayane Tailor Elite", page_icon="🧵", layout="wide")

# --- تحسينات التصميم (CSS) للراحة البصرية الكاملة ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        text-align: right;
    }
    
    .main { background-color: #f8f9fa; }
    
    /* تصميم الهيدر الملكي الخاص بكِ فقط */
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
    
    /* تنسيق البطاقات */
    .stExpander {
        border-radius: 15px !important;
        border: 1px solid #e0e0e0 !important;
        background: white !important;
        margin-bottom: 10px !important;
    }
    
    /* أزرار التواصل */
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

    /* إخفاء أي هوامش غير ضرورية */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- نظام تسجيل الدخول ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def check_login(key, sheet_url):
    if key == "Rano 2912" and ("docs.google.com" in sheet_url or "googleusercontent" in sheet_url):
        st.session_state['authenticated'] = True
        st.session_state['user_url'] = sheet_url
        return True
    return False

if not st.session_state['authenticated']:
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'''
            <div style="background: white; padding: 30px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 5px solid #2D0B5A; text-align: center;">
                <h2 style="color: #2D0B5A;">🔓 نظام Rayane Tailor</h2>
                <p style="color: #666;">يرجى إدخال بيانات الوصول للوحة التحكم</p>
            </div>
        ''', unsafe_allow_html=True)
        license_key = st.text_input("مفتاح الترخيص", type="password")
        user_sheet = st.text_input("رابط Google Sheet CSV")
        if st.button("دخول آمن", use_container_width=True):
            if check_login(license_key, user_sheet):
                st.rerun()
            else:
                st.error("المعلومات غير صحيحة.")
    st.stop()

# --- جلب ومعالجة البيانات ---
@st.cache_data(ttl=60)
def load_data(url):
    try:
        if "edit" in url:
            url = url.replace("edit#gid=", "export?format=csv&gid=")
            url = re.sub(r"edit\?.*", "export?format=csv", url)
        
        data = pd.read_csv(url)
        data.columns = [col.strip() for col in data.columns]
        for col in data.columns:
            if any(x in col.lower() for x in ["موعد", "delivery", "date", "تاريخ"]):
                data[col] = pd.to_datetime(data[col], errors='coerce')
        return data
    except Exception as e:
        st.error(f"خطأ في جلب البيانات: {e}")
        return None

def fix_google_drive_link(url):
    if pd.isna(url): return None
    url = str(url)
    if 'drive.google.com' in url:
        match = re.search(r'id=([a-zA-Z0-9_-]+)', url) or re.search(r'file/d/([a-zA-Z0-9_-]+)', url)
        if match: return f'https://drive.google.com/uc?id={match.group(1)}'
    return url

def get_status_color(delivery_date):
    if pd.isna(delivery_date): return "#eee"
    try:
        days_left = (delivery_date.date() - date.today()).days
        if days_left < 0: return "#ff4b4b" 
        if days_left <= 2: return "#ffa500" 
        return "#28a745"
    except: return "#eee"

# --- الواجهة البرمجية ---
lang = st.sidebar.selectbox("🌐 اللغة", ["العربية", "Français"])
t = {
    "العربية": {
        "title": "Rayane Tailor Elite", "tab_form": "➕ إضافة", 
        "tab1": "📊 السجل المالي", "tab2": "📐 الباترون والقص",
        "search": "🔍 بحث...", "delivery": "موعد التسليم", "profit": "إجمالي الأرباح"
    }
}
txt = t.get(lang, t["العربية"])

# --- الهيدر الاحترافي (بدون أي علامات خارجية) ---
st.markdown(f'''
    <div class="header-box">
        <h1 style="margin:0; font-size: 2.5rem; letter-spacing: 1px;">{txt["title"]}</h1>
        <p style="opacity: 0.9; margin-top: 10px; font-weight: 300;">Management & Design Elite System</p>
    </div>
''', unsafe_allow_html=True)

tab0, tab1, tab2 = st.tabs([txt["tab_form"], txt["tab1"], txt["tab2"]])

with tab0:
    st.info("💡 قومي بتعبئة بيانات الزبونة عبر الاستمارة المربوطة.")
    st.link_button("فتح استمارة الإدخال", "https://docs.google.com/forms/", use_container_width=True)

with tab1:
    df = load_data(st.session_state['user_url'])
    if df is not None:
        price_col = next((c for c in df.columns if any(x in c for x in ["سعر", "Price", "حق يدك"])), None)
        if price_col:
            df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
            st.metric(label=txt["profit"], value=f"{df[price_col].sum():,.0f} DA")
        
        query = st.text_input(txt["search"])
        if query: 
            df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]
        
        for idx, row in df[::-1].iterrows():
            d_date = row.get("موعد التسليم") or row.get("Delivery Date")
            color = get_status_color(d_date)
            with st.expander(f"👤 {row.iloc[1]} | 📅 {d_date.date() if hasattr(d_date, 'date') else '---'}"):
                st.markdown(f'<div style="height:5px; background:{color}; border-radius:10px; margin-bottom:15px;"></div>', unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    img = fix_google_drive_link(next((row[c] for c in df.columns if any(x in c for x in ["صورة", "رابط"])), None))
                    if img: st.image(img, use_container_width=True)
                with c2:
                    for c in df.columns[1:6]: st.write(f"**{c}:** {row[c]}")
                    phone = next((row[c] for c in df.columns if any(x in c for x in ["هاتف", "Phone"])), "")
                    wa_url = f"https://wa.me/{phone}?text=مرحباً {row.iloc[1]}، فستانك جاهز لدى Rayane Tailor."
                    st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-button">📱 إرسال واتساب</a>', unsafe_allow_html=True)

with tab2:
    st.subheader("📐 هندسة المقاسات والباترون")
    df = load_data(st.session_state['user_url'])
    s_bust, s_waist, s_len, s_shoulder = 90.0, 70.0, 140.0, 40.0
    
    if df is not None:
        choice = st.selectbox("سحب مقاسات الزبونة:", ["---"] + df.iloc[:, 1].tolist())
        if choice != "---":
            c_data = df[df.iloc[:, 1] == choice].iloc[0]
            for col in df.columns:
                val = pd.to_numeric(c_data[col], errors='coerce
