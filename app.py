import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import time
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image

# 1. إعدادات الصفحة والواجهة الملكية
st.set_page_config(page_title="Rayane Tailor Elite Ultimate", layout="wide", initial_sidebar_state="collapsed", page_icon="✂️")

# تهيئة MediaPipe Pose للتحليل البصري
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

# دالة معالجة النصوص العربية
def ar(text):
    if not text: return ""
    return get_display(reshape(str(text)))

# نظام الترجمة
t = {
    "العربية": {
        "title": "إمبراطورية Rayane Tailor Elite",
        "subtitle": "النظام الذكي المتكامل للتفصيل والحياكة الراقية (v2.0 Pro)",
        "step1": "🖼️ ميزة البحث والتعرف على الموديل (AI Scan)",
        "step2": "👥 بروفايل الزبون ونوع اللباس",
        "step3": "📏 هندسة المقاسات والباترون الذكي (CAD)",
        "step4": "🧪 الحاسبة الذكية للأقمشة والسلع",
        "step5": "🧾 الإدارة المالية والربط السحابي",
        "upload_btn": "رفع صورة الموديل (من الجهاز، بنترست، أو المتصفح)",
        "gender": "جنس الزبون",
        "style": "تصنيف اللباس العالمي",
        "trad_style": "اللباس التقليدي جزائري",
        "cut": "نوع القصة (الخراطة)",
        "save_cloud": "💾 مزامنة وحفظ (Google Sheets)",
        "pdf_inv": "توليد فاتورة PDF احترافية شاملة",
        "ai_scan": "🤖 استنتاج المقاسات آلياً من الصورة",
        "cad_export": "📐 تصدير باترون صناعي جاهز للقص (SVG/CAD)"
    },
    "English": {
        "title": "Rayane Tailor Elite Empire",
        "subtitle": "Smart Integrated System for High-End Couture (v2.0 Pro)",
        "step1": "🖼️ Image Recognition (AI Scan)",
        "step2": "👥 Client & Style",
        "step3": "📏 Pattern Engineering (CAD)",
        "step4": "🧪 Smart Calculator",
        "step5": "🧾 Cloud & Financials",
        "upload_btn": "Upload Model",
        "gender": "Gender",
        "style": "Global Style",
        "trad_style": "Algerian Traditional",
        "cut": "Cut Type",
        "save_cloud": "💾 Sync to Sheets",
        "pdf_inv": "Generate Full PDF Invoice",
        "ai_scan": "🤖 AI Auto-Inference from Image",
        "cad_export": "📐 Export Industrial CAD (SVG)"
    }
}

size_charts = {
    "S": {"neck": 34, "shoulder": 38, "armhole": 22, "bust": 88, "w1": 68, "w2": 72, "w3": 92, "width": 95, "total": 140, "sleeve": 58, "arm_c": 30, "wrist": 16, "bust_depth": 24},
    "M": {"neck": 36, "shoulder": 40, "armhole": 24, "bust": 96, "w1": 76, "w2": 80, "w3": 100, "width": 105, "total": 142, "sleeve": 59, "arm_c": 32, "wrist": 17, "bust_depth": 26},
    "L": {"neck": 38, "shoulder": 42, "armhole": 26, "bust": 104, "w1": 84, "w2": 88, "w3": 108, "width": 115, "total": 145, "sleeve": 60, "arm_c": 34, "wrist": 18, "bust_depth": 28},
    "XL": {"neck": 40, "shoulder": 44, "armhole": 28, "bust": 112, "w1": 92, "w2": 96, "w3": 116, "width": 125, "total": 148, "sleeve": 61, "arm_c": 36, "wrist": 19, "bust_depth": 30}
}

# CSS المطور مع خلفية "أدوات الخياطة" وتأثيرات احترافية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;700&display=swap');
    
    .stApp { 
        background-color: #fcfaf7; 
        background-image: url("https://www.transparenttextures.com/patterns/sewing-kit.png"); 
        background-attachment: fixed; 
    }
    
    html, body, [class*="css"] { 
        font-family: 'Cairo', sans-serif; 
        text-align: right; 
        direction: rtl; 
    }
    
    /* الهيدر الملكي */
    .header-style {
        background: linear-gradient(135deg, #1a0933 0%, #4B0D85 80%, #D4AF37 100%);
        padding: 40px; 
        border-radius: 0px 0px 40px 40px; 
        color: white; 
        text-align: center;
        border-bottom: 5px solid #D4AF37; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.4); 
        margin-bottom: 30px;
    }
    
    /* تنسيق الكروت والحاويات - Glassmorphism */
    .stExpander { 
        background-color: rgba(255, 255, 255, 0.95) !important; 
        border: 1px solid #e0e0e0 !important;
        border-right: 8px solid #D4AF37 !important; 
        border-radius: 12px !important; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }
    
    /* الأزرار الاحترافية */
    .stButton>button { 
        background: linear-gradient(90deg, #2D0B5A 0%, #4B0D85 100%); 
        color: white; 
        border-radius: 8px; 
        border: none; 
        padding: 10px 24px; 
        font-weight: bold; 
        width: 100%; 
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(75, 13, 133, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(75, 13, 133, 0.3);
        background: linear-gradient(90deg, #D4AF37 0%, #F4CF57 100%); 
        color: #1a0933;
    }

    /* تنسيق الأرقام والمدخلات */
    div[data-baseweb="input"] {
        border-radius: 8px;
        background-color: #f8f9fa;
        border: 1px solid #ddd;
    }

    /* النصوص */
    h1, h2, h3 { color: #2D0B5A; }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #D4AF37;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. نظام الدخول
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

# 3. Sidebar & Header
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3050/3050212.png", width=80)
    st.markdown("### ⚙️ System Control")
    sel_lang = st.selectbox("Language / اللغة", ["العربية", "English"])
    cur_t = t[sel_lang]
    st.success("🟢 System Online")
    st.info(f"📅 {datetime.now().strftime('%Y-%m-%d')}")
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

st.markdown(f'<div class="header-style"><h1>{cur_t["title"]}</h1><p style="font-size:18px; opacity:0.9;">{cur_t["subtitle"]}</p></div>', unsafe_allow_html=True)

# --- الخطوة 1: الرفع وتحليل الذكاء الاصطناعي ---
if 'ai_measured' not in st.session_state:
    st.session_state.ai_measured = size_charts["M"].copy()

with st.expander(cur_t["step1"], expanded=True):
    col_up, col_res = st.columns([1, 2])
    with col_up:
        img_file = st.file_uploader(cur_t["upload_btn"], type=['png', 'jpg', 'jpeg'])
        is_far = st.checkbox("🔍 وضع التصوير عن بعد (+3m)")
    
    if img_file: 
        image = Image.open(img_file)
        with col_up:
            st.image(image, caption="Uploaded Model", use_container_width=True)
        
        with col_res:
            if st.button(cur_t["ai_scan"]):
                # محاكاة تجربة مستخدم احترافية
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("⏳ جاري معالجة الهيكل العظمي (Skeleton Detection)...")
                time.sleep(0.5)
                progress_bar.progress(30)
                
                img_np = np.array(image)
                results = pose.process(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
                
                status_text.text("📐 حساب النسب والأبعاد الهندسية...")
                progress_bar.progress(60)
                time.sleep(0.3)
                
                if results.pose_landmarks:
                    lm = results.pose_landmarks.landmark
                    dist_factor = 1.2 if is_far else 1.0
                    shoulder_width = abs(lm[11].x - lm[12].x) * dist_factor
                    
                    if shoulder_width > 0.45: detected = "XL"
                    elif shoulder_width > 0.38: detected = "L"
                    else: detected = "M"
                    
                    st.session_state.ai_measured = size_charts[detected].copy()
                    progress_bar.progress(100)
                    status_text.text("✅ تمت العملية بنجاح!")
                    st.success(f"🤖 النتيجة: تم تحليل الجسم وتحديد المقاس الأنسب: **{detected}**")
                else:
                    progress_bar.empty()
                    st.error("⚠️ لم يتم التعرف على تفاصيل الجسم بوضوح. يرجى استخدام صورة أوضح.")

# --- الخطوة 2: النوع ---
with st.expander(cur_t["step2"]):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{cur_t['gender']}**")
        gender = st.radio("الجنس", ["رجل", "امرأة", "ولد", "بنت"], horizontal=True, label_visibility="collapsed")
        garment_type = st.selectbox(cur_t["style"], ["كاجوال", "رسمي", "سروال", "فستان", "فاست", "آخر"])
    with c2:
        algerian_trad = st.selectbox(cur_t["trad_style"], ["None", "قندورة", "كاراكو", "قفطان", "شدة", "بدرون"])
        cut_type = st.select_slider(cur_t["cut"], options=["Slim", "Regular", "Oversize", "A-Line", "Cloch", "Double Cloch"])

# --- الخطوة 3: الباترون الهندسي (مع إضافة الخانات اليدوية الجديدة) ---
with st.expander(cur_t["step3"]):
    st.markdown("##### ⚙️ إعدادات المقاسات (Measurements Engine)")
    preset = st.radio("المقياس المعتمد (اختر Manual للإدخال اليدوي الحر):", ["AI Detected", "Manual", "S", "M", "L", "XL"], horizontal=True)
    
    if preset == "AI Detected":
        def_vals = st.session_state.ai_measured
    else:
        base_vals = size_charts.get(preset if preset != "Manual" else "M", size_charts["M"])
        def_vals = base_vals.copy()

    # تقسيم احترافي للمقاسات
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.caption("المنطقة العلوية")
        m_neck = st.number_input("الرقبة (Neck)", value=int(def_vals.get("neck", 36)), help="محيط الرقبة عند القاعدة")
        m_shoulder = st.number_input("الكتف (Shoulder)", value=int(def_vals.get("shoulder", 40)))
        m_bust = st.number_input("محيط الصدر (Bust)", value=int(def_vals.get("bust", 96)))
    with col_m2:
        st.caption("الجذع والخصر")
        m_w1 = st.number_input("الخصر العلوي (Waist)", value=int(def_vals.get("w1", 76)))
        m_width = st.number_input("العرض السفلي (Hem)", value=int(def_vals.get("width", 105)))
        m_armhole = st.number_input("حردة الابط (Armhole)", value=int(def_vals.get("armhole", 24)))
    with col_m3:
        st.caption("الأطوال")
        m_total = st.number_input("الطول الكلي (Total L)", value=int(def_vals.get("total", 142)))
        m_arm_l = st.number_input("طول الذراع (Sleeve)", value=int(def_vals.get("sleeve", 59)))
        m_shoulder_slope = st.slider("ميلان الكتف", 0, 8, 3)
    with col_m4:
        st.caption("🔬 قياسات دقيقة (Pro)")
        m_wrist = st.number_input("محيط المعصم (Wrist)", value=int(def_vals.get("wrist", 17)))
        m_bust_depth = st.number_input("عمق الصدر (Depth)", value=int(def_vals.get("bust_depth", 26)))
        st.info("💡 هذه القياسات لضبط الكم والبنسات.")

    st.markdown("---")
    st.markdown("### 🛠️ خيارات التصميم المتطور (Advanced Design)")
    col_adv1, col_adv2 = st.columns(2)
    with col_adv1:
        has_sleeves = st.checkbox("فستان بأكمام (Full Sleeves)", value=True)
        has_back = st.checkbox("يوجد ظهر (Has Back)", value=True)
        has_sides = st.checkbox("يوجد جوانب (Has Sides)", value=True)
    with col_adv2:
        pocket_type = st.selectbox("نوع الجيوب", ["بدون", "جيب شق (Welt)", "جيب خارجي (Patch)", "جيب جانبي"])
        slit_type = st.selectbox("الفتحة (Slit)", ["بدون", "فتحة خلفية", "فتحة جانبية", "فتحة أمامية"])
    
    extra = st.multiselect("إضافات هندسية:", ["بانسات", "كشكشة", "طيات", "بطانة"])

    fabric_selected = st.session_state.get('fabric_sel', 'قطيفة')
    ease_allowance = 0
    if fabric_selected in ["كتان", "ستان"]: ease_allowance = 4
    
    adjusted_armhole = m_armhole
    if not has_back:
        adjusted_armhole -= 2
        st.warning("ℹ️ تنبيه هندسي: تم تعديل توازن الحردة آلياً (-2سم) لأن التصميم بدون ظهر.")

    # --- المعاين ثلاثي الأبعاد والباترون ---
    tab_3d, tab_2d = st.tabs([f"👗 {ar('المعاين الملكي (3D)')}", f"📐 {ar('الباترون الهندسي (CAD)')}"])
    
    color_map = {"قطيفة": "#4B0D85", "حرير": "#FFD700", "كتان": "#F5F5DC", "كريب": "#E6E6FA", "ستان": "#FFFFFF"}
    fabric_color = color_map.get(fabric_selected, "#D4AF37")

    with tab_3d:
        three_js_code = f"""
        <div id="container3d" style="width: 100%; height: 400px; background: radial-gradient(circle, #fcfaf7 0%, #eeeeee 100%); border-radius: 20px; border: 1px solid #ddd;"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            const container = document.getElementById('container3d');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, container.clientWidth / 400, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, 400);
            container.appendChild(renderer.domElement);
            
            const light = new THREE.DirectionalLight(0xffffff, 1);
            light.position.set(5, 5, 5).normalize();
            scene.add(light);
            scene.add(new THREE.AmbientLight(0x404040));
            
            const material = new THREE.MeshPhongMaterial({{ color: '{fabric_color}', shininess: 80, specular: 0x111111 }});
            
            // Torso
            const torsoGeom = new THREE.CylinderGeometry(0.5, 0.7, 1.5, 32);
            const torso = new THREE.Mesh(torsoGeom, material);
            scene.add(torso);
            
            if ({str(has_sleeves).lower()}) {{
                const armGeom = new THREE.CylinderGeometry(0.12, 0.08, 1.2, 32);
                const leftArm = new THREE.Mesh(armGeom, material);
                leftArm.position.set(-0.75, 0.3, 0);
                leftArm.rotation.z = Math.PI/3;
                scene.add(leftArm);
                
                const rightArm = new THREE.Mesh(armGeom, material);
                rightArm.position.set(0.75, 0.3, 0);
                rightArm.rotation.z = -Math.PI/3;
                scene.add(rightArm);
            }}
            
            const skirtGeom = new THREE.ConeGeometry(0.85, 2.2, 64, 1, true);
            const skirt = new THREE.Mesh(skirtGeom, material);
            skirt.position.y = -1.6;
            scene.add(skirt);
            
            camera.position.z = 4.5;
            camera.position.y = -0.5;
            
            function animate() {{
                requestAnimationFrame(animate);
                torso.rotation.y += 0.005;
                if(skirt) skirt.rotation.y += 0.005;
                renderer.render(scene, camera);
            }}
            animate();
        </script>
        <div style="text-align:center; font-size:12px; color:#888;">استخدم الماوس للتحكم (محاكاة تلقائية للدوران)</div>
        """
        st.components.v1.html(three_js_code, height=430)

    with tab_2d:
        darts_svg = '<path d="M 250,220 L 245,300 L 250,310 L 255,300 Z" fill="rgba(255,0,0,0.2)" stroke="red" stroke-width="1"/>' if "بانسات" in extra else ""
        ruffles_svg = '<path d="M 180,450 Q 200,430 220,450 Q 240,470 260,450 Q 280,430 300,450 Q 320,470 340,450" fill="none" stroke="#D4AF37" stroke-width="2"/>' if "كشكشة" in extra else ""
        sleeves_svg = f'<path d="M 400,100 L 480,350 L 440,360 L 350,180" fill="none" stroke="#2D0B5A" stroke-width="2" stroke-dasharray="5,5"/>' if has_sleeves else ""
        back_line_opacity = "1" if has_back else "0.1"
        back_msg = "" if has_back else f'<text x="200" y="250" fill="red" font-size="20">{ar("تصميم بدون ظهر - توازن مشدود")}</text>'
        pocket_svg = ""
        if pocket_type == "جيب خارجي (Patch)": pocket_svg = '<rect x="300" y="320" width="60" height="70" fill="none" stroke="#4B0D85" stroke-width="1.5"/>'
        elif pocket_type == "جيب شق (Welt)": pocket_svg = '<line x1="300" y1="340" x2="360" y2="340" stroke="#4B0D85" stroke-width="3"/>'
        slit_svg = f'<line x1="250" y1="450" x2="250" y2="380" stroke="blue" stroke-width="2" stroke-dasharray="4"/>' if slit_type != "بدون" else ""

        armhole_path = f"M 400,{60+m_shoulder_slope*5} C 420,120 400,160 350,180"
        
        # إضافة شبكة خلفية (Grid) للباترون ليبدو احترافياً
        grid_pattern = """
        <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#eee" stroke-width="1"/>
            </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
        """

        pattern_svg_content = f"""
        <svg width="500" height="500" viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#fff" stroke="#D4AF37" stroke-width="2"/>
            {grid_pattern}
            <path d="M 180,50 Q 250,30 320,50 L 400,{60+m_shoulder_slope*5} {armhole_path} L 320,450 L 180,450 Z" 
                  fill="rgba(45, 11, 90, 0.05)" stroke="#2D0B5A" stroke-width="3" style="opacity:{back_line_opacity}"/>
            
            <text x="210" y="25" font-size="12" fill="#2D0B5A" font-weight="bold">{ar('الرقبة')}: {m_neck}</text>
            <line x1="320" y1="50" x2="400" y2="{60+m_shoulder_slope*5}" stroke="red" stroke-width="1" />
            <text x="350" y="45" font-size="10" fill="red">{ar('كتف')}</text>

            <text x="220" y="200" font-size="12" fill="blue">{ar('مساحة راحة')}: +{ease_allowance}cm</text>
            <text x="220" y="480" font-size="15" fill="#2D0B5A" font-weight="bold">{ar('الطول')}: {m_total}cm | {ar('المعصم')}: {m_wrist}</text>
            
            {darts_svg} {ruffles_svg} {sleeves_svg} {pocket_svg} {slit_svg} {back_msg}
        </svg>
        """
        st.components.v1.html(pattern_svg_content, height=510)
        st.download_button(cur_t["cad_export"], data=pattern_svg_content, file_name=f"Rayane_Pattern_{datetime.now().strftime('%H%M')}.svg", mime="image/svg+xml")

# --- الخطوة 4: الحاسبة الذكية ---
with st.expander(cur_t["step4"]):
    c_c1, c_c2 = st.columns(2)
    with c_c1:
        st.markdown("#### 🧶 المواد الأولية")
        fabric = st.selectbox("القماش", ["قطيفة", "حرير", "كتان", "كريب", "دونتال", "ستان"], key='fabric_sel')
        u_price = st.number_input("سعر المتر (DA)", value=1000, step=100)
        buttons_cost = st.number_input("تكلفة لوازم صغيرة (أزرار) (DA)", value=0, step=50)
    with c_c2:
        st.markdown("#### 📐 الكميات والتصنيع")
        base = (m_total + m_arm_l + 20) / 100
        mult = 2.5 if "Cloch" in cut_type else (1.5 if "A-Line" in cut_type else 1.0)
        sleeve_extra = 0.6 if has_sleeves else 0
        total_f = (base * mult) + sleeve_extra
        
        # عرض متطور للنتيجة
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin:0; color:#4B0D85">{total_f:.2f} m</h3>
            <p style="margin:0; color:#666">الكمية المقترحة للشراء</p>
        </div>
        """, unsafe_allow_html=True)
        
        extra_items_cost = st.number_input("لوازم إضافية (سحاب/عقاد) (DA)", value=0, step=100)
        labor = st.number_input("حق الخياطة واليد العاملة (DA)", value=3000, step=500)

# --- الخطوة 5: الفاتورة والسحابة ---
with st.expander(cur_t["step5"]):
    items_total = buttons_cost + extra_items_cost
    final_price = (total_f * u_price) + labor + items_total
    
    col_fin1, col_fin2 = st.columns([2, 1])
    with col_fin1:
        st.markdown("#### 🧾 تفاصيل الفاتورة")
        inv_data = {
            "البند": ["القماش", "اللوازم", "اليد العاملة", "الإجمالي"],
            "التفاصيل": [f"{fabric} ({total_f:.2f}m)", "أزرار وسحابات", "تفصيل وخياطة", "-"],
            "السعر (DA)": [f"{total_f * u_price:.2f}", f"{items_total:.2f}", f"{labor:.2f}", f"**{final_price:.2f}**"]
        }
        st.dataframe(pd.DataFrame(inv_data), use_container_width=True, hide_index=True)
    
    with col_fin2:
        st.markdown("#### 📲 إجراءات")
        if st.button(cur_t["save_cloud"]):
            try:
                with st.spinner("جاري الاتصال بقاعدة البيانات..."):
                    df = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Client": gender, "Total": final_price, "Status": "Saved"}])
                    conn.update(spreadsheet=st.secrets["GSHEET_URL"], data=df)
                    st.success("✅ تم الحفظ بنجاح!")
            except: st.error("❌ خطأ في الاتصال (تحقق من الإنترنت)")

        if st.button(cur_t["pdf_inv"]):
            pdf = FPDF()
            pdf.add_page()
            try:
                pdf.add_font('Cairo', '', 'Cairo-Regular.ttf', uni=True)
                pdf.set_font('Cairo', '', 16)
            except: pdf.set_font("Arial", "B", 16)
            
            # رأس الفاتورة
            pdf.set_fill_color(75, 13, 133)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 20, ar("إمبراطورية Rayane Tailor - فاتورة رسمية"), 0, 1, 'C', 1)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(10)
            
            pdf.set_font('Cairo' if 'Cairo' in pdf.fonts else 'Arial', '', 12)
            pdf.cell(0, 10, f"{ar('التاريخ')}: {datetime.now().date()}", ln=True, align='R')
            pdf.cell(0, 10, f"{ar('نوع الزبون')}: {ar(gender)} | {ar('الموديل')}: {ar(garment_type)}", ln=True, align='R')
            pdf.ln(5)
            
            pdf.set_font('Cairo' if 'Cairo' in pdf.fonts else 'Arial', 'B', 14)
            pdf.cell(0, 10, f"{ar('--- تفاصيل التكلفة ---')}", ln=True, align='C')
            pdf.ln(5)
            
            pdf.set_font('Cairo' if 'Cairo' in pdf.fonts else 'Arial', '', 12)
            pdf.cell(100, 10, f"{total_f*u_price:.2f} DA", 1, 0, 'C')
            pdf.cell(90, 10, f"{ar('تكلفة القماش')} ({fabric})", 1, 1, 'R')
            
            pdf.cell(100, 10, f"{items_total:.2f} DA", 1, 0, 'C')
            pdf.cell(90, 10, f"{ar('لوازم وخردوات')}", 1, 1, 'R')
            
            pdf.cell(100, 10, f"{labor:.2f} DA", 1, 0, 'C')
            pdf.cell(90, 10, f"{ar('أتعاب التصميم والخياطة')}", 1, 1, 'R')
            
            pdf.ln(10)
            pdf.set_fill_color(212, 175, 55) # ذهبي
            pdf.set_font('Cairo' if 'Cairo' in pdf.fonts else 'Arial', 'B', 16)
            pdf.cell(0, 15, f"{ar('المبلغ الإجمالي')}: {final_price:.2f} DA", 1, 1, 'C', 1)
            
            st.download_button("Download Full Invoice (PDF)", pdf.output(), "Rayane_Tailor_Invoice.pdf")

st.markdown("---")
st.caption("2026 © Rayane Tailor Elite - Professional Tailoring System | v2.0 Ultimate Edition")
