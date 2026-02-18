import streamlit as st
import pandas as pd
import datetime

# ==============================================================================
# 1. CONFIGURATION DU "COCKPIT"
# ==============================================================================
st.set_page_config(
    page_title="Lease Valuation | Premium Edition",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. DESIGN SYSTEM "TIER-1 CONSULTING" (CSS)
# ==============================================================================
st.markdown("""
    <style>
    /* IMPORTS FONTS LUXE */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

    :root {
        --primary: #1e293b;   /* Slate 800 - Le "Noir" Corporate */
        --gold: #b4975a;      /* Or brossé - Luxe discret */
        --paper: #ffffff;     /* Blanc pur */
        --bg: #f1f5f9;        /* Gris très léger pour le fond */
        --subtle: #94a3b8;    /* Gris texte secondaire */
    }

    /* STRUCTURE GÉNÉRALE */
    .stApp {
        background-color: var(--bg);
        font-family: 'Inter', sans-serif;
    }
    
    /* MASQUER LES ÉLÉMENTS STREAMLIT PAR DÉFAUT */
    #MainMenu, footer, header {visibility: hidden;}

    /* LA FEUILLE A4 (CONTAINER PRINCIPAL) */
    .report-sheet {
        background-color: var(--paper);
        max-width: 21cm; /* Largeur A4 */
        margin: 0 auto;
        padding: 40px 60px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.05);
        border-top: 5px solid var(--primary);
        min-height: 29.7cm; /* Hauteur A4 min */
    }

    /* TYPOGRAPHIE */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: var(--primary);
    }
    
    .report-title {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 5px;
    }
    
    .report-subtitle {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--gold);
        font-weight: 600;
    }

    /* CARTES KPI (LES INDICES) */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin: 30px 0;
        padding: 20px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 4px;
    }
    
    .kpi-item {
        text-align: center;
    }
    
    .kpi-val {
        font-size: 20px;
        font-weight: 600;
        color: var(--primary);
        font-family: 'Inter', sans-serif;
    }
    
    .kpi-label {
        font-size: 10px;
        text-transform: uppercase;
        color: var(--subtle);
        margin-top: 5px;
    }

    /* LE RÉSULTAT FINAL (HERO) */
    .result-hero {
        text-align: center;
        padding: 40px 0;
        margin: 30px 0;
        border-top: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .result-amount {
        font-size: 56px;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        color: var(--primary);
    }
    
    .result-caption {
        font-size: 12px;
        color: var(--subtle);
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* BADGES STATUT */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .status-warning { background: #fffbeb; color: #b45309; border: 1px solid #fcd34d; }
    .status-success { background: #f0fdf4; color: #15803d; border: 1px solid #86efac; }
    .status-neutral { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

    /* L'ACCORDÉON (EXPANDER) */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: var(--subtle);
        background-color: transparent;
        border: none;
    }
    
    /* IMPRESSION */
    @media print {
        .stApp { background: white; }
        section[data-testid="stSidebar"] { display: none; }
        .report-sheet { box-shadow: none; margin: 0; border-top: none; }
        .streamlit-expanderHeader { display: none; } /* On cache le bouton */
        .streamlit-expanderContent { display: block !important; height: auto !important; opacity: 1 !important; visibility: visible !important; } /* On force le contenu à s'afficher */
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. MOTEUR DE DONNÉES (ROBUSTE)
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

def get_indice(t):
    if df_indices.empty: return None
    r = df_indices[df_indices["Trimestre"] == t]
    return r.iloc[0]["Indice"] if not r.empty else None

def get_offset(t, years_back=0):
    try:
        p = t.split("-T")
        return f"{int(p[0]) - years_back}-T{int(p[1])}"
    except: return None

# ==============================================================================
# 4. SIDEBAR (PANNEAU DE CONTRÔLE)
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Paramètres du Bail")
    
    loyer_actuel = st.number_input(
        "Loyer Annuel Actuel (€)", 
        value=2155.28, step=100.0, format="%.2f"
    )
    
    if not df_indices.empty:
        liste_trimestres = df_indices["Trimestre"].tolist()[::-1]
        trimestre_rev = st.selectbox("Trimestre Révision (N)", liste_trimestres)
        
        # Auto-Calcul des dates
        trimestre_ref = get_offset(trimestre_rev, 3)
        trimestre_n1 = get_offset(trimestre_rev, 1)
        trimestre_n2 = get_offset(trimestre_rev, 2)
        
        # Récupération Indices
        ilc_rev = get_indice(trimestre_rev)
        ilc_ref = get_indice(trimestre_ref)
        ilc_n1 = get_indice(trimestre_n1)
        ilc_n2 = get_indice(trimestre_n2)

        st.success(f"🔗 Réf. Automatique (N-3) : **{trimestre_ref}**")
    else:
        st.error("Base de données manquante.")
        st.stop()

    st.markdown("---")
    st.caption("Pour imprimer le rapport officiel : `CTRL + P`")

# ==============================================================================
# 5. LOGIQUE JURIDIQUE (LE CERVEAU)
# ==============================================================================
if ilc_rev and ilc_ref:
    # 1. Qualification Période
    annee_float = int(trimestre_rev.split("-")[0]) + (int(trimestre_rev.split("-T")[1])/10)
    
    cas = "D"
    regime_label = "Droit Commun (Code de Commerce)"
    if 2022.2 <= annee_float <= 2023.1: 
        cas, regime_label = "A", "Loi Pouvoir d'Achat (Période A)"
    elif 2023.2 <= annee_float <= 2024.1: 
        cas, regime_label = "B", "Loi Pouvoir d'Achat (Période B)"
    elif 2024.2 <= annee_float <= 2026.1: 
        cas, regime_label = "C", "Loi Pouvoir d'Achat (Période C)"

    # 2. Calcul Glissement
    glissement = 0.0
    ref_gliss_txt = ""
    if cas == "C" and ilc_n1 and ilc_n2: 
        glissement = (ilc_n1 / ilc_n2) - 1
        ref_gliss_txt = "N-1 / N-2"
    elif ilc_rev and ilc_n1: 
        glissement = (ilc_rev / ilc_n1) - 1
        ref_gliss_txt = "N / N-1"
        
    is_plafonne = glissement >= 0.035
    
    # 3. Calcul Final
    nouveau_loyer = 0.0
    formule_tex = ""
    badge_html = ""
    
    if cas == "D":
        nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
        badge_html = '<span class="status-badge status-neutral">STANDARD</span>'
        formule_tex = r"L_{rev} = L_{act} \times \frac{ILC_{N}}{ILC_{ref}}"
    
    elif cas == "A":
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (ilc_n1 / ilc_ref) * 1.035
            badge_html = '<span class="status-badge status-warning">PLAFONNÉ (3.5%)</span>'
            formule_tex = r"L_{rev} = L_{act} \times \frac{ILC_{N-1}}{ILC_{ref}} \times 1,035"
        else:
            nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
            badge_html = '<span class="status-badge status-success">NON PLAFONNÉ</span>'
            formule_tex = r"L_{rev} = L_{act} \times \frac{ILC_{N}}{ILC_{ref}}"

    elif cas == "B":
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * (1.035**2)
            badge_html = '<span class="status-badge status-warning">DOUBLE PLAFOND (3.5%)</span>'
            formule_tex = r"L_{rev} = L_{act} \times \frac{ILC_{N-2}}{ILC_{ref}} \times (1,035)^2"
        else:
            nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * 1.035 * (ilc_rev / ilc_n1)
            badge_html = '<span class="status-badge status-success">COMPLEXE (NON PLAFONNÉ)</span>'
            formule_tex = r"L_{rev} = L_{act} \times \frac{ILC_{N-2}}{ILC_{ref}} \times 1,035 \times \frac{ILC_{N}}{ILC_{N-1}}"

    elif cas == "C":
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (1.035**2) * (ilc_rev / ilc_n1)
            badge_html = '<span class="status-badge status-warning">PLAFONNÉ (3.5%)</span>'
            formule_tex = r"L_{rev} = L_{act} \times (1,035)^2 \times \frac{ILC_{N}}{ILC_{N-1}}"
        else:
            nouveau_loyer = loyer_actuel * 1.035 * (ilc_rev / ilc_n2)
            badge_html = '<span class="status-badge status-success">NON PLAFONNÉ</span>'
            formule_tex = r"L_{rev} = L_{act} \times 1,035 \times \frac{ILC_{N}}{ILC_{N-2}}"

    # ==============================================================================
    # 6. VISUALISATION (LA FEUILLE A4)
    # ==============================================================================
    
    # Début du Container A4
    st.markdown('<div class="report-sheet">', unsafe_allow_html=True)

    # --- HEADER ---
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="report-subtitle">RAPPORT D\'EXPERTISE</div>', unsafe_allow_html=True)
        st.markdown('<div class="report-title">Révision Triennale ILC</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color:#64748B; font-size:14px;">Révision au titre du <b>{trimestre_rev}</b></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="text-align:right;">
            <div style="font-weight:bold; font-size:14px; color:#1e293b;">DATE D'ÉDITION</div>
            <div style="font-family:'Playfair Display'; font-size:18px;">{datetime.date.today().strftime('%d.%m.%Y')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- KPI GRID (INDICES) ---
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-item">
            <div class="kpi-val">{ilc_ref}</div>
            <div class="kpi-label">RÉFÉRENCE<br>({trimestre_ref})</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-val">{ilc_n2 if ilc_n2 else '-'}</div>
            <div class="kpi-label">INDICE<br>N-2</div>
        </div>
        <div class="kpi-item">
            <div class="kpi-val">{ilc_n1 if ilc_n1 else '-'}</div>
            <div class="kpi-label">INDICE<br>N-1</div>
        </div>
        <div class="kpi-item" style="border-left:1px solid #e2e8f0;">
            <div class="kpi-val" style="color:#b4975a;">{ilc_rev}</div>
            <div class="kpi-label" style="color:#b4975a;">RÉVISION<br>({trimestre_rev})</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- RÉSULTAT HERO ---
    st.markdown(f"""
    <div class="result-hero">
        <div class="result-caption">NOUVEAU LOYER ANNUEL (H.T. H.C.)</div>
        <div class="result-amount">{nouveau_loyer:,.2f} €</div>
        <div style="margin-top:10px;">{badge_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- AUDIT TRAIL (LE DÉTAIL DEROULANT) ---
    st.markdown("---")
    with st.expander("🔎 AUDITER LE CALCUL & LA FORMULE (CLIQUER POUR DÉROULER)", expanded=False):
        
        ec1, ec2 = st.columns(2)
        
        with ec1:
            st.markdown("#### 1. Qualification Juridique")
            st.markdown(f"""
            * **Régime :** {regime_label}
            * **Glissement pertinent ({ref_gliss_txt}) :** {glissement:.2%}
            * **Seuil Légal :** 3.50%
            """)
            if is_plafonne and cas != "D":
                st.warning("Le glissement dépasse 3.5%. Le mécanisme de plafonnement s'active pour protéger le locataire.")
            else:
                st.info("Le glissement est conforme ou le régime ne prévoit pas de plafonnement.")

        with ec2:
            st.markdown("#### 2. Formule Mathématique")
            st.latex(formule_tex)
            st.markdown("**Vérification Numérique :**")
            st.code(f"Calcul = {nouveau_loyer:.4f} €")

    # --- FOOTER ---
    st.markdown("""
    <div style="text-align:center; margin-top:40px; font-size:10px; color:#cbd5e1;">
        DOCUMENT GÉNÉRÉ PAR TAX-TECH SOLUTIONS • STRICTEMENT CONFIDENTIEL
    </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # --- ECRAN D'ACCUEIL (SI PAS DE DONNEES) ---
    st.info("Veuillez configurer les paramètres dans le panneau latéral pour générer le rapport.")
