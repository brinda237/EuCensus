import streamlit as st
import sys
import os
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Analyse Stratégique | AssurInsight",
    page_icon="📊",
    layout="wide"
)

# --- IMPORT DB_MANAGER ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from database.db_manager import save_entry, get_all_data, create_table
    create_table()
except ImportError:
    st.error("⚠️ Erreur de liaison avec le module database.")

# --- GESTION DES NOTIFICATIONS ---
if "success_msg" not in st.session_state:
    st.session_state.success_msg = None

# --- CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    .stApp { background-color: #f8faff; font-family: 'Plus Jakarta Sans', sans-serif; }

    .stMarkdown, .stSelectbox label, .stTextInput label, .stRadio label, .stSlider label, .stMultiSelect label, 
    .stHeader, p, span, label, .stSubheader, h1, h2, h3 {
        color: #002d5e !important;
        font-weight: 600 !important;
    }

    .header-container {
        text-align: center;
        padding: 30px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 30px;
        border: 1px solid #e2e8f0;
    }

    .main-title {
        background: linear-gradient(90deg, #002d5e, #007bff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
    }

    .section-card {
        background: white;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #007bff;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #002d5e 0%, #007bff 100%) !important;
        color: white !important;
        border: none !important;
        height: 50px;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease;
    }
    </style>
""", unsafe_allow_html=True)

# --- AFFICHAGE DU SUCCÈS ---
if st.session_state.success_msg:
    st.balloons()
    st.success(st.session_state.success_msg)
    st.session_state.success_msg = None

# --- BOUTON RETOUR ---
col_back, _ = st.columns([1, 4])
with col_back:
    if st.button("⬅️ Menu Principal", key="btn_home"):
        st.switch_page("Accueil.py")

# --- HEADER ---
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">Analyse Stratégique & Statistique</h1>
        <p style="color: #64748b; font-weight: 400;">Intelligence de marché et corrélations socio-économiques</p>
    </div>
""", unsafe_allow_html=True)

tab_anal, tab_form, tab_view = st.tabs(["📈 TABLEAU DE BORD COMPLET", "🖋️ COLLECTE", "📊 DONNÉES BRUTES"])

# --- CHARGEMENT DES DONNÉES ---
df = get_all_data()

with tab_anal:
    if df is not None and not df.empty:
        # --- KPIs ---
        st.markdown("### 🔑 Indicateurs Critiques")
        k1, k2, k3, k4 = st.columns(4)
        k1.markdown(f'<div class="metric-card"><b>Échantillon</b><br><span style="font-size:24px; color:#007bff;">{len(df)}</span></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="metric-card"><b>Confiance Moy.</b><br><span style="font-size:24px; color:#007bff;">{round(df["niveau_confiance"].mean(), 1)}/10</span></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="metric-card"><b>Villes</b><br><span style="font-size:24px; color:#007bff;">{df["ville"].nunique()}</span></div>', unsafe_allow_html=True)
        k4.markdown(f'<div class="metric-card"><b>Taux de Digitalisation</b><br><span style="font-size:24px; color:#007bff;">{round((df["connaissance_assurance"].isin(["Bonne", "Expert"]).mean()*100),1)}%</span></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # --- ANALYSE DE CORRÉLATION (LES NOUVEAUX GRAPHIQUES) ---
        st.markdown("### 🔗 Analyses de Corrélation & Cross-Data")
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("📍 Confiance Moyenne par Région")
            # Corrélation Confiance / Région (profession contient la région dans votre logique de save)
            reg_conf = df.groupby('profession')['niveau_confiance'].mean().sort_values().reset_index()
            fig_reg_conf = px.bar(reg_conf, x='niveau_confiance', y='profession', orientation='h', 
                                 color='niveau_confiance', color_continuous_scale='Blues')
            st.plotly_chart(fig_reg_conf, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_c2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("🔥 Impact des Sinistres sur la Confiance")
            # Corrélation Confiance / Expérience Sinistre
            # Note: il faut s'assurer que la colonne 'experience_sinistre' existe ou adapter selon vos clés
            fig_sin = px.box(df, x='culture_cima', y='niveau_confiance', points="all", color='sexe')
            st.plotly_chart(fig_sin, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- RÉPARTITION DÉMOGRAPHIQUE ---
        st.markdown("### 👥 Profils des Répondants")
        a1, a2, a3 = st.columns([1, 1, 1.5])
        with a1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Répartition Sexe")
            fig_sexe = px.pie(df, names='sexe', hole=0.4, color_discrete_sequence=['#002d5e', '#007bff'])
            st.plotly_chart(fig_sexe, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with a2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Volume par Âge")
            age_data = df['age_tranche'].value_counts().reset_index()
            fig_age = px.bar(age_data, x='age_tranche', y='count', color_discrete_sequence=['#007bff'])
            st.plotly_chart(fig_age, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with a3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Topographie des Collectes")
            fig_tree = px.treemap(df, path=['profession', 'ville'], color='niveau_confiance', color_continuous_scale='RdBu')
            st.plotly_chart(fig_tree, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- COMPORTEMENTS & PSYCHOLOGIE ---
        st.markdown("### 🧠 Baromètre Psychologique")
        b1, b2, b3 = st.columns(3)
        with b1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Canaux Favoris")
            canal_data = df['critere_choix'].value_counts().reset_index()
            fig_canal = px.funnel(canal_data, y='critere_choix', x='count', color_discrete_sequence=['#002d5e'])
            st.plotly_chart(fig_canal, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with b2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Barrières Majeures")
            fig_barr = px.pie(df, names='barriere_principale', color_discrete_sequence=px.colors.sequential.OrRd)
            st.plotly_chart(fig_barr, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with b3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Niveau de Connaissance")
            radar_data = df['connaissance_assurance'].value_counts().reset_index()
            fig_radar = px.line_polar(radar_data, r='count', theta='connaissance_assurance', line_close=True)
            fig_radar.update_traces(fill='toself', line_color='#007bff')
            st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- ANALYSE SOCIO-FINANCIÈRE ---
        st.markdown("### 💰 Dimensions Financières")
        d1, d2 = st.columns(2)
        with d1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Confiance par Secteur d'Activité")
            fig_sect = px.violin(df, y='niveau_confiance', x='secteur_activite', box=True, color='secteur_activite')
            st.plotly_chart(fig_sect, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with d2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.subheader("Revenu vs Digitalisation")
            fig_rev = px.density_heatmap(df, x="revenu_mensuel", y="connaissance_assurance", text_auto=True, color_continuous_scale='Viridis')
            st.plotly_chart(fig_rev, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📊 En attente de données pour générer l'intelligence de marché.")

# --- ONGLET 2 : FORMULAIRE ---
with tab_form:
    with st.form("survey_form", clear_on_submit=True):
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("👤 Profil & Localisation")
        c1, c2, c3 = st.columns(3)
        with c1:
            sexe = st.selectbox("Sexe", ["Masculin", "Féminin"])
            age = st.selectbox("Âge", ["18-25", "26-35", "36-45", "46-55", "56+"])
        with c2:
            region_val = st.selectbox("Région", ["Littoral", "Centre", "Ouest", "Sud", "Nord", "Est", "Adamaoua", "EN", "NW", "SW"])
            ville = st.text_input("Ville")
        with c3:
            secteur = st.selectbox("Secteur", ["Public", "Privé Formel", "Informel", "Étudiant", "Libéral"])
            revenu = st.selectbox("Revenu Mensuel", ["< 50k", "50k-150k", "150k-300k", "300k-600k", "> 600k"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🧠 Perception & Confiance")
        c4, c5 = st.columns(2)
        with c4:
            perception = st.radio("L'assurance est pour vous :", ["Nécessaire", "Une charge", "Une obligation"], horizontal=True)
            connaissance = st.select_slider("Niveau de connaissance", ["Nulle", "Faible", "Moyenne", "Bonne", "Expert"])
        with c5:
            confiance = st.slider("Confiance envers les assureurs (0-10)", 0, 10, 5)
            barriere = st.selectbox("Principale barrière", ["Coût élevé", "Méfiance (Remboursement)", "Lenteur administrative", "Manque d'infos", "Religieux/Culturel"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🛡️ Habitudes & Digitalisation")
        c6, c7 = st.columns(2)
        with c6:
            type_assur = st.multiselect("Assurances possédées", ["Auto", "Santé", "Vie/Décès", "Retraite", "Scolaire", "Habitation", "Aucune"])
            canal = st.selectbox("Canal préféré", ["Agent physique", "Courtier", "Banque", "Application Mobile", "Site Web"])
        with c7:
            experience = st.radio("Sinistre non remboursé ?", ["Non", "Oui", "Jamais eu de sinistre"], horizontal=True)
            insurtech = st.select_slider("Prêt pour l'assurance digitale ?", ["Pas du tout", "Peut-être", "Totalement prêt"])
        st.markdown('</div>', unsafe_allow_html=True)

        submit_btn = st.form_submit_button("🚀 ENREGISTRER L'ENQUÊTE")
        
        if submit_btn:
            if not ville:
                st.warning("⚠️ Précisez la ville.")
            else:
                data = {
                    "sexe": sexe, "age_tranche": age, "ville": ville, "profession": region_val, 
                    "secteur_activite": secteur, "revenu_mensuel": revenu, "connaissance_assurance": connaissance,
                    "type_abonnement": ", ".join(type_assur) if type_assur else "Aucune", "niveau_confiance": confiance,
                    "barriere_principale": barriere, "critere_choix": canal, "culture_cima": perception
                }
                save_entry(data)
                st.session_state.success_msg = f"✨ Enregistré avec succès !"
                st.rerun()

# --- ONGLET 3 : VUE DONNÉES ---
with tab_view:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger CSV complet", data=csv, file_name="AssurInsight_Export.csv", mime="text/csv")
    else:
        st.info("La base de données est actuellement vide.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    <div style="text-align: center; padding-top: 20px; color: #94a3b8; font-size: 0.8rem;">
        © 2026 AssurInsight - Intelligence de Données | Analyseur Statistique V2.0
    </div>
""", unsafe_allow_html=True)