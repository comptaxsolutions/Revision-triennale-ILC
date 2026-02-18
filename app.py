import streamlit as st
import pandas as pd
import datetime

# ==============================================================================
# 1. CONFIGURATION "LUXURY"
# ==============================================================================
st.set_page_config(
    page_title="Lease Analytics | Révision ILC",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. DESIGN SYSTEM (CSS AVANCÉ & PRINT)
# ==============================================================================
st.markdown("""
    <style>
    /* --- FONTS & COLORS --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:wght@700&display=swap');
    
    :root {
        --primary: #0F172A; /* Navy Blue Profond */
        --accent: #D4AF37; /* Or Métallique */
        --bg-color: #F8FAFC; /* Gris très pâle */
        --card-bg: #FFFFFF;
        --text-main: #334155;
    }

    /* --- GENERAL LAYOUT --- */
    .stApp {
        background-color: var(--bg-color);
        font-family: 'Inter', sans-serif;
    }
    
    /* Cacher les éléments Streamlit par défaut */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* --- SIDEBAR (CONTROLE) --- */
    section[data-testid="stSidebar"] {
        background-color: var(--card-bg);
        border-right: 1px solid #E2E8F0;
        box-shadow: 4px 0 24px rgba(0,0,0,0.02);
    }
    
    /* --- TITRES --- */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif; /* Font "Luxe" */
        color: var(--primary);
    }
    
    /* --- CARTE "DOCUMENT" (Le coeur de l'app) --- */
    .report-container {
        background-color: white;
        padding: 60px;
        border-radius: 2px; /* Style feuille A4 */
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        max-width: 900px;
        margin: auto;
        border-top: 6px solid var(--accent);
    }
    
    .report-header {
        border-bottom: 2px solid #F1F5F9;
        padding-bottom: 20px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .metric-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--primary);
    }
    
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748B;
        margin-top: 5px;
    }

    /* --- LE RÉSULTAT FINAL --- */
    .final-result-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: white;
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        margin-top: 30px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.2);
    }
    
    .gold-text {
        color: var(--accent);
        font-weight: bold;
    }

    /* --- PRINT CSS (LA MAGIE) --- */
    @media print {
        /* Cacher tout ce qui n'est pas le rapport */
        section[data-testid="stSidebar"] { display: none !important; }
        .stApp { background-color: white !important; }
        header, footer, .stDeployButton { display: none !important; }
        
        /* Ajuster le rapport pour le papier */
        .report-container {
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            width: 100% !important;
            max-width: 100% !important;
        }
        
        /* Cacher les boutons d'aide/expanders si on veut une version clean */
        .streamlit-expanderHeader { display: none; }
        .streamlit-expanderContent { display: block !important; border: none !important; }
        
        body {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. MOTEUR DE DONNÉES & LOGIQUE (ROBUSTE)
# ==============================================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("indices_ilc.xlsx")
        df.columns = ["Trimestre", "Indice"]
        df['Trimestre'] = df['Trimestre'].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

df_indices = load_data()

def get_indice_value(t):
    if df_indices.empty: return None
    r = df_indices[df_indices["Trimestre"] == t]
    return r.iloc[0]["Indice"] if not r.empty else None

def get_offset_trimestre(t, years_back=0):
    try:
        p = t.split("-T")
        return f"{int(p[0]) - years_back}-T{int(p[1])}"
    except: return None

# ==============================================================================
# 4. SIDEBAR (PANNEAU DE CONTRÔLE)
# ==============================================================================

with st.sidebar:
    st.markdown("## ⚙️ Paramètres")
    st.markdown("---")
    
    # Input Stylisé
    loyer_actuel = st.number_input(
        "Loyer Annuel Actuel (€)", 
        value=2155.28, step=100.0, format="%.2f",
        help="Montant H.T. H.C. avant révision"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not df_indices.empty:
        liste_trimestres = df_indices["Trimestre"].tolist()[::-1]
        trimestre_rev = st.selectbox("Trimestre de Révision (N)", liste_trimestres)
        
        # Logique Auto
        trimestre_ref_auto = get_offset_trimestre(trimestre_rev, years_back=3)
        ilc_rev = get_indice_value(trimestre_rev)
        ilc_ref = get_indice_value(trimestre_ref_auto)
        
        st.markdown(f"""
        <div style="background:#F1F5F9; padding:10px; border-radius:5px; font-size:0.85rem; color:#475569;">
            <strong>🔗 Auto-Link :</strong><br>
            Le trimestre de référence a été fixé automatiquement au <b>{trimestre_ref_auto}</b> (N-3).
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.error("Base de données indices manquante.")
        st.stop()

    st.markdown("---")
    st.info("💡 **Astuce Pro :** Pour imprimer le rapport ou l'enregistrer en PDF, faites `CTRL + P` (ou `CMD + P` sur Mac).")

# ==============================================================================
# 5. MOTEUR DE CALCUL (BACKEND)
# ==============================================================================
if ilc_rev and ilc_ref:
    # Indices intermédiaires
    trimestre_n1 = get_offset_trimestre(trimestre_rev, years_back=1)
    trimestre_n2 = get_offset_trimestre(trimestre_rev, years_back=2)
    ilc_n1 = get_indice_value(trimestre_n1)
    ilc_n2 = get_indice_value(trimestre_n2)
    
    # Qualification Juridique
    annee_float = int(trimestre_rev.split("-")[0]) + (int(trimestre_rev.split("-T")[1])/10)
    
    cas = "D"
    if 2022.2 <= annee_float <= 2023.1: cas = "A"
    elif 2023.2 <= annee_float <= 2024.1: cas = "B"
    elif 2024.2 <= annee_float <= 2026.1: cas = "C"
    
    # Calcul Glissement
    glissement = 0.0
    if cas == "C" and ilc_n1 and ilc_n2: glissement = (ilc_n1 / ilc_n2) - 1
    elif ilc_rev and ilc_n1: glissement = (ilc_rev / ilc_n1) - 1
        
    is_plafonne = glissement >= 0.035
    
    # Calcul Final & Textes
    nouveau_loyer = 0.0
    titre_regime = ""
    badge_html = ""
    formule_tex = ""
    
    if cas == "D":
        nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
        titre_regime = "Droit Commun (Code de Commerce)"
        badge_html = "<span style='color:#64748B;'>Standard</span>"
        formule_tex = r"L_{rev} = L_{act} \times \frac{ILC_{N}}{ILC_{ref}}"
    
    elif cas == "A":
        titre_regime = "Loi Pouvoir d'Achat (Cas A)"
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (ilc_n1 / ilc_ref) * 1.035
            badge_html = "<span style='color:#D97706;'>⚠️ Plafonné</span>"
            formule_tex = r"L_{rev} = L_{act} \times \frac{ILC_{N-1}}{ILC_{ref}} \times 1,035"
        else:
            nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
            badge_html = "<span style='color:#059669;'>Non Plafonné</span>"
            formule_tex = r"L_{rev} = L_{act} \times \frac{ILC_{N}}{ILC_{ref}}"

    elif cas == "B":
        titre_regime = "Loi Pouvoir d'Achat (Cas B)"
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * (1.035**2)
            badge_html = "<span style='color:#D97706;'>⚠️ Plafonné (Double)</span>"
            formule_tex = r"L_{rev} = L_{act} \times \frac{ILC_{N-2}}{ILC_{ref}} \times (1,035)^2"
        else:
            nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * 1.035 * (ilc_rev / ilc_n1)
            badge_html = "<span style='color:#059669;'>Complexe</span>"
            formule_tex = r"L_{rev} = L_{act} \times \frac{ILC_{N-2}}{ILC_{ref}} \times 1,035 \times \frac{ILC_{N}}{ILC_{N-1}}"

    elif cas == "C":
        titre_regime = "Loi Pouvoir d'Achat (Cas C)"
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (1.035**2) * (ilc_rev / ilc_n1)
            badge_html = "<span style='color:#D97706;'>⚠️ Plafonné</span>"
            formule_tex = r"L_{rev} = L_{act} \times (1,035)^2 \times \frac{ILC_{N}}{ILC_{N-1}}"
        else:
            nouveau_loyer = loyer_actuel * 1.035 * (ilc_rev / ilc_n2)
            badge_html = "<span style='color:#059669;'>Non Plafonné</span>"
            formule_tex = r"L_{rev} = L_{act} \times 1,035 \times \frac{ILC_{N}}{ILC_{N-2}}"

# ==============================================================================
# 6. VISUALISATION (LA PAGE A4 VIRTUELLE)
# ==============================================================================

# On centre tout dans une "feuille" blanche
st.markdown('<div class="report-container">', unsafe_allow_html=True)

# --- Header du Rapport ---
st.markdown(f"""
<div class="report-header">
    <div>
        <h1 style="margin:0; font-size:24px;">CERTIFICAT DE RÉVISION</h1>
        <p style="margin:0; color:#64748B;">Baux Commerciaux & Professionnels</p>
    </div>
    <div style="text-align:right;">
        <p style="margin:0; font-weight:bold;">Date : {datetime.date.today().strftime('%d/%m/%Y')}</p>
        <p style="margin:0; font-size:12px; color:#94A3B8;">Réf Dossier : REV-{trimestre_rev}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Grille des Indices ---
st.markdown("### 1. Données de Référence")
st.markdown("<br>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-value">{ilc_ref}</div>
        <div class="metric-label">Réf ({trimestre_ref_auto})</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-value">{ilc_n2 if ilc_n2 else '-'}</div>
        <div class="metric-label">Indice N-2</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-value">{ilc_n1 if ilc_n1 else '-'}</div>
        <div class="metric-label">Indice N-1</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-box" style="border-color:var(--accent); background:#FFFAF0;">
        <div class="metric-value" style="color:var(--accent);">{ilc_rev}</div>
        <div class="metric-label" style="color:#B7950B;">Révision ({trimestre_rev})</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- Analyse Juridique ---
st.markdown("### 2. Analyse Juridique & Calcul")
st.markdown(f"""
<div style="padding: 20px; border-left: 4px solid var(--primary); background: #F8FAFC;">
    <p style="margin:0; font-weight:600; font-size:1.1rem;">Régime Applicable : {titre_regime}</p>
    <p style="margin-top:5px; margin-bottom:15px;">Statut Plafonnement : {badge_html}</p>
    <p style="font-style:italic; color:#475569;">
        Le glissement annuel de l'indice pertinent s'établit à <b>{glissement:.2%}</b>.
        {"Le seuil légal de 3,5% est dépassé, déclenchant le mécanisme de bouclier." if is_plafonne and cas != 'D' else "Ce taux reste inférieur ou égal au plafond légal (ou hors champ d'application)."}
    </p>
</div>
""", unsafe_allow_html=True)

# Affichage formule LaTeX propre
st.markdown("<br>", unsafe_allow_html=True)
st.latex(formule_tex)

# --- Résultat Final ---
st.markdown(f"""
<div class="final-result-box">
    <p style="margin:0; font-size:14px; text-transform:uppercase; letter-spacing:2px; opacity:0.8;">Nouveau Loyer Annuel</p>
    <p style="margin:10px 0; font-size:42px; font-weight:700; font-family:'Playfair Display';">{nouveau_loyer:,.2f} €</p>
    <p style="margin:0; font-size:14px; opacity:0.8;">(Hors Taxes & Hors Charges)</p>
</div>
""", unsafe_allow_html=True)

# --- Footer du rapport ---
st.markdown("""
<div style="margin-top:50px; text-align:center; font-size:10px; color:#CBD5E1;">
    <p>Document généré automatiquement par Lease Analytics Tech. Valeur informative.</p>
</div>
</div>
""", unsafe_allow_html=True) # Fin du container rapport
