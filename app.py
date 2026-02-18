import streamlit as st
import pandas as pd
import datetime

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE
# ==============================================================================
st.set_page_config(
    page_title="ComptaxSolutions | Lease Valuation",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. DESIGN SYSTEM (CSS) - Injecté proprement
# ==============================================================================
# Cette méthode garantit que le CSS est chargé avant tout le reste
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap');

    /* Reset global */
    .stApp { background-color: #e0e5ec; font-family: 'Lato', sans-serif; }
    header, footer, #MainMenu { visibility: hidden; }
    
    /* Supprime les marges par défaut de Streamlit */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }

    /* La Feuille A4 */
    div.report-container {
        background-color: white;
        width: 21cm;
        min-height: 29.7cm;
        margin: auto;
        padding: 2cm;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        color: #1a1a1a;
        position: relative;
    }

    /* Typographie */
    h1.main-title { font-family: 'Playfair Display', serif; font-size: 26px; font-weight: 700; color: #1a1a1a; margin: 0; }
    div.sub-title { font-size: 10px; text-transform: uppercase; letter-spacing: 3px; color: #a38f60; margin-top: 5px; }
    h2.section-header { font-family: 'Playfair Display', serif; font-size: 18px; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-top: 30px; margin-bottom: 15px; }

    /* Grille Indices */
    div.grid-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-top: 15px;
    }
    div.grid-item {
        border: 1px solid #eee;
        padding: 15px;
        text-align: center;
    }
    div.grid-value { font-family: 'Playfair Display', serif; font-size: 16px; font-weight: bold; }
    div.grid-label { font-size: 9px; text-transform: uppercase; color: #666; margin-top: 5px; }

    /* Lignes de calcul */
    div.calc-line {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px dashed #eee;
        padding: 8px 0;
        font-size: 14px;
    }
    div.calc-total {
        display: flex;
        justify-content: space-between;
        border-top: 2px solid #1a1a1a;
        padding: 15px 0;
        font-weight: bold;
        font-size: 16px;
        margin-top: 10px;
    }

    /* Résultat Hero */
    div.hero-box {
        background-color: #f9f9f9;
        border: 1px solid #1a1a1a;
        text-align: center;
        padding: 30px;
        margin-top: 40px;
    }
    div.hero-amount { font-family: 'Playfair Display', serif; font-size: 42px; font-weight: 700; }
    
    /* Impression */
    @media print {
        .stApp { background-color: white; }
        section[data-testid="stSidebar"] { display: none; }
        div.report-container { box-shadow: none; margin: 0; padding: 0; width: 100%; }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. MOTEUR DE DONNÉES & CALCUL
# ==============================================================================

# Chargement robuste des données
@st.cache_data
def load_data():
    try:
        # Création d'un dataset par défaut si le fichier manque pour éviter le crash
        default_data = {
            "Trimestre": ["2026-T1", "2025-T4", "2025-T3", "2025-T2", "2025-T1", "2024-T4", "2024-T3", "2024-T2", "2024-T1", "2023-T4", "2023-T3", "2023-T2", "2023-T1", "2022-T4", "2022-T3", "2022-T2", "2022-T1", "2021-T4", "2021-T3", "2021-T2", "2021-T1"],
            "Indice": [137.0, 136.5, 136.0, 135.5, 135.0, 134.5, 134.0, 133.5, 132.91, 132.63, 132.78, 131.59, 130.69, 128.53, 126.98, 126.13, 124.83, 120.61, 119.7, 118.41, 118.57]
        }
        try:
            df = pd.read_excel("indices_ilc.xlsx")
            df.columns = ["Trimestre", "Indice"]
            df['Trimestre'] = df['Trimestre'].astype(str).str.strip()
            return df
        except:
            return pd.DataFrame(default_data)
    except: return pd.DataFrame()

df_indices = load_data()

# Fonctions utilitaires
def get_val(t):
    row = df_indices[df_indices["Trimestre"] == t]
    return row.iloc[0]["Indice"] if not row.empty else None

def get_date_offset(t, years):
    try:
        y, q = t.split('-T')
        return f"{int(y)-years}-T{q}"
    except: return None

# ==============================================================================
# 4. INTERFACE UTILISATEUR (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.header("Paramètres")
    loyer = st.number_input("Loyer Annuel (€)", value=2155.28, step=100.0)
    
    trimestres = df_indices["Trimestre"].tolist()
    # Tri inverse pour avoir le plus récent en haut
    if trimestres:
        t_rev = st.selectbox("Trimestre Révision", trimestres)
    else:
        st.error("Aucune donnée d'indice chargée.")
        st.stop()
    
    # Calculs auto dates
    t_ref = get_date_offset(t_rev, 3)
    t_n1 = get_date_offset(t_rev, 1)
    t_n2 = get_date_offset(t_rev, 2)
    
    # Récupération indices
    i_rev = get_val(t_rev)
    i_ref = get_val(t_ref)
    i_n1 = get_val(t_n1)
    i_n2 = get_val(t_n2)

# ==============================================================================
# 5. LOGIQUE MÉTIER
# ==============================================================================
if i_rev and i_ref:
    # Qualification
    y_float = int(t_rev.split('-')[0]) + (int(t_rev.split('T')[1])/10)
    
    cas = "D"
    txt_regime = "Droit Commun (L.145-37)"
    if 2022.2 <= y_float <= 2023.1: cas = "A"; txt_regime = "Dispositif Bouclier (Cas A)"
    elif 2023.2 <= y_float <= 2024.1: cas = "B"; txt_regime = "Dispositif Bouclier (Cas B)"
    elif 2024.2 <= y_float <= 2026.1: cas = "C"; txt_regime = "Dispositif Bouclier (Cas C)"

    # Glissement
    gliss = 0.0
    if cas == "C" and i_n1 and i_n2: gliss = (i_n1/i_n2)-1
    elif i_rev and i_n1: gliss = (i_rev/i_n1)-1
    
    plafonne = gliss >= 0.035
    txt_statut = "⚠️ PLAFONNÉ" if plafonne and cas != "D" else "✅ NON PLAFONNÉ"
    
    # Calcul Final & Étapes HTML
    res = 0.0
    html_lines = ""
    
    def add_line(lbl, val):
        return f'<div class="calc-line"><span>{lbl}</span><span>{val}</span></div>'

    if cas == "D":
        res = loyer * (i_rev/i_ref)
        html_lines += add_line("Loyer de Base", f"{loyer:,.2f} €")
        html_lines += add_line(f"Variation ({t_rev}/{t_ref})", f"{i_rev} / {i_ref}")
        
    elif cas == "A":
        html_lines += add_line("Loyer de Base", f"{loyer:,.2f} €")
        if plafonne:
            res = loyer * (i_n1/i_ref) * 1.035
            html_lines += add_line("Variation (N-1/Ref)", f"{i_n1}/{i_ref}")
            html_lines += add_line("Plafonnement", "+3.5%")
        else:
            res = loyer * (i_rev/i_ref)
            html_lines += add_line("Variation Réelle", f"{i_rev}/{i_ref}")

    elif cas == "B":
        html_lines += add_line("Loyer de Base", f"{loyer:,.2f} €")
        if plafonne:
            res = loyer * (i_n2/i_ref) * (1.035**2)
            html_lines += add_line("Variation (N-2/Ref)", f"{i_n2}/{i_ref}")
            html_lines += add_line("Double Plafond", "+7.12% (1.035²)")
        else:
            res = loyer * (i_n2/i_ref) * 1.035 * (i_rev/i_n1)
            html_lines += add_line("Formule Complexe", "Non plafonnée")

    elif cas == "C":
        html_lines += add_line("Loyer de Base", f"{loyer:,.2f} €")
        if plafonne:
            res = loyer * (1.035**2) * (i_rev/i_n1)
            html_lines += add_line("Double Plafond", "1.0712")
            html_lines += add_line("Variation (N/N-1)", f"{i_rev}/{i_n1}")
        else:
            res = loyer * 1.035 * (i_rev/i_n2)
            html_lines += add_line("Coeff 2023", "1.035")
            html_lines += add_line("Variation (N/N-2)", f"{i_rev}/{i_n2}")

    pct_evol = ((res/loyer)-1)*100
    date_jour = datetime.date.today().strftime('%d/%m/%Y')
    
    # Gestion des valeurs nulles pour affichage
    v_n2 = i_n2 if i_n2 else "-"
    v_n1 = i_n1 if i_n1 else "-"

    # ==========================================================================
    # 6. CONSTRUCTION DE LA PAGE HTML FINALE (Vraiment Propre)
    # ==========================================================================
    html_report = f"""
    <div class="report-container">
        <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2px solid #1a1a1a; padding-bottom:20px;">
            <div>
                <h1 class="main-title">ComptaxSolutions</h1>
                <div class="sub-title">Expertise Fiscale & Digitale</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:12px; color:#666;">CERTIFICAT DE RÉVISION</div>
                <div style="font-size:14px; font-weight:bold;">{date_jour}</div>
            </div>
        </div>

        <div style="margin-top:30px;">
            <h2 class="section-header">1. Contexte Juridique</h2>
            <div style="font-size:14px; line-height:1.5;">
                Révision triennale établie selon l'indice ILC du <b>{t_rev}</b>.<br>
                Régime applicable : <b>{txt_regime}</b><br>
                Statut du glissement : <b>{txt_statut}</b>
            </div>
        </div>

        <h2 class="section-header">2. Indices de Référence</h2>
        <div class="grid-container">
            <div class="grid-item" style="background-color:#f8f8f8;">
                <div class="grid-value">{i_ref}</div>
                <div class="grid-label">RÉF ({t_ref})</div>
            </div>
            <div class="grid-item">
                <div class="grid-value">{v_n2}</div>
                <div class="grid-label">N-2</div>
            </div>
            <div class="grid-item">
                <div class="grid-value">{v_n1}</div>
                <div class="grid-label">N-1</div>
            </div>
            <div class="grid-item" style="border-color:#1a1a1a;">
                <div class="grid-value">{i_rev}</div>
                <div class="grid-label" style="color:#1a1a1a; font-weight:bold;">RÉV ({t_rev})</div>
            </div>
        </div>

        <h2 class="section-header">3. Détail du Calcul</h2>
        <div style="margin-top:20px;">
            {html_lines}
            <div class="calc-total">
                <span>NOUVEAU LOYER ANNUEL</span>
                <span>{res:,.2f} €</span>
            </div>
        </div>

        <div class="hero-box">
            <div style="font-size:10px; text-transform:uppercase; letter-spacing:2px; color:#666; margin-bottom:10px;">Montant Révisé</div>
            <div class="hero-amount">{res:,.2f} €</div>
            <div style="margin-top:10px; font-size:12px; color:#666;">Évolution : {pct_evol:+.2f}%</div>
        </div>

        <div style="position:absolute; bottom:2cm; left:0; width:100%; text-align:center; font-size:10px; color:#999;">
            Document généré par l'algorithme ComptaxSolutions.
        </div>
    </div>
    """
    
    st.markdown(html_report, unsafe_allow_html=True)

else:
    st.warning("Données insuffisantes pour le calcul (Indices historiques manquants).")
