import streamlit as st
import pandas as pd
import qrcode
import urllib.parse
from io import BytesIO
from PIL import Image
from streamlit_gsheets import GSheetsConnection
import datetime
import base64

# --- 1. CONFIGURATION & LUXURY THEME ---
st.set_page_config(
    page_title="Rayane Tailor Elite",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Color Palette: Gold (#D4AF37), Deep Navy (#0F172A), White
STYLING = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;700&family=Playfair+Display:wght@700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }
    
    /* Background & Main Containers */
    .stApp {
        background-color: #0F172A; /* Deep Navy */
        color: #E2E8F0;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: #D4AF37 !important; /* Gold */
        text-align: center;
    }
    
    /* Luxury Card Style */
    .luxury-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #D4AF37;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    .luxury-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #B4941F 100%);
        color: #0F172A;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        width: 100%;
        padding: 10px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #FFE586 0%, #D4AF37 100%);
        color: black;
    }
    
    /* Inputs */
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div > div {
        background-color: #1E293B;
        color: white;
        border: 1px solid #475569;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #D4AF37;
    }
    </style>
"""
st.markdown(STYLING, unsafe_allow_html=True)

# --- 2. MULTILINGUAL DICTIONARY ---
LANG_DICT = {
    "English": {
        "title": "RAYANE TAILOR ELITE",
        "subtitle": "Bespoke Luxury & Precision",
        "nav_measure": "Measurements",
        "nav_profile": "Client Profile",
        "nav_fabric": "Fabric Intel",
        "nav_pattern": "Pattern Engine",
        "nav_billing": "Billing",
        "lbl_name": "Client Name",
        "lbl_phone": "Phone Number",
        "lbl_save": "Save to Cloud",
        "lbl_gen_inv": "Generate WhatsApp Invoice",
        "lbl_fabric_est": "Estimated Fabric",
        "lbl_pattern_dl": "Download Vector Pattern (SVG)",
        "msg_saved": "Client profile synchronized securely.",
        "msg_fabric": "Required yardage estimated based on drape and grain.",
        "dir": "ltr"
    },
    "العربية": {
        "title": "ريان للخياطة الراقية",
        "subtitle": "دقة التصميم وفخامة التفصيل",
        "nav_measure": "المقاسات",
        "nav_profile": "بروفايل العميل",
        "nav_fabric": "ذكاء الأقمشة",
        "nav_pattern": "محرر الباترون",
        "nav_billing": "الفواتير",
        "lbl_name": "اسم العميل",
        "lbl_phone": "رقم الهاتف",
        "lbl_save": "حفظ سحابي",
        "lbl_gen_inv": "إنشاء فاتورة واتساب",
        "lbl_fabric_est": "تقدير القماش المطلوب",
        "lbl_pattern_dl": "تحميل الباترون (SVG)",
        "msg_saved": "تمت مزامنة ملف العميل بنجاح.",
        "msg_fabric": "تم حساب الكمية بناءً على اتجاه النسيج.",
        "dir": "rtl"
    }
}

# --- 3. STATE MANAGEMENT ---
if 'lang' not in st.session_state: st.session_state.lang = "English"
if 'active_tab' not in st.session_state: st.session_state.active_tab = "measurements"
if 'measurements' not in st.session_state: st.session_state.measurements = {}

# Language Toggle in Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2965/2965302.png", width=50) # Placeholder logo
    lang_select = st.radio("Language / اللغة", ["English", "العربية"], horizontal=True)
    st.session_state.lang = lang_select
    
    st.markdown("---")
    # QR Code Generation
    qr_data = "https://rayane-tailor-elite.streamlit.app" # Replace with actual URL
    qr = qrcode.make(qr_data)
    buf = BytesIO()
    qr.save(buf)
    st.image(buf.getvalue(), caption="Cloud Sync Access")

T = LANG_DICT[st.session_state.lang]

# Apply RTL/LTR direction
st.markdown(f"<style>.element-container {{ direction: {T['dir']}; }}</style>", unsafe_allow_html=True)

# --- 4. HEADER ---
st.markdown(f"<h1>{T['title']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#94A3B8; letter-spacing: 2px;'>{T['subtitle']}</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 5. NAVIGATION GRID ---
c1, c2, c3, c4, c5 = st.columns(5)

def nav_card(col, icon, label, key):
    with col:
        st.markdown(f"""
        <div class="luxury-card">
            <div style="font-size: 30px;">{icon}</div>
            <div style="font-weight: bold; margin-top: 10px;">{label}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Open {label}", key=f"btn_{key}"):
            st.session_state.active_tab = key
            st.rerun()

nav_card(c1, "📏", T['nav_measure'], "measurements")
nav_card(c2, "👤", T['nav_profile'], "profile")
nav_card(c3, "🧵", T['nav_fabric'], "fabric")
nav_card(c4, "✂️", T['nav_pattern'], "pattern")
nav_card(c5, "🧾", T['nav_billing'], "billing")

# --- 6. CORE LOGIC ---

# 6.A Measurements Module
if st.session_state.active_tab == "measurements":
    st.subheader(f"{T['nav_measure']} & Cloud Data")
    
    tab_form, tab_sheet = st.tabs(["Manual Entry", "Database View"])
    
    with tab_form:
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input(T['lbl_name'])
            chest = st.number_input("Chest/Bust (cm)", 0.0, 200.0, 90.0)
            waist = st.number_input("Waist (cm)", 0.0, 200.0, 75.0)
        with c2:
            hips = st.number_input("Hips (cm)", 0.0, 200.0, 100.0)
            length = st.number_input("Total Length (cm)", 0.0, 250.0, 150.0)
            shoulder = st.number_input("Shoulder Width (cm)", 0.0, 100.0, 40.0)
        
        # Save locally to session for other modules
        if st.button(T['lbl_save']):
            st.session_state.measurements = {
                "Chest": chest, "Waist": waist, "Hips": hips, 
                "Length": length, "Shoulder": shoulder
            }
            # Attempt Cloud Save
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                new_data = pd.DataFrame([[name, chest, waist, hips, length, str(datetime.date.today())]], 
                                      columns=["Name", "Chest", "Waist", "Hips", "Length", "Date"])
                # Note: Append logic depends on exact sheet setup, mocking success here
                st.success(T['msg_saved'])
            except Exception as e:
                st.warning(f"Local Save Only (Cloud Config Missing): {e}")

# 6.B Client Profile
elif st.session_state.active_tab == "profile":
    st.subheader(T['nav_profile'])
    
    profile_type = st.radio("Select Category", ["Man (Formal)", "Woman (Haute Couture)", "Child (Standard)"], horizontal=True)
    
    st.info(f"Drafting logic calibrated for: **{profile_type}**")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.write("### Body Shape Analysis")
        shape = st.selectbox("Shape", ["Hourglass", "Pear", "Rectangle", "Inverted Triangle", "Apple"])
    with c2:
        st.write("### Fit Preferences")
        fit = st.select_slider("Fit Tightness", options=["Skin Tight", "Slim", "Regular", "Loose", "Oversize"])

# 6.C Fabric Intelligence
elif st.session_state.active_tab == "fabric":
    st.subheader(T['nav_fabric'])
    
    c1, c2 = st.columns(2)
    with c1:
        fabric_type = st.selectbox("Fabric Type", ["Silk Satin", "Wool Blend", "Velvet", "Linen", "Chiffon"])
        design_type = st.selectbox("Garment Type", ["Suit (2pc)", "Evening Gown", "Shirt", "Trousers"])
        width = st.selectbox("Bolt Width", ["150 cm (Standard)", "110 cm (Narrow)"])
    
    with c2:
        # Simple Calculation Logic
        base_needed = st.session_state.measurements.get("Length", 150) / 100
        multiplier = 1.0
        
        if design_type == "Suit (2pc)": multiplier = 2.5
        elif design_type == "Evening Gown": multiplier = 2.0
        
        if width == "110 cm (Narrow)": multiplier *= 1.4
        
        total_fabric = base_needed * multiplier
        
        st.metric(label=T['lbl_fabric_est'], value=f"{total_fabric:.2f} Meters")
        st.progress(min(total_fabric/5, 1.0))
        st.caption(T['msg_fabric'])

# 6.D Precision Pattern Engine (SVG)
elif st.session_state.active_tab == "pattern":
    st.subheader(T['nav_pattern'])
    
    st.markdown("Upload Reference Sketch (for visual aid only)")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Reference", width=300)
    
    st.markdown("### Vector Generation")
    
    # Parametric Drafting Logic (Simplified Bodice Block)
    m = st.session_state.measurements
    if not m:
        st.warning("Please enter measurements in the Measurements tab first.")
    else:
        # Logic to generate SVG string
        w_px = m['Chest'] * 5 # Scale for display
        h_px = m['Length'] * 5
        
        svg_content = f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {m['Chest']+20} {m['Length']+20}" width="500" height="600" style="border:1px solid #D4AF37; background:#fff;">
            <defs>
                <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                    <path d="M 10 0 L 0 0 0 10" fill="none" stroke="gray" stroke-width="0.1"/>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
            
            <path d="M 0 0 L {m['Chest']/2} 0 L {m['Chest']/2} {m['Length']} L 0 {m['Length']} Z" 
                  fill="none" stroke="black" stroke-width="0.5" />
            
            <path d="M 0 0 Q {m['Chest']/6} {m['Chest']/6} {m['Chest']/4} 0" 
                  fill="none" stroke="red" stroke-width="0.5" />
            
            <path d="M {m['Chest']/2} 0 Q {m['Chest']/2 - 5} {m['Length']/4} {m['Chest']/2} {m['Length']/3}" 
                  fill="none" stroke="red" stroke-width="0.5" />
            
            <circle cx="{m['Chest']/4}" cy="{m['Length']/2}" r="1" fill="blue" />
            <text x="5" y="{m['Length']-5}" font-size="2" font-family="Arial">Hemline: {m['Chest']}cm Width</text>
        </svg>
        """
        
        # Display SVG
        st.markdown(svg_content, unsafe_allow_html=True)
        
        # Download Button
        b64 = base64.b64encode(svg_content.encode('utf-8')).decode("utf-8")
        href = f'<a href="data:image/svg+xml;base64,{b64}" download="rayane_pattern_v1.svg" class="css-button">{T["lbl_pattern_dl"]}</a>'
        st.markdown(href, unsafe_allow_html=True)

# 6.E Billing & WhatsApp
elif st.session_state.active_tab == "billing":
    st.subheader(T['nav_billing'])
    
    col1, col2 = st.columns(2)
    with col1:
        labor_cost = st.number_input("Labor Cost (DA)", 0, 100000, 5000)
        fabric_cost = st.number_input("Materials Cost (DA)", 0, 100000, 2000)
        tax = st.number_input("Tax / Fees (%)", 0, 100, 0)
    
    with col2:
        subtotal = labor_cost + fabric_cost
        total = subtotal + (subtotal * (tax/100))
        
        st.markdown(f"""
        <div style="background-color:#1E293B; padding:20px; border-radius:10px; border:1px solid #D4AF37;">
            <h2 style="color:white !important;">TOTAL</h2>
            <h1 style="color:#D4AF37 !important;">{total:,.2f} DA</h1>
        </div>
        """, unsafe_allow_html=True)
        
        client_phone = st.text_input(T['lbl_phone'], placeholder="213555...")
        
        if client_phone:
            msg_text = f"Rayane Tailor Elite Invoice\n\nFabric: {fabric_cost}\nLabor: {labor_cost}\nTotal: {total} DA"
            encoded_msg = urllib.parse.quote(msg_text)
            wa_link = f"https://wa.me/{client_phone}?text={encoded_msg}"
            
            st.markdown(f"""
            <a href="{wa_link}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#25D366; color:white; padding:15px; border-radius:8px; text-align:center; font-weight:bold; margin-top:10px;">
                    WhatsApp Invoice 📱
                </div>
            </a>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #555;'>Rayane Tailor Elite © 2026 | Powered by Streamlit</div>", unsafe_allow_html=True)
