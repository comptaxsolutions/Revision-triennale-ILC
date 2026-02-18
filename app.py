import streamlit as st
import pandas as pd
import datetime

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="ComptaxSolutions | Lease Valuation", page_icon="🏛️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap');
    .stApp { background-color: #e0e5ec; font-family: 'Lato', sans-serif; }
    header, footer, #MainMenu { visibility: hidden; }
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }
    
    /* FEUILLE A4 */
    div.report-container {
        background-color: white; width: 21cm; min-height: 29.7cm; margin: auto;
        padding: 2cm; box-shadow: 0 10px 25px rgba(0,0,0,0.1); color: #1a1a1a;
    }
    
    h1.main-title { font-family: 'Playfair Display', serif; font-size: 26px; font-weight: 700; color: #1a1a1a; margin: 0; }
    div.sub-title { font-size: 10px; text-transform: uppercase; letter-spacing: 3px; color: #a38f60; margin-top: 5px; }
    h2.section-header { font-family: 'Playfair Display', serif; font-size: 18px; border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-top: 30px; }
    
    /* GRIDS & BOXES */
    div.grid-container { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 15px; }
    div.grid-item { border: 1px solid #eee; padding: 15px; text-align: center; }
    div.grid-value { font-family: 'Playfair Display', serif; font-size: 16px; font-weight: bold; }
    div.grid-label { font-size: 9px; text-transform: uppercase; color: #666; margin-top: 5px; }
    
    div.calc-line { display: flex; justify-content: space-between; border-bottom: 1px dashed #eee; padding: 8px 0; font-size: 14px; }
    div.calc-total { display: flex; justify-content: space-between; border-top: 2px solid #1a1a1a; padding: 15px 0; font-weight: bold; font-size: 16px; margin-top: 10px; }
    
    div.hero-box { background-color: #f9f9f9; border: 1px solid #1a1a1a; text-align: center; padding: 30px; margin-top: 40px; }
    div.hero-amount { font-family: 'Playfair Display', serif; font-size: 42px; font-weight: 700; }
    
    @media print {
        .stApp { background-color: white; }
        section[data-testid="stSidebar"] { display: none; }
        div.report-container { box-shadow: none; margin: 0; padding: 0; width: 100%; }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DONNÉES
# ==============================================================================
@st.cache_data
def load_data():
    try:
        # On force la lecture en string pour éviter les problèmes de format date Excel
        df = pd.read_excel("indices_ilc.xlsx", dtype=str)
        df.columns = ["Trimestre", "Indice"]
        # Nettoyage et conversion
        df['Trimestre'] = df['Trimestre'].astype(str).str.strip()
        # On remplace les virgules par des points si l'excel est en format FR
        df['Indice'] = df['Indice'].astype(str).str.replace(',', '.').astype(float)
        return df
    except Exception as e:
        return pd.DataFrame() # Retourne vide si erreur

df_indices = load_data()

def get_val(t):
    if df_indices.empty: return None
    row = df_indices[df_indices["Trimestre"] == t]
    return row.iloc[0]["Indice"] if not row.empty else None

def get_date_offset(t, years):
    try:
        # Gestion robuste du format YYYY-TX ou YYYY-QX
        parts = t.replace('Q', 'T').split('-T')
        y, q = int(parts[0]), int(parts[1])
        return f"{y-years}-T{q}"
    except: return "Erreur Format"

# ==============================================================================
# 3. SIDEBAR & DEBUG
# ==============================================================================
with st.sidebar:
    st.header("Paramètres")
    loyer = st.number_input("Loyer Annuel (€)", value=2155.28, step=100.0)
    
    if not df_indices.empty:
        trimestres = df_indices["Trimestre"].tolist()
        t_rev = st.selectbox("Trimestre Révision", trimestres)
    else:
        st.error("❌ Fichier Excel illisible ou manquant.")
        st.stop()
    
    # Calcul des cibles
    t_ref = get_date_offset(t_rev, 3)
    t_n1 = get_date_offset(t_rev, 1)
    t_n2 = get_date_offset(t_rev, 2)
    
    # Récupération valeurs
    i_rev = get_val(t_rev)
    i_ref = get_val(t_ref)
    i_n1 = get_val(t_n1)
    i_n2 = get_val(t_n2)
    
    # --- PANNEAU DE DIAGNOSTIC ---
    with st.expander("🕵️ Diagnostic Données", expanded=True):
        if i_ref is None:
            st.error(f"❌ Manquant: {t_ref}")
            st.caption("Le calcul exige l'indice d'il y a 3 ans.")
        else:
            st.success(f"✅ Trouvé: {t_ref} ({i_ref})")
            
        if i_rev is None: st.error(f"❌ Indice {t_rev} vide")

# ==============================================================================
# 4. LOGIQUE
# ==============================================================================
if i_rev and i_ref:
    # Qualification
    y_float = int(t_rev.split('-')[0]) + (int(t_rev.split('T')[1])/10)
    
    cas, txt_regime = "D", "Droit Commun (L.145-37)"
    if 2022.2 <= y_float <= 2023.1: cas, txt_regime = "A", "Dispositif Bouclier (Cas A)"
    elif 2023.2 <= y_float <= 2024.1: cas, txt_regime = "B", "Dispositif Bouclier (Cas B)"
    elif 2024.2 <= y_float <= 2026.1: cas, txt_regime = "C", "Dispositif Bouclier (Cas C)"

    # Glissement
    gliss = 0.0
    if cas == "C" and i_n1 and i_n2: gliss = (i_n1/i_n2)-1
    elif i_rev and i_n1: gliss = (i_rev/i_n1)-1
    
    plafonne = gliss >= 0.035
    txt_statut = "⚠️ PLAFONNÉ" if plafonne and cas != "D" else "✅ NON PLAFONNÉ"
    
    # Calcul
    res, html_lines = 0.0, ""
    def add_line(lbl, val): return f'<div class="calc-line"><span>{lbl}</span><span>{val}</span></div>'

    if cas == "D":
        res = loyer * (i_rev/i_ref)
        html_lines += add_line("Loyer Base", f"{loyer:,.2f} €") + add_line(f"Variation ({t_rev}/{t_ref})", f"{i_rev} / {i_ref}")
    elif cas == "A":
        if plafonne:
            res = loyer * (i_n1/i_ref) * 1.035
            html_lines += add_line("Variation (N-1/Ref)", f"{i_n1}/{i_ref}") + add_line("Plafonnement", "+3.5%")
        else:
            res = loyer * (i_rev/i_ref)
            html_lines += add_line("Variation Réelle", f"{i_rev}/{i_ref}")
    elif cas == "B":
        if plafonne:
            res = loyer * (i_n2/i_ref) * (1.035**2)
            html_lines += add_line("Variation (N-2/Ref)", f"{i_n2}/{i_ref}") + add_line("Double Plafond", "1.035²")
        else:
            res = loyer * (i_n2/i_ref) * 1.035 * (i_rev/i_n1)
            html_lines += add_line("Formule Complexe", "Non plafonnée")
    elif cas == "C":
        if plafonne:
            res = loyer * (1.035**2) * (i_rev/i_n1)
            html_lines += add_line("Double Plafond", "1.0712") + add_line("Variation (N/N-1)", f"{i_rev}/{i_n1}")
        else:
            res = loyer * 1.035 * (i_rev/i_n2)
            html_lines += add_line("Coeff 2023", "1.035") + add_line("Variation (N/N-2)", f"{i_rev}/{i_n2}")

    # Rendu HTML
    date_jour = datetime.date.today().strftime('%d/%m/%Y')
    v_n2 = i_n2 if i_n2 else "-"
    v_n1 = i_n1 if i_n1 else "-"
    
    html_report = f"""
    <div class="report-container">
        <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2px solid #1a1a1a; padding-bottom:20px;">
            <div><h1 class="main-title">ComptaxSolutions</h1><div class="sub-title">Expertise Fiscale & Digitale</div></div>
            <div style="text-align:right;"><div style="font-size:12px; color:#666;">CERTIFICAT DE RÉVISION</div><div style="font-size:14px; font-weight:bold;">{date_jour}</div></div>
        </div>

        <div style="margin-top:30px;">
            <h2 class="section-header">1. Contexte Juridique</h2>
            <div style="font-size:14px; line-height:1.5;">Révision triennale au <b>{t_rev}</b>.<br>Régime : <b>{txt_regime}</b><br>Statut : <b>{txt_statut}</b></div>
        </div>

        <h2 class="section-header">2. Indices ILC</h2>
        <div class="grid-container">
            <div class="grid-item" style="background:#f8f8f8;"><div class="grid-value">{i_ref}</div><div class="grid-label">RÉF ({t_ref})</div></div>
            <div class="grid-item"><div class="grid-value">{v_n2}</div><div class="grid-label">N-2</div></div>
            <div class="grid-item"><div class="grid-value">{v_n1}</div><div class="grid-label">N-1</div></div>
            <div class="grid-item" style="border-color:#1a1a1a;"><div class="grid-value">{i_rev}</div><div class="grid-label" style="color:#1a1a1a; font-weight:bold;">RÉV ({t_rev})</div></div>
        </div>

        <h2 class="section-header">3. Détail du Calcul</h2>
        <div style="margin-top:20px;">{html_lines}<div class="calc-total"><span>NOUVEAU LOYER</span><span>{res:,.2f} €</span></div></div>

        <div class="hero-box">
            <div style="font-size:10px; text-transform:uppercase; letter-spacing:2px; color:#666;">Montant Révisé</div>
            <div class="hero-amount">{res:,.2f} €</div>
        </div>
        
        <div style="position:absolute; bottom:2cm; width:calc(100% - 4cm); text-align:center; font-size:10px; color:#999;">Généré par ComptaxSolutions</div>
    </div>
    """
    st.markdown(html_report, unsafe_allow_html=True)

else:
    st.warning("⚠️ En attente de données historiques. Vérifiez le panneau latéral 'Diagnostic'.")
