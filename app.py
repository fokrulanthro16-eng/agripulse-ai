import os
import json
import time
import io
import streamlit as st
from PIL import Image, ImageDraw

# Page Configuration
st.set_page_config(
    page_title="AgriPulse AI | Pathology & Fair-Trade Route Optimizer",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Design
st.markdown("""
<style>
    /* Global Styles & Variables */
    :root {
        --primary-green: #10b981;
        --dark-green: #047857;
        --accent-amber: #f59e0b;
        --accent-red: #ef4444;
        --bg-card: rgba(16, 185, 129, 0.04);
        --border-color: rgba(16, 185, 129, 0.2);
    }
    
    /* Main container tweaks */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Header Container */
    .hero-header {
        background: linear-gradient(135deg, #064e3b 0%, #047857 50%, #065f46 100%);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(4, 120, 87, 0.3);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        color: #a7f3d0;
        margin-top: 0.4rem;
        font-weight: 400;
    }
    
    /* Custom Card */
    .agri-card {
        background-color: var(--stBackground);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* Metric Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-severe {
        background-color: rgba(239, 68, 68, 0.15);
        color: #dc2626;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .badge-moderate {
        background-color: rgba(245, 158, 11, 0.15);
        color: #d97706;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .badge-low {
        background-color: rgba(16, 185, 129, 0.15);
        color: #059669;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .stat-box {
        background: rgba(16, 185, 129, 0.06);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    .stat-val {
        font-size: 1.6rem;
        font-weight: 700;
        color: #047857;
    }
    
    .stat-lbl {
        font-size: 0.85rem;
        color: #4b5563;
        font-weight: 500;
    }
    
    /* Table Styling */
    div[data-testid="stMarkdownContainer"] table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }
    
    div[data-testid="stMarkdownContainer"] th {
        background-color: #047857 !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 10px 14px !important;
        text-align: left;
    }
    
    div[data-testid="stMarkdownContainer"] td {
        padding: 10px 14px !important;
        border-bottom: 1px solid #f3f4f6;
    }
    
    /* Best ROI Highlight Banner */
    .roi-banner {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 1.2rem;
        margin-top: 1rem;
        color: #064e3b;
    }
    
    .roi-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #047857;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Try importing google-genai
GENAI_AVAILABLE = False
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/color/96/wheat.png", width=64)
    st.title("AgriPulse AI Config")
    st.caption("Autonomous Plant Pathology & Market Logistics Engine")
    st.markdown("---")
    
    api_key_input = st.text_input(
        "🔑 Gemini API Key",
        type="password",
        help="Enter your Gemini API key from Google AI Studio. Leave empty to run high-fidelity simulation mode.",
        placeholder="AIzaSy..."
    )
    
    crop_type = st.selectbox(
        "🌾 Crop Category",
        options=[
            "Rice",
            "Potato",
            "Tomato",
            "Wheat",
            "Corn",
            "Mustard",
            "Other"
        ],
        index=0
    )
    
    origin_location = st.text_input(
        "📍 Farm Origin Location",
        value="Sylhet, Bangladesh",
        help="Enter your farm, village, or regional origin location"
    )
    
    st.markdown("---")
    st.markdown("### ⚙️ System Specifications")
    st.markdown("""
    - **Vision Model**: `gemini-2.5-flash`
    - **SDK**: `google-genai` (v0.1+)
    - **Target Region**: Regional Wholesale Agricultural Markets
    - **Arbitrage Mode**: Real-time Net Profit ROI
    """)
    
    st.markdown("---")
    st.caption("© 2026 AgriPulse AI System. Built for Agricultural Extension Agents & Farmers.")

# Helper function to generate mock crop leaf sample if no image uploaded
def generate_sample_crop_image(crop_name):
    img = Image.new('RGB', (400, 400), color=(34, 139, 34))
    draw = ImageDraw.Draw(img)
    # Draw leaf vein patterns
    draw.line([(200, 400), (200, 0)], fill=(0, 100, 0), width=8)
    draw.line([(200, 300), (100, 200)], fill=(0, 100, 0), width=4)
    draw.line([(200, 250), (300, 150)], fill=(0, 100, 0), width=4)
    draw.line([(200, 180), (80, 100)], fill=(0, 100, 0), width=4)
    draw.line([(200, 120), (320, 50)], fill=(0, 100, 0), width=4)
    
    # Draw disease spots based on crop type
    if "Rice" in crop_name:
        # Spindle lesions
        draw.ellipse([(150, 120), (180, 180)], fill=(139, 69, 19), outline=(255, 215, 0))
        draw.ellipse([(220, 200), (240, 260)], fill=(139, 69, 19), outline=(255, 215, 0))
        draw.ellipse([(130, 280), (160, 340)], fill=(105, 105, 105), outline=(139, 69, 19))
    elif "Potato" in crop_name:
        # Dark blight spots
        draw.ellipse([(120, 100), (220, 200)], fill=(47, 79, 79), outline=(218, 165, 32))
        draw.ellipse([(210, 220), (290, 300)], fill=(47, 79, 79), outline=(218, 165, 32))
    elif "Tomato" in crop_name:
        # Yellowing leaf curl & spots
        draw.ellipse([(140, 140), (240, 240)], fill=(218, 165, 32), outline=(178, 34, 34))
        draw.ellipse([(90, 250), (150, 310)], fill=(178, 34, 34), outline=(255, 215, 0))
    else:
        # Generic rust spots
        draw.ellipse([(160, 160), (210, 210)], fill=(160, 82, 45), outline=(255, 140, 0))
        draw.ellipse([(220, 100), (260, 140)], fill=(160, 82, 45), outline=(255, 140, 0))
    return img

# Mock Analysis Data Generator for Fallback/Simulation Mode
def get_mock_analysis_data(crop_type, origin, harvest_volume):
    crop_clean = crop_type.split("/")[0].strip()
    
    mock_db = {
        "Rice": {
            "disease_en": "Rice Blast (Pyricularia oryzae)",
            "confidence": 96,
            "severity": "Severe",
            "symptoms": "Distinct elliptical spindle-shaped leaf lesions with grayish centers and dark reddish-brown borders on leaf blades.",
            "organic": "Spray Neem seed kernel extract (5%) or apply Trichoderma harzianum bio-fungicide (5g/L) during early morning hours.",
            "chemical": "Tricyclazole 75 WP @ 0.6g/Liter or Isoprothiolane 40 EC @ 1.5ml/Liter of water. Apply 2 sprays at 10-day intervals.",
            "preventive": "Ensure balanced Nitrogen fertilization (avoid excess urea). Maintain optimal standing water (2-3 cm) and burn affected stubble post-harvest.",
            "base_price": 1380
        },
        "Potato": {
            "disease_en": "Late Blight (Phytophthora infestans)",
            "confidence": 94,
            "severity": "Severe",
            "symptoms": "Water-soaked dark brown/black spots starting from leaf tips and margins, with white fuzzy fungal growth on undersides in humid conditions.",
            "organic": "Apply Copper Hydroxide / Bordeaux Mixture (1%) spray. Prune severely infected lower stems immediately.",
            "chemical": "Mancozeb 75 WP (2g/L) as protective spray, or Cymoxanil + Mancozeb (2.5g/L) / Dimethomorph (1g/L) as curative treatment.",
            "preventive": "Use certified disease-free seed tubers. Avoid overhead irrigation and ensure wide ridge spacing for leaf aeration.",
            "base_price": 950
        },
        "Tomato": {
            "disease_en": "Tomato Yellow Leaf Curl Virus (TYLCV)",
            "confidence": 92,
            "severity": "Moderate",
            "symptoms": "Upward curling of leaf margins, severe chlorosis (yellowing), leaf size reduction, and stunted plant growth.",
            "organic": "Spray Yellow Sticky Traps (15 traps/acre) to catch whitefly vectors. Spray soapy water or Refined Neem Oil (3ml/L).",
            "chemical": "Target Whitefly vector using Imidacloprid 17.8 SL @ 0.5ml/L or Acetamiprid 20 SP @ 0.2g/L water.",
            "preventive": "Plant reflective silver plastic mulch to repel whiteflies. Install fine 40-mesh insect netting over seedbeds.",
            "base_price": 1650
        },
        "Wheat": {
            "disease_en": "Wheat Blast (Magnaporthe oryzae Triticum)",
            "confidence": 89,
            "severity": "Moderate",
            "symptoms": "Bleached spikelets on heads, dark gray spots on rachis, leading to premature head drying and shriveled grains.",
            "organic": "Apply Garlic clove extract (5%) spray and treat seeds with Trichoderma viride.",
            "chemical": "Folicur (Tebuconazole 250 EC) @ 1ml/L or Nativo 75 WG (Tebuconazole + Trifloxystrobin) @ 0.6g/L.",
            "preventive": "Sow early in recommended planting window (Nov 15-30). Use blast-resistant varieties like BARI Gom 33.",
            "base_price": 1420
        },
        "Corn": {
            "disease_en": "Common Rust (Puccinia sorghi)",
            "confidence": 91,
            "severity": "Low",
            "symptoms": "Small, powdery brown to reddish-orange pustules scattered across both leaf surfaces.",
            "organic": "Spray Sulfur-based bio-formulations or Bio-agent Pseudomonas fluorescens @ 10g/L.",
            "chemical": "Propiconazole 25 EC @ 1ml/L or Azoxystrobin + Difenoconazole @ 1ml/L water.",
            "preventive": "Plant rust-resistant hybrids. Avoid dense crop canopy and maintain crop rotation with non-graminaceous crops.",
            "base_price": 1100
        },
        "Mustard": {
            "disease_en": "Alternaria Blight (Alternaria brassicae)",
            "confidence": 95,
            "severity": "Moderate",
            "symptoms": "Concentric dark brown circular spots on lower leaves, stems, and pods with chlorotic halos.",
            "organic": "Spray bio-fungicide Trichoderma harzianum or Datura leaf extract (10%).",
            "chemical": "Iprodione 50 WP (Rovral) @ 2g/L or Mancozeb 75 WP @ 2.5g/L water.",
            "preventive": "Seed treatment with Carboxin + Thiram (2.5g/kg seed). Maintain optimal row spacing (30 cm).",
            "base_price": 2800
        }
    }
    
    data = mock_db.get(crop_clean, mock_db["Rice"])
    bp = data["base_price"]
    vol = float(harvest_volume)
    
    origin_name = origin.split(",")[0].strip() if "," in origin else origin.strip()
    
    # 3 Realistic Regional Wholesale Markets in English
    markets = [
        {
            "market_name": f"{origin_name} Local Upazila Market",
            "distance_km": 14,
            "price_per_mound_bdt": bp,
            "transport_cost_bdt": round(15 * 14 + (vol * 8)),
            "recommendation": "Local Quick Clearance"
        },
        {
            "market_name": "Sylhet Kazir Bazar Regional Wholesale Hub",
            "distance_km": 62,
            "price_per_mound_bdt": bp + 180,
            "transport_cost_bdt": round(45 * 25 + (vol * 18)),
            "recommendation": "⭐ BEST ROI DISPATCH ROUTE"
        },
        {
            "market_name": "Dhaka Karwan Bazar National Wholesale Market",
            "distance_km": 295,
            "price_per_mound_bdt": bp + 360,
            "transport_cost_bdt": round(120 * 35 + (vol * 32)),
            "recommendation": "High Transit Risk & Fuel Surcharge"
        }
    ]
    
    # Calculate financial metrics
    for m in markets:
        gross = m["price_per_mound_bdt"] * vol
        net = gross - m["transport_cost_bdt"]
        m["gross_bdt"] = gross
        m["net_profit_bdt"] = net

    # Best market selection
    best_m = max(markets, key=lambda x: x["net_profit_bdt"])
    
    reasoning = f"Direct dispatch to **{best_m['market_name']}** delivers the highest net return of **BDT {best_m['net_profit_bdt']:,}** for your {vol:.0f} mound harvest. " \
                f"Despite transporting {best_m['distance_km']} km, the wholesale price premium (+BDT {best_m['price_per_mound_bdt'] - bp}/mound) significantly outweighs the transport cost."

    return {
        "disease_name_en": data["disease_en"],
        "confidence_score": data["confidence"],
        "severity_level": data["severity"],
        "symptoms_observed": data["symptoms"],
        "organic_remedy": data["organic"],
        "chemical_treatment": data["chemical"],
        "preventive_measures": data["preventive"],
        "markets": markets,
        "best_route_reasoning": reasoning
    }

# Main Application Layout
st.markdown("""
<div class="hero-header">
    <div class="hero-title">
        <span>🌾 AgriPulse AI</span>
    </div>
    <div class="hero-subtitle">
        Autonomous Crop Pathology Diagnosis & Fair-Trade Wholesale Route Optimizer
    </div>
</div>
""", unsafe_allow_html=True)

# 2-Column Responsive Layout
left_col, right_col = st.columns([1, 1.25], gap="large")

# LEFT PANEL: Input & Inspection
with left_col:
    st.subheader("📸 1. Crop Leaf Inspection & Harvest Input")
    
    with st.container():
        st.markdown('<div class="agri-card">', unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload Leaf Image",
            type=["jpg", "jpeg", "png"],
            help="Select a clear photograph of the affected plant leaf"
        )
        
        use_sample = st.checkbox("Use Demo Preset Image", value=(uploaded_file is None))
        
        preview_img = None
        if uploaded_file is not None:
            try:
                preview_img = Image.open(uploaded_file)
                st.image(preview_img, caption=f"Uploaded Specimen: {uploaded_file.name}", use_container_width=True)
                st.caption(f"Dimensions: {preview_img.size[0]}x{preview_img.size[1]} px | Format: {preview_img.format}")
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
        elif use_sample:
            preview_img = generate_sample_crop_image(crop_type)
            st.image(preview_img, caption=f"Simulated {crop_type} Specimen with Pathological Lesions", use_container_width=True)
            st.info("ℹ️ Displaying synthetic specimen customized for selected crop type.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('<div class="agri-card">', unsafe_allow_html=True)
    st.markdown("#### 📦 Harvest Volume & Logistics Parameters")
    
    harvest_volume = st.number_input(
        "Estimated Harvest Volume (Mounds)",
        min_value=1,
        max_value=1000,
        value=20,
        step=1,
        help="1 Mound ≈ 37.32 kg. Enter estimated harvest yield."
    )
    
    st.caption(f"Total Weight Equivalent: **{harvest_volume * 37.32:,.1f} kg** ({harvest_volume * 0.03732:,.2f} Metric Tons)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    run_btn = st.button("🚀 Run AgriPulse Diagnosis & Market Analysis", use_container_width=True, type="primary")

# RIGHT PANEL: AI Diagnostic Engine & Logistics Optimizer
with right_col:
    st.subheader("🔬 2. AI Pathology & Fair-Trade Arbitrage Results")
    
    if not run_btn and "analysis_results" not in st.session_state:
        st.info("👈 Upload a crop leaf image (or use sample preset) and click **Run AgriPulse Diagnosis & Market Analysis** to initiate inspection.")
        
        # Display feature highlights card
        st.markdown("""
        <div class="agri-card">
            <h4>💡 How AgriPulse AI Empowers Farmers:</h4>
            <ul>
                <li><b>Computer Vision Pathology</b>: Detects crop diseases early with diagnostic confidence scores and visual symptom breakdowns.</li>
                <li><b>Agronomic Prescriptions</b>: Provides both organic eco-friendly remedies and precise targeted chemical treatments with dosages.</li>
                <li><b>Fair-Trade Market Arbitrage</b>: Compares regional wholesale market prices, deducts fuel/truck logistics, and calculates real net profit in BDT.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    if run_btn:
        if preview_img is None:
            st.error("Please upload an image or enable the demo preset image to proceed.")
        else:
            with st.spinner("⏳ Analyzing leaf micro-pathology & evaluating regional wholesale market arbitrage..."):
                analysis_data = None
                used_live_api = False
                
                # Check if API Key provided and google-genai is installed
                if api_key_input and api_key_input.strip() != "":
                    if GENAI_AVAILABLE:
                        try:
                            # Use official google-genai SDK
                            client = genai.Client(api_key=api_key_input.strip())
                            
                            # Convert PIL Image to Bytes for API
                            img_byte_arr = io.BytesIO()
                            preview_img.save(img_byte_arr, format='JPEG')
                            img_bytes = img_byte_arr.getvalue()
                            
                            prompt = f"""
                            You are an expert plant pathologist and agricultural economist specializing in crop diagnosis and regional wholesale market route optimization.
                            Analyze this crop leaf image for disease diagnosis and perform market route arbitrage.
                            CRITICAL REQUIREMENT: Respond strictly and 100% in professional English. Do not include non-English characters or non-English script anywhere in your JSON output.
                            
                            Context:
                            - Crop Type: {crop_type}
                            - Farm Origin Location: {origin_location}
                            - Harvest Volume: {harvest_volume} mounds
                            
                            Respond strictly in valid JSON format matching this structure:
                            {{
                              "disease_name_en": "Disease Name in English (Scientific Name)",
                              "confidence_score": 95,
                              "severity_level": "Severe" (or "Moderate" or "Low"),
                              "symptoms_observed": "Observed visual symptoms details in English",
                              "organic_remedy": "Organic/Bio-control remedy details in English",
                              "chemical_treatment": "Targeted chemical treatment with exact dosage in English",
                              "preventive_measures": "Preventive field management measures in English",
                              "markets": [
                                {{
                                  "market_name": "Market Name in English (e.g. Local Upazila Market)",
                                  "distance_km": 15,
                                  "price_per_mound_bdt": 1350,
                                  "transport_cost_bdt": 450,
                                  "recommendation": "Brief recommendation tag in English"
                                }},
                                {{
                                  "market_name": "Regional Market Name in English (e.g. Sylhet Wholesale Market)",
                                  "distance_km": 60,
                                  "price_per_mound_bdt": 1500,
                                  "transport_cost_bdt": 1200,
                                  "recommendation": "Brief recommendation tag in English"
                                }},
                                {{
                                  "market_name": "National Market Name in English (e.g. Dhaka Karwan Bazar Wholesale Hub)",
                                  "distance_km": 280,
                                  "price_per_mound_bdt": 1620,
                                  "transport_cost_bdt": 3800,
                                  "recommendation": "Brief recommendation tag in English"
                                }}
                              ],
                              "best_route_reasoning": "Clear financial and agronomic reasoning for the best market choice in English"
                            }}
                            """
                            
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[
                                    types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'),
                                    prompt
                                ],
                                config=types.GenerateContentConfig(
                                    response_mime_type="application/json"
                                )
                            )
                            
                            if response.text:
                                raw_json = response.text
                                analysis_data = json.loads(raw_json)
                                
                                # Compute gross and net for live API response
                                vol = float(harvest_volume)
                                for m in analysis_data.get("markets", []):
                                    gross = m["price_per_mound_bdt"] * vol
                                    net = gross - m["transport_cost_bdt"]
                                    m["gross_bdt"] = gross
                                    m["net_profit_bdt"] = net
                                    
                                used_live_api = True
                        except Exception as e:
                            st.warning(f"⚠️ Gemini Live API call encountered an issue ({str(e)}). Switching to high-fidelity simulation engine.")
                            analysis_data = get_mock_analysis_data(crop_type, origin_location, harvest_volume)
                    else:
                        st.warning("⚠️ `google-genai` SDK is loading in fallback mode. Executing simulation analysis engine.")
                        analysis_data = get_mock_analysis_data(crop_type, origin_location, harvest_volume)
                else:
                    # Run fallback simulation mode
                    analysis_data = get_mock_analysis_data(crop_type, origin_location, harvest_volume)
                
                st.session_state["analysis_results"] = analysis_data
                st.session_state["used_live_api"] = used_live_api

    # Render Results if available in session_state
    if "analysis_results" in st.session_state:
        res = st.session_state["analysis_results"]
        used_api = st.session_state.get("used_live_api", False)
        
        if used_api:
            st.success("⚡ Live Gemini 2.5 Flash Multimodal Diagnosis Completed Successfully!")
        else:
            st.info("ℹ️ Mode: High-Fidelity Agricultural Simulation Engine (Enter Gemini API Key in sidebar for live model calls)")
            
        # 1. Pathology Diagnosis Header & Metrics
        st.markdown("### 🔬 Pathology Diagnosis & Severity Grading")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-lbl">Detected Pathology</div>
                <div style="font-size: 1.1rem; font-weight:700; color:#047857; margin-top:4px;">{res.get('disease_name_en', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col2:
            conf = res.get('confidence_score', 90)
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-lbl">AI Diagnostic Confidence</div>
                <div class="stat-val">{conf}%</div>
                <div style="font-size: 0.8rem; color:#10b981;">High Precision Verification</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col3:
            sev = res.get('severity_level', 'Moderate')
            badge_class = "badge-severe" if sev == "Severe" else ("badge-moderate" if sev == "Moderate" else "badge-low")
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-lbl">Severity Grading</div>
                <div style="margin-top:8px;"><span class="badge {badge_class}">{sev}</span></div>
                <div style="font-size: 0.8rem; color:#6b7280; margin-top:4px;">Immediate Attention</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"**👁️ Visual Symptoms Observed**: {res.get('symptoms_observed', 'N/A')}")
        st.markdown("---")
        
        # 2. Agronomic Prescription
        st.markdown("### 💊 Actionable Agronomic Prescription")
        
        rx_tab1, rx_tab2, rx_tab3 = st.tabs([
            "🌿 Organic / Bio-Control", 
            "🧪 Chemical Treatment", 
            "🛡️ Preventive Measures"
        ])
        
        with rx_tab1:
            st.success(f"**Bio-Control Remedy**: {res.get('organic_remedy', 'N/A')}")
            st.caption("Eco-friendly remedies minimize chemical residues and preserve beneficial soil micro-organisms.")
            
        with rx_tab2:
            st.warning(f"**Targeted Fungicide/Bactericide**: {res.get('chemical_treatment', 'N/A')}")
            st.caption("Follow exact mixing ratios and safety instructions. Wear protective masks during field spraying.")
            
        with rx_tab3:
            st.info(f"**Field Management**: {res.get('preventive_measures', 'N/A')}")
            st.caption("Preventative crop rotation and field sanitation prevent pathogen spore spread to surrounding plots.")
            
        st.markdown("---")
        
        # 3. Fair-Trade Wholesale Arbitrage Table
        st.markdown("### 📈 Fair-Trade Wholesale Market Arbitrage")
        st.caption(f"Comparing regional wholesale market hubs for **{harvest_volume} mounds** from **{origin_location}**")
        
        mkts = res.get("markets", [])
        if mkts:
            # Build Markdown Table
            table_md = "| Market Name | Distance | Price / Mound | Transport Cost | Net Profit (BDT) | Recommendation |\n"
            table_md += "| :--- | :---: | :---: | :---: | :---: | :--- |\n"
            
            best_market = None
            max_net = -1
            
            for m in mkts:
                name = m.get("market_name", "Wholesale Market")
                dist = m.get("distance_km", 0)
                price = m.get("price_per_mound_bdt", 0)
                t_cost = m.get("transport_cost_bdt", 0)
                net = m.get("net_profit_bdt", price * harvest_volume - t_cost)
                recom = m.get("recommendation", "-")
                
                if net > max_net:
                    max_net = net
                    best_market = m
                
                table_md += f"| **{name}** | {dist} km | BDT {price:,} | BDT {t_cost:,} | **BDT {net:,.0f}** | {recom} |\n"
                
            st.markdown(table_md)
            
            # ROI Banner Highlight
            if best_market:
                st.markdown(f"""
                <div class="roi-banner">
                    <div class="roi-header">
                        <span>🏆 Optimal Dispatch Route: {best_market.get('market_name')}</span>
                    </div>
                    <div style="font-size:0.95rem; line-height: 1.5; color: #064e3b;">
                        <b>Net Financial Yield</b>: BDT {best_market.get('net_profit_bdt', 0):,.0f} &nbsp;|&nbsp; 
                        <b>Wholesale Rate</b>: BDT {best_market.get('price_per_mound_bdt', 0):,}/mound &nbsp;|&nbsp; 
                        <b>Logistics Deduct</b>: BDT {best_market.get('transport_cost_bdt', 0):,}<br>
                        <hr style="border: 0; border-top: 1px solid rgba(16, 185, 129, 0.3); margin: 8px 0;">
                        {res.get('best_route_reasoning', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

