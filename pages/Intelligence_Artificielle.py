import streamlit as st
import sys
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pickle
from sklearn.cluster import KMeans

# --- CONFIGURATION ---
st.set_page_config(page_title="AI Vision | AssurInsight", page_icon="🧠", layout="wide")

# --- IMPORT DB ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from database.db_manager import get_all_data
except ImportError:
    st.error("⚠️ Connexion database perdue.")

# --- UI DESIGN : GLASSMORPHISM & LIGHT THEME (FORCÉ) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    :root {
        --primary-color: #3b82f6;
        --background-color: #f0f4f8;
        --secondary-background-color: #ffffff;
        --text-color: #002d5e;
        --font: 'Outfit', sans-serif;
    }

    html, body, [class*="css"] { 
        font-family: 'Outfit', sans-serif; 
        background-color: #f0f4f8 !important; 
        color: #002d5e !important;
    }
    
    .stApp {
        background-color: #f0f4f8 !important;
    }

    .ai-header {
        background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
        padding: 40px;
        border-radius: 30px;
        box-shadow: 20px 20px 60px #d1d9e6, -20px -20px 60px #ffffff;
        text-align: center;
        margin-bottom: 40px;
        border: 1px solid rgba(255, 255, 255, 0.8);
    }
    
    .main-title {
        background: linear-gradient(90deg, #1e40af, #3b82f6, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 3.5rem; letter-spacing: -1px;
    }

    .stat-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 24px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }
    .stat-card:hover { transform: translateY(-5px); border-color: #3b82f6; }

    .ai-badge {
        background: #ebf4ff; color: #1e40af;
        padding: 5px 15px; border-radius: 50px;
        font-size: 0.8rem; font-weight: 600;
        text-transform: uppercase;
    }

    h1, h2, h3, p, span, label, .stMarkdown {
        color: #002d5e !important;
    }

    /* Correction du contraste pour les messages d'alerte et metrics */
    div[data-testid="stMetricValue"] > div { color: #1e40af !important; }
    div[data-testid="stAlert"] p { color: inherit !important; }
    .stAlert { border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- ENGINE IA AVANCÉ AVEC CHARGEMENT DE MODÈLE ---
def advanced_ai_engine(df):
    # 1. Scoring d'Appétence
    rev_weights = {"< 50k": 10, "50k-150k": 25, "150k-300k": 45, "300k-600k": 70, "> 600k": 95}
    
    df['revenu_mensuel'] = df['revenu_mensuel'].fillna("< 50k")
    df['niveau_confiance'] = pd.to_numeric(df['niveau_confiance'], errors='coerce').fillna(df['niveau_confiance'].median() if not df['niveau_confiance'].empty else 5)
    
    df['score_fin'] = df['revenu_mensuel'].map(rev_weights).fillna(10)
    df['score_appetence'] = (df['score_fin'] * 0.4) + (df['niveau_confiance'] * 6)
    df['risk_score'] = 100 - (df['niveau_confiance'] * 10)
    
    # 2. Clustering via Pipeline (ml_pipeline.pkl)
    X = df[['niveau_confiance', 'score_fin']].astype(float).values
    X = np.nan_to_num(X)
    
    # Chemin vers le modèle sauvegardé
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "ml_pipeline.pkl")
    
    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                pipeline = pickle.load(f)
            df['segment_id'] = pipeline.predict(X)
        except:
            # Fallback si le pickle est corrompu ou incompatible
            kmeans = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X)
            df['segment_id'] = kmeans.labels_
    else:
        # Fallback si le fichier n'existe pas encore
        kmeans = KMeans(n_clusters=3, n_init=10, random_state=42).fit(X)
        df['segment_id'] = kmeans.labels_
    
    segment_names = {0: "💎 Potentiel Élevé", 1: "🛡️ Profil Prudent", 2: "⚡ Opportunistes"}
    df['segment_label'] = df['segment_id'].map(segment_names).fillna("Non Classé")
    
    return df

# --- PAGE LAYOUT & NAVIGATION ---
st.markdown('<div class="ai-header"><span class="ai-badge">Intelligence Artificielle V3.0</span><h1 class="main-title">AI Strategy & Vision</h1><p style="color: #64748b;">Moteur prédictif de segmentation et d\'optimisation de conversion</p></div>', unsafe_allow_html=True)

# Bouton Retour à l'accueil
if st.button("⬅️ Retour à l'Accueil"):
    st.switch_page("Accueil.py") 

df = get_all_data()

if df is not None and len(df) >= 3:
    df = advanced_ai_engine(df)

    # --- TOP METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="stat-card"><small>📈 Appétence Moyenne</small><h3>{round(df["score_appetence"].mean(),1)}%</h3></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="stat-card"><small>⚠️ Indice de Risque (Churn)</small><h3 style="color:#ef4444;">{round(df["risk_score"].mean(),1)}%</h3></div>', unsafe_allow_html=True)
    with m3:
        top_seg = df['segment_label'].value_counts().idxmax() if not df.empty else "N/A"
        st.markdown(f'<div class="stat-card"><small>🏆 Segment Dominant</small><h3 style="color:#3b82f6;">{top_seg}</h3></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="stat-card"><small>🤝 Confiance Globale</small><h3>{round(df["niveau_confiance"].mean()*10,1)}/100</h3></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- MAIN ANALYTICS ---
    col_main1, col_main2 = st.columns([2, 1])

    with col_main1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.subheader("🎯 Clustering Intelligent : Profils Comportementaux")
        fig_cluster = px.scatter(df, x="score_fin", y="niveau_confiance", 
                                 color="segment_label", size="score_appetence",
                                 hover_data=['ville', 'revenu_mensuel'],
                                 color_discrete_sequence=px.colors.qualitative.Bold,
                                 template="simple_white")
        fig_cluster.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_cluster, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.subheader("📦 Recommandations Stratégiques")
        reco_data = df.groupby('segment_label')['score_appetence'].count().reset_index()
        fig_donut = px.pie(reco_data, values='score_appetence', names='segment_label', 
                           hole=0.7, color_discrete_sequence=['#1e40af', '#60a5fa', '#93c5fd'])
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- PREDICTIVE TABLE ---
    st.markdown('<div class="stat-card">', unsafe_allow_html=True)
    st.subheader("📋 Liste des Prospects Prioritaires (Score IA > 60)")
    priority_df = df[df['score_appetence'] > 60][['ville', 'sexe', 'revenu_mensuel', 'score_appetence', 'segment_label']].sort_values(by='score_appetence', ascending=False)
    st.dataframe(priority_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- LIVE SIMULATOR ---
    st.markdown("### 🧬 Simulateur de Neurones (Inférence Directe)")
    with st.expander("Tester un profil instantanément pour une aide à la décision"):
        sc1, sc2, sc3 = st.columns(3)
        v_rev = sc1.select_slider("Revenu Mensuel Estimé", ["< 50k", "50k-150k", "150k-300k", "300k-600k", "> 600k"])
        v_conf = sc2.slider("Niveau de Confiance (0-10)", 0, 10, 5)
        v_mat = sc3.selectbox("Maturité / Connaissance", ["Nulle", "Faible", "Moyenne", "Bonne", "Expert"])
        
        if st.button("Lancer l'Inférence"):
            rev_val = {"< 50k": 10, "50k-150k": 25, "150k-300k": 45, "300k-600k": 70, "> 600k": 95}.get(v_rev)
            final_score = (rev_val * 0.4) + (v_conf * 6)
            
            st.toast("Analyse des vecteurs en cours...", icon="🤖")
            st.write("---")
            c_res1, c_res2 = st.columns(2)
            c_res1.metric("Probabilité de Conversion", f"{round(final_score,1)}%")
            
            if final_score > 70:
                st.balloons()
                st.success("✅ Cible Prioritaire : Recommander Assurance Vie / Investissement Capitalisé")
            elif final_score > 40:
                st.info("ℹ️ Cible Standard : Recommander Assurance Santé / Auto Responsabilité Civile")
            else:
                st.warning("⚠️ Basse Priorité : Focus Micro-assurance Scolaire ou Accident")

else:
    st.info("💡 Collectez au moins 3 enquêtes pour activer le moteur de Clustering IA.")