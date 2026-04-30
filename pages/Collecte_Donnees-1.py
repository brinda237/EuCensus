import streamlit as st
import sys
import os
import io
import pandas as pd
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Collecte de Données | EduCensus Cameroun",
    page_icon="📝",
    layout="wide"
)

# --- IMPORT DB_MANAGER ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from db_manager import save_entry, get_all_data, create_table
    create_table()
except ImportError:
    st.error("⚠️ Erreur de liaison avec le module db_manager. Vérifiez le chemin du dossier.")

# --- GESTION DES NOTIFICATIONS POST-RERUN ---
if "success_msg" not in st.session_state:
    st.session_state.success_msg = None

# --- FONCTION EXPORT PDF ---
def export_pdf(df):
    try:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Rapport de Recensement Scolaire - EduCensus ({datetime.now().strftime('%d/%m/%Y')})", styles['Title']))
        data_list = [df.columns.to_list()] + df.values.tolist()
        t = Table(data_list)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(t)
        doc.build(elements)
        return buffer.getvalue()
    except Exception as e:
        return None

# --- CSS THÈME EDUCENSUS (VERT) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    .stApp {
        background-color: #f0faf4;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stMarkdown, .stSelectbox label, .stTextInput label, .stRadio label,
    .stSlider label, .stMultiSelect label, .stHeader, p, span, label,
    .stSubheader, h1, h2, h3 {
        color: #1a4731 !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    .header-container {
        text-align: center;
        padding: 30px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 30px;
        border: 1px solid #b7e4c7;
    }

    .main-title {
        background: linear-gradient(90deg, #1a4731, #2d9e5f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
    }

    .section-card {
        background: white;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #b7e4c7;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #1a4731 0%, #2d9e5f 100%) !important;
        color: white !important;
        border: none !important;
        height: 60px;
        border-radius: 15px !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        box-shadow: 0 10px 20px rgba(45, 158, 95, 0.2) !important;
        transition: all 0.3s ease;
    }

    div.stButton > button:hover {
        transform: scale(1.01);
        box-shadow: 0 12px 25px rgba(45, 158, 95, 0.3) !important;
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
        st.switch_page("Page acceuil.py")

# --- HEADER ---
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">📋 Collecte de Données Scolaires</h1>
        <p style="color: #64748b; font-weight: 400;">Contribuez au recensement de l'éducation au Cameroun</p>
    </div>
""", unsafe_allow_html=True)

tab_form, tab_view = st.tabs(["🖋️ FORMULAIRE DE RECENSEMENT", "📊 BASE DE DONNÉES & EXPORTS"])

with tab_form:
    with st.form("recensement_form", clear_on_submit=True):

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("👤 Informations Personnelles")
        c1, c2, c3 = st.columns(3)
        with c1:
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            sexe = st.selectbox("Sexe", ["Masculin", "Féminin"])
        with c2:
            age = st.selectbox("Tranche d'âge", ["5-10", "11-14", "15-18", "19-25", "26+"])
            region = st.selectbox("Région", ["Littoral", "Centre", "Ouest", "Sud", "Nord",
                                              "Est", "Adamaoua", "Extrême-Nord", "Nord-Ouest", "Sud-Ouest"])
            ville = st.text_input("Ville")
        with c3:
            statut = st.selectbox("Statut", ["Élève", "Étudiant", "Enseignant", "Parent d'élève"])
            handicap = st.radio("Situation de handicap ?", ["Non", "Oui"], horizontal=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("🏫 Informations Scolaires")
        c4, c5 = st.columns(2)
        with c4:
            nom_ecole = st.text_input("Nom de l'établissement")
            type_ecole = st.selectbox("Type d'établissement", ["Public", "Privé Laïc", "Privé Confessionnel"])
            niveau = st.selectbox("Niveau scolaire", ["Maternelle", "Primaire", "Collège", "Lycée",
                                                       "Université", "Formation Professionnelle"])
        with c5:
            classe = st.text_input("Classe / Filière")
            langue = st.selectbox("Langue d'enseignement", ["Français", "Anglais", "Bilingue"])
            acces_internet = st.radio("Accès à Internet à l'école ?", ["Oui", "Non"], horizontal=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.subheader("📊 Conditions & Environnement")
        c6, c7 = st.columns(2)
        with c6:
            distance_ecole = st.selectbox("Distance domicile-école", ["< 1 km", "1-5 km", "5-10 km", "> 10 km"])
            moyen_transport = st.selectbox("Moyen de transport", ["À pied", "Vélo", "Moto", "Bus", "Voiture"])
        with c7:
            acces_eau = st.radio("Accès à l'eau potable à l'école ?", ["Oui", "Non"], horizontal=True)
            satisfaction = st.select_slider("Satisfaction de l'enseignement (1-5)",
                                            options=["1 - Très insatisfait", "2 - Insatisfait",
                                                     "3 - Neutre", "4 - Satisfait", "5 - Très satisfait"])
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🚀 ENREGISTRER DANS LA BASE DE DONNÉES")

        if submit_btn:
            if not ville or not nom_ecole:
                st.warning("⚠️ Veuillez remplir la ville et le nom de l'établissement.")
            else:
                data = {
                    "nom": nom,
                    "prenom": prenom,
                    "sexe": sexe,
                    "age_tranche": age,
                    "region": region,
                    "ville": ville,
                    "statut": statut,
                    "handicap": handicap,
                    "nom_ecole": nom_ecole,
                    "type_ecole": type_ecole,
                    "niveau": niveau,
                    "classe": classe,
                    "langue": langue,
                    "acces_internet": acces_internet,
                    "distance_ecole": distance_ecole,
                    "moyen_transport": moyen_transport,
                    "acces_eau": acces_eau,
                    "satisfaction": satisfaction
                }
                try:
                    save_entry(data)
                    st.session_state.success_msg = f"✨ Recensement de {nom} {prenom} à {ville} enregistré avec succès !"
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'enregistrement : {e}")

with tab_view:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    try:
        df = get_all_data()
    except:
        df = None

    if df is not None and not df.empty:
        st.markdown(f"### 🗂️ Base de Données ({len(df)} enregistrements)")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.markdown("### 📥 Exporter les Données")

        col_csv, col_xlsx, col_pdf = st.columns(3)

        csv_data = df.to_csv(index=False).encode('utf-8')
        col_csv.download_button(
            label="📂 Télécharger en CSV",
            data=csv_data,
            file_name=f"EduCensus_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

        output_xlsx = io.BytesIO()
        with pd.ExcelWriter(output_xlsx, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Recensement_Scolaire')
        col_xlsx.download_button(
            label="📂 Télécharger en Excel",
            data=output_xlsx.getvalue(),
            file_name=f"EduCensus_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        pdf_data = export_pdf(df)
        if pdf_data:
            col_pdf.download_button(
                label="📂 Télécharger en PDF",
                data=pdf_data,
                file_name=f"EduCensus_Rapport_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            col_pdf.info("PDF : Installez 'reportlab'")
    else:
        st.info("💡 La base de données est vide. Remplissez le formulaire pour commencer le recensement.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
    <div style="text-align: center; padding-top: 20px; color: #94a3b8; font-size: 0.8rem;">
        © 2026 EduCensus Cameroun | Plateforme Nationale de Recensement Scolaire
    </div>
""", unsafe_allow_html=True)
