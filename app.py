import streamlit as st
import pandas as pd
import re
import math
from datetime import datetime, date
import urllib.parse

# 1. إعدادات الصفحة
st.set_page_config(page_title="Rayane Tailor Elite Business Pro", layout="wide")

# --- نظام تسجيل الدخول ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def check_login(key, sheet_url):
    if key == "Rano 2912" and "docs.google.com" in sheet_url:
        st.session_state['authenticated'] = True
        st.session_state['user_url'] = sheet_url
        return True
    return False

if not st.session_state['authenticated']:
    st.markdown("""<style> .login-box { background: white; padding: 2.5rem; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); border-top: 5px solid #6A0DAD; text-align: center; } </style>""", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3069/3069154.png", width=80)
        st.header("🔑 دخول نظام Rayane Tailor")
        license_key = st.text_input("مفتاح الترخيص", type="password")
        user_sheet = st.text_input("رابط Google Sheet CSV")
        if st.button("دخول"):
            if check_login(license_key, user_sheet):
                st.rerun()
            else:
                st.error("المعلومات غير صحيحة.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- جلب البيانات ---
csv_url = st.session_state['user_url']

@st.cache_data(ttl=60)
def load_data(url):
    try:
        data = pd.read_csv(url)
        data.columns = [col.strip() for col in data.columns]
        # محاولة تحويل عمود التاريخ لتاريخ حقيقي للتنبيهات
        for col in data.columns:
            if "موعد" in col or "delivery" in col.lower():
                data[col] = pd.to_datetime(data[col], errors='coerce')
        return data
    except: return None

# --- الوظائف المساعدة ---
def fix_google_drive_link(url):
    if pd.isna(url): return None
    url = str(url)
    if 'drive.google.com' in url:
        match = re.search(r'id=([a-zA-Z0-9_-]+)', url) or re.search(r'file/d/([a-zA-Z0-9_-]+)', url)
        if match: return f'https://drive.google.com/uc?id={match.group(1)}'
    return url

def get_status_color(delivery_date):
    if pd.isna(delivery_date): return "#eee"
    days_left = (delivery_date.date() - date.today()).days
    if days_left < 0: return "#ff4b4b" # متأخر (أحمر)
    if days_left <= 2: return "#ffa500" # قريب جداً (برتقالي)
    return "#28a745" # وقت كافٍ (أخضر)

# --- اللغات ---
lang = st.sidebar.selectbox("🌐 Language / اللغة", ["العربية", "Français", "English"])
t = {
    "العربية": {
        "title": "🧵 Rayane Tailor Elite Pro", "tab_form": "➕ إضافة طلبية", 
        "tab1": "📊 سجل المواعيد والأرباح", "tab2": "📐 الباترون والمالية",
        "search": "🔍 بحث...", "delivery": "موعد التسليم", "total_price": "السعر النهائي",
        "wa_btn": "📱 إرسال فاتورة واتساب", "stats": "📈 إحصائيات الشهر", "profit": "صافي الربح المتوقع"
    },
    "Français": {
        "title": "🧵 Rayane Tailor Elite Pro", "tab_form": "➕ Ajouter", 
        "tab1": "📊 Registre & Finance", "tab2": "📐 Patronage",
        "search": "🔍 Chercher...", "delivery": "Livraison", "total_price": "Prix Final",
        "wa_btn": "📱 Facture WhatsApp", "stats": "📈 Stats du Mois", "profit": "Bénéfice Net"
    }
}
txt = t.get(lang, t["العربية"])

# التنسيق البصري
st.markdown(f'<div style="background: linear-gradient(135deg, #4B0082, #6A0DAD); padding: 20px; color: white; border-radius: 15px; text-align: center; border-bottom: 5px solid #FFD700;"><h1>{txt["title"]}</h1></div>', unsafe_allow_html=True)

tab0, tab1, tab2 = st.tabs([txt["tab_form"], txt["tab1"], txt["tab2"]])

with tab0:
    st.info("أدخلي بيانات الزبونة في استمارتك الخاصة.")
    st.markdown("[🔗 افتح استمارة Google Forms](https://docs.google.com/forms/)")

with tab1:
    df = load_data(csv_url)
    if df is not None:
        # --- ميزة كشف الأرباح الشهرية ---
        st.subheader(txt["stats"])
        # البحث عن أعمدة السعر (نفترض وجود عمود فيه كلمة 'سعر' أو 'Price' أو 'حق يدك')
        price_col = next((c for c in df.columns if any(x in c for x in ["سعر", "Price", "حق يدك"])), None)
        if price_col:
            df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
            monthly_profit = df.iloc[-30:][price_col].sum() # آخر 30 طلبية كمثال
            st.metric(label=txt["profit"], value=f"{monthly_profit:,.2f} DA")
        
        st.divider()
        query = st.text_input(txt["search"])
        if query: df = df[df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]
        
        for idx, row in df[::-1].iterrows():
            d_date = row.get("موعد التسليم") or row.get("Delivery Date")
            color = get_status_color(d_date)
            
            with st.expander(f"👤 {row.iloc[1]} | 📅 {txt['delivery']}: {d_date.date() if not pd.isna(d_date) else '---'}"):
                st.markdown(f'<div style="width: 100%; height: 5px; background: {color}; border-radius: 5px; margin-bottom: 10px;"></div>', unsafe_allow_html=True)
                c1, c2 = st.columns([1, 2])
                with c1:
                    img = fix_google_drive_link(next((row[c] for c in df.columns if any(x in c for x in ["صورة", "رابط"])), None))
                    if img: st.image(img)
                with c2:
                    # عرض البيانات
                    for c in df.columns[1:6]: st.write(f"**{c}:** {row[c]}")
                    
                    # --- زر إرسال فاتورة واتساب ---
                    client_name = row.iloc[1]
                    price = row[price_col] if price_col else "0"
                    phone = next((row[c] for c in df.columns if "هاتف" in c or "Phone" in c), "")
                    msg = f"مرحباً {client_name}، فستانك جاهز في ورشة Rayane Tailor. المبلغ الإجمالي: {price} DA. شكراً لثقتكِ بنا!"
                    wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; padding:10px; border-radius:10px; text-align:center;">{txt["wa_btn"]}</div></a>', unsafe_allow_html=True)

with tab2:
    # --- محرك الباترون (نفس الكود السابق مع الاحتفاظ بالقيم المسحوبة آلياً) ---
    df = load_data(csv_url)
    st.header(txt["auto_pull"])
    s_bust, s_waist, s_len, s_shoulder = 90.0, 70.0, 140.0, 40.0
    if df is not None:
        choice = st.selectbox("اختر الزبونة:", ["---"] + df.iloc[:, 1].tolist())
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
        st.subheader("📐 هندسة الباترون")
        b_v = st.number_input("الصدر", value=float(s_bust))
        w_v = st.number_input("الخصر", value=float(s_waist))
        l_v = st.number_input("الطول", value=float(s_len))
        s_v = st.number_input("الكتف", value=float(s_shoulder))
        dart = st.slider("عمق البنسة", 0, 30, 10)
        flare = st.slider("درجة التوسيع (Flare)", 0, 100, 20)
        
        # رسم الباترون
        svg = f"""<svg width="400" height="600" viewBox="0 0 500 800" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="white" />
            <path d="M 100,50 L {100+s_v*2},50 L {100+b_v},200 L {100+b_v-dart},250 L {100+w_v},400 L {100+w_v+flare*2},{l_v*4} L 100,{l_v*4} Z" fill="none" stroke="black" stroke-width="3"/>
            <text x="20" y="780" font-size="12" fill="gray">Rayane Tailor Elite - Professional Pattern</text>
        </svg>"""
        if st.button("توليد الباترون"):
            st.components.v1.html(svg, height=500)
            st.download_button("📥 تحميل الباترون", svg, "pattern.svg", "image/svg+xml")

    with cp2:
        st.subheader("💰 حساب التكلفة")
        f_p = st.number_input("سعر القماش", 0)
        a_p = st.number_input("سعر الإكسسوارات", 0)
        l_p = st.number_input("حق يدكِ", 1500)
        st.success(f"الإجمالي: {f_p + a_p + l_p:,.2f} DA")
        st.write(f"📏 القماش المطلوب: **{(l_v + 40 + flare/2)/100:.2f} متر**")

st.sidebar.button("تسجيل الخروج", on_click=lambda: st.session_state.update({"authenticated": False}))
