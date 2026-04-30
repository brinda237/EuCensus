import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests
import sys
import os
import pandas as pd

# Configuration de la page (DOIT être en premier)
st.set_page_config(page_title="EduCensus | Cameroun", layout="wide", page_icon="🎓")

# --- GESTION DE LA BASE DE DONNÉES & TEMPS RÉEL ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'database')))

try:
    from db_manager import create_table, get_all_data
    create_table()
    data_raw = get_all_data()
    total_reponses = len(data_raw)
except Exception as e:
    total_reponses = 0

# --- FONCTION POUR ANIMATIONS LOTTIE ---
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except:
        return None

lottie_education = load_lottieurl("https://lottie.host/8227f12e-1579-4503-b541-11d2e2930256/m7N8w3XjGv.json")

# --- STYLE CSS AVANCÉ & FOOTER ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"]  { font-family: 'Poppins', sans-serif; }
    .stApp { background: linear-gradient(to bottom, #f8fafc, #ffffff); }

    /* --- MENU RESPONSIVE --- */
    @media (max-width: 768px) {
        .main-title { font-size: 2.2rem !important; text-align: center; }
        .hero-text { text-align: center; }
        .nav-link { padding: 10px !important; font-size: 12px !important; }
        div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    }

    /* --- BOUTON DANSANT (CTA) --- */
    @keyframes pulse-green {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { transform: scale(1.05); box-shadow: 0 0 0 15px rgba(34, 197, 94, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }

    div.stButton > button {
        background: linear-gradient(90deg, #16a34a 0%, #22c55e 100%) !important;
        color: white !important;
        border-radius: 50px !important;
        padding: 1.2rem 2.5rem !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        border: none !important;
        animation: pulse-green 2s infinite !important;
        display: block !important;
        margin: 2rem auto !important;
        transition: 0.4s ease-in-out;
    }

    /* --- CARTES KPI --- */
    .metric-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        text-align: center;
        border-top: 5px solid #16a34a;
        transition: 0.3s;
        margin-bottom: 15px;
    }
    .metric-card:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(22,163,74,0.15); }

    /* --- FOOTER PROFESSIONNEL --- */
    .footer {
        background-color: #052e16;
        color: white;
        padding: 50px 20px 20px 20px;
        border-radius: 30px 30px 0 0;
        margin-top: 50px;
    }
    .footer-column h4 { color: #22c55e; margin-bottom: 20px; font-weight: 700; }
    .footer-column p { font-size: 0.9rem; color: #cbd5e1; line-height: 1.6; }
    .footer-bottom {
        text-align: center;
        padding-top: 30px;
        border-top: 1px solid #166534;
        margin-top: 30px;
        font-size: 0.8rem;
        color: #94a3b8;
    }

    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- MENU DE NAVIGATION ---
selected = option_menu(
    menu_title=None,
    options=["Accueil", "Collecte de Données", "Statistiques", "IA & Prévisions"],
    icons=["house-fill", "pencil-square", "graph-up-arrow", "robot"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "5px!important", "background-color": "#ffffff", "box-shadow": "0 4px 15px rgba(0,0,0,0.1)", "border-radius": "0px"},
        "icon": {"color": "#16a34a", "font-size": "18px"}, 
        "nav-link": {"font-size": "14px", "text-align": "center", "margin":"2px", "font-weight": "600"},
        "nav-link-selected": {"background": "linear-gradient(90deg, #16a34a, #22c55e)", "color": "white"},
    }
)

if selected == "Accueil":
    # --- HERO SECTION ---
    col_h1, col_h2 = st.columns([1.5, 1])
    
    with col_h1:
        st.markdown(f"""
            <div class='hero-text' style='padding-top: 2rem;'>
                <h1 class="main-title" style='font-size: 3.5rem; font-weight: 800; color: #052e16; line-height: 1.1;'>
                    L'Éducation au Cameroun <br><span style='color: #16a34a;'>Pilotée par la Data.</span>
                </h1>
                <p style='font-size: 1.2rem; color: #5a7184; margin: 1.5rem 0;'>
                    Plateforme nationale de recensement scolaire. Nous avons déjà enregistré 
                    <b style='color:#16a34a;'>{total_reponses} élèves & étudiants</b> en temps réel. 
                    Aidez-nous à cartographier l'éducation camerounaise.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎓 PARTICIPER AU RECENSEMENT MAINTENANT"):
            st.switch_page("pages/Collecte_Donnees.py")
            
    with col_h2:
        if lottie_education:
            st_lottie(lottie_education, height=380, key="education_anim")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- KPI SECTION ---
    st.markdown("<h3 style='text-align: center; color: #052e16; margin-bottom: 2rem; font-weight:700;'>Observatoire Scolaire National</h3>", unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.markdown(f"<div class='metric-card'><h2 style='color: #16a34a; margin:0;'>{total_reponses}</h2><p style='color: #1e293b; font-weight: 600; margin:0;'>Recensés</p><small>Collecte Live</small></div>", unsafe_allow_html=True)
    with k2:
        st.markdown("<div class='metric-card'><h2 style='color: #16a34a; margin:0;'>79%</h2><p style='color: #1e293b; font-weight: 600; margin:0;'>Taux de Scolarisation</p><small>Primaire National</small></div>", unsafe_allow_html=True)
    with k3:
        st.markdown("<div class='metric-card'><h2 style='color: #16a34a; margin:0;'>10</h2><p style='color: #1e293b; font-weight: 600; margin:0;'>Régions</p><small>Couverture Nationale</small></div>", unsafe_allow_html=True)
    with k4:
        st.markdown("<div class='metric-card'><h2 style='color: #16a34a; margin:0;'>MINESEC</h2><p style='color: #1e293b; font-weight: 600; margin:0;'>Tutelle</p><small>Cadre Officiel</small></div>", unsafe_allow_html=True)

    # --- SECTION VISION & IMPACT ---
    st.markdown("<br><hr style='border: 0.5px solid #e2e8f0;'><br>", unsafe_allow_html=True)
    v1, v2 = st.columns([1, 1], gap="large")
    
    with v1:
        st.markdown("""
            <h2 style='color: #052e16; font-weight: 700;'>L'impact de vos données</h2>
            <p style='color: #5a7184; font-size: 1.1rem;'>
                <b>EduCensus</b> est un moteur de transformation pour le système éducatif :
            </p>
            <ul style='color: #5a7184; font-size: 1.05rem; line-height: 1.8;'>
                <li>🎯 <b>Cartographie :</b> Identifier les zones de sous-scolarisation.</li>
                <li>⚡ <b>Équité :</b> Réduire les disparités régionales et de genre.</li>
                <li>📉 <b>Décrochage :</b> Analyser et prévenir l'abandon scolaire.</li>
            </ul>
        """, unsafe_allow_html=True)
    
    with v2:
        st.image("https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=1000&auto=format&fit=crop", use_container_width=True, caption="Recensement de la population scolarisée au Cameroun")

    # --- FOOTER PROFESSIONNEL ---
    st.markdown("""
        <div class="footer">
            <div class="container">
                <div style="display: flex; flex-wrap: wrap; justify-content: space-between;">
                    <div class="footer-column" style="flex: 1; min-width: 250px; margin-bottom: 20px;">
                        <h4>EduCensus Cameroun</h4>
                        <p>La première plateforme nationale de recensement et d'analyse de la population scolarisée au Cameroun.</p>
                    </div>
                    <div class="footer-column" style="flex: 1; min-width: 200px; margin-bottom: 20px;">
                        <h4>Navigation</h4>
                        <p>• Accueil<br>• Collecte de Données<br>• Statistiques<br>• IA & Prévisions</p>
                    </div>
                    <div class="footer-column" style="flex: 1; min-width: 200px; margin-bottom: 20px;">
                        <h4>Contact & Support</h4>
                        <p>Email: contact@educensus.cm<br>Yaoundé, Cameroun<br>Expertise Éducation & MINESEC</p>
                    </div>
                </div>
                <div class="footer-bottom">
                    &copy; 2026 EduCensus Cameroun | Propulsé par Streamlit & Intelligence Artificielle
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- ROUTAGE ---
elif selected == "Collecte de Données":
    st.switch_page("pages/Collecte_Donnees.py")
elif selected == "Statistiques":
    st.switch_page("pages/Analyse_Exploratoire.py")
elif selected == "IA & Prévisions":
    st.switch_page("pages/Intelligence_Artificielle.py")