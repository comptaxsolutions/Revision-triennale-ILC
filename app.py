import streamlit as st
import pandas as pd
import datetime

# ==============================================================================
# 1. CONFIGURATION DU STYLE (CSS GLOBAL)
# ==============================================================================
st.set_page_config(
    page_title="ComptaxSolutions | Lease Valuation",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nous définissons le CSS dans une variable séparée pour éviter les bugs d'indentation
CSS_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap');

:root {
    --bg-app: #e0e5ec;
    --paper: #ffffff;
    --ink: #1a1a1a;
    --gold: #a38f60;
    --subtle: #666666;
    --border: #dcdcdc;
}

/* Force le fond d'écran et la police */
.stApp { background-color: var(--bg-app); font-family: 'Lato', sans-serif; }

/* Cache les éléments parasites de Streamlit */
header, footer, #MainMenu { visibility: hidden; }
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* LA FEUILLE A4 */
.a4-sheet {
    background-color: var(--paper);
    width: 21cm;
    min-height: 29.7cm;
    margin: 0 auto;
    padding: 2cm;
    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    color: var(--ink);
    position: relative;
}

/* TYPOGRAPHIE */
h1.doc-title { font-family: 'Playfair Display', serif; font-size: 28px; color: var(--ink); margin: 0; padding: 0; border: none; }
.doc-subtitle { font-family: 'Lato', sans-serif; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: var(--gold); margin-top: 0; }
h3.section-title { font-family: 'Playfair Display', serif; font-size: 18px; color: var(--ink); margin-top: 30px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }

/* GRILLE INDICES */
.data-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px; }
.data-box { border: 1px solid var(--border); padding: 15px; text-align: center; }
.data-val { font-size: 16px; font-weight: bold; font-family: 'Playfair Display', serif; }
.data-lbl { font-size: 9px; text-transform: uppercase; color: var(--subtle); margin-top: 5px; }

/* RESULTAT */
.hero-result { background-color: #f9f9f9; border: 1px solid var(--ink); padding: 30px; text-align: center; margin: 30px 0; }
.hero-amount { font-family: 'Playfair Display', serif; font-size: 48px; font-weight: 700; color: var(--ink); }
.hero-lbl { font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: var(--subtle); }

/* LIGNES DE CALCUL */
.calc-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed var(--border); font-size: 14px; }
.calc-total { display: flex; justify-content: space-between; padding: 15px 0; font-weight: bold; border-top: 2px solid var(--ink); margin-top: 10px; font-size: 16px; }
.math-formula { font-family: 'Courier New', monospace; background: #f4f4f4; padding: 10px; font-size: 12px; color: #333; margin: 10px 0; }

/* MODE IMPRESSION (CTRL+P) */
@media print {
    .stApp { background-color: white; }
    section[data-testid="stSidebar"] { display: none; }
    .a4-sheet { box-shadow: none; margin: 0; width: 100%; padding: 0; }
    .block-container { padding: 0 !important; }
}
</style>
"""

# Injection immédiate du CSS
st.markdown(CSS_STYLE, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DES DONNÉES
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
# 3. INTERFACE DE CONTRÔLE (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Paramètres")
    loyer_actuel = st.number_input("Loyer Annuel (€)", value=2155.28, step=100.0, format="%.2f")
    
    selected_trimestre = None
    if not df_indices.empty:
        liste_trimestres = df_indices["Trimestre"].tolist()[::-1]
        selected_trimestre = st.selectbox("Trimestre Révision", liste_trimestres)
    else:
        st.error("Fichier 'indices_ilc.xlsx' introuvable.")
        st.stop()

# ==============================================================================
# 4. MOTEUR DE CALCUL (LOGIQUE PURE)
# ==============================================================================
def calculate_revision(loyer, trimestre_rev):
    # Récupération des dates
    trimestre_ref = get_offset(trimestre_rev, 3)
    trimestre_n1 = get_offset(trimestre_rev, 1)
    trimestre_n2 = get_offset(trimestre_rev, 2)
    
    # Récupération des indices
    ilc_rev = get_indice(trimestre_rev)
    ilc_ref = get_indice(trimestre_ref)
    ilc_n1 = get_indice(trimestre_n1)
    ilc_n2 = get_indice(trimestre_n2)
    
    if not ilc_ref: return None # Pas assez d'historique
    
    # Qualification Juridique
    annee_float = int(trimestre_rev.split("-")[0]) + (int(trimestre_rev.split("-T")[1])/10)
    cas = "D"
    regime = "Droit Commun (Code de Commerce L.145-37)"
    
    if 2022.2 <= annee_float <= 2023.1: cas, regime = "A", "Dispositif Bouclier Loyer (Période A)"
    elif 2023.2 <= annee_float <= 2024.1: cas, regime = "B", "Dispositif Bouclier Loyer (Période B)"
    elif 2024.2 <= annee_float <= 2026.1: cas, regime = "C", "Dispositif Bouclier Loyer (Période C)"

    # Glissement
    glissement = 0.0
    if cas == "C" and ilc_n1 and ilc_n2: glissement = (ilc_n1 / ilc_n2) - 1
    elif ilc_rev and ilc_n1: glissement = (ilc_rev / ilc_n1) - 1
    
    is_plafonne = glissement >= 0.035
    
    # Calcul
    nouveau_loyer = 0.0
    steps = []
    formule = ""
    
    if cas == "D":
        nouveau_loyer = loyer * (ilc_rev / ilc_ref)
        steps.append(("Loyer de Base", f"{loyer:,.2f} €", False))
        steps.append(("x Indice Révision / Réf", f"{ilc_rev} / {ilc_ref}", False))
        formule = f"{loyer:.2f} × ({ilc_rev} ÷ {ilc_ref})"
        
    elif cas == "A":
        if is_plafonne:
            nouveau_loyer = loyer * (ilc_n1 / ilc_ref) * 1.035
            steps.append(("Loyer de Base", f"{loyer:,.2f} €", False))
            steps.append(("x Variation (N-1/Ref)", f"{ilc_n1} / {ilc_ref}", False))
            steps.append(("x Plafonnement", "1.035", True))
            formule = f"{loyer:.2f} × ({ilc_n1} ÷ {ilc_ref}) × 1.035"
        else:
            nouveau_loyer = loyer * (ilc_rev / ilc_ref)
            steps.append(("Loyer de Base", f"{loyer:,.2f} €", False))
            steps.append(("x Variation (N/Ref)", f"{ilc_rev} / {ilc_ref}", False))
            formule = f"{loyer:.2f} × ({ilc_rev} ÷ {ilc_ref})"
            
    elif cas == "B":
        if is_plafonne:
            nouveau_loyer = loyer * (ilc_n2 / ilc_ref) * (1.035**2)
            steps.append(("Loyer de Base", f"{loyer:,.2f} €", False))
            steps.append(("x Variation (N-2/Ref)", f"{ilc_n2} / {ilc_ref}", False))
            steps.append(("x Double Plafond", "1.0712 (1.035²)", True))
            formule = f"{loyer:.2f} × ({ilc_n2} ÷ {ilc_ref}) × 1.035²"
        else:
            nouveau_loyer = loyer * (ilc_n2 / ilc_ref) * 1.035 * (ilc_rev / ilc_n1)
            steps.append(("Loyer de Base", f"{loyer:,.2f} €", False))
            steps.append(("x Variation (N-2/Ref)", f"{ilc_n2} / {ilc_ref}", False))
            steps.append(("x Coeff 2023", "1.035", False))
            steps.append(("x Variation (N/N-1)", f"{ilc_rev} / {ilc_n1}", False))
            formule = "Formule complexe Cas B (Non plafonné)"

    elif cas == "C":
        if is_plafonne:
            nouveau_loyer = loyer * (1.035**2) * (ilc_rev / ilc_n1)
            steps.append(("Loyer de Base", f"{loyer:,.2f} €", False))
            steps.append(("x Double Plafond", "1.0712", True))
            steps.append(("x Variation (N/N-1)", f"{ilc_rev} / {ilc_n1}", False))
            formule = f"{loyer:.2f} × 1.035² × ({ilc_rev} ÷ {ilc_n1})"
        else:
            nouveau_loyer = loyer * 1.035 * (ilc_rev / ilc_n2)
            steps.append(("Loyer de Base", f"{loyer:,.2f} €", False))
            steps.append(("x Coeff 2023", "1.035", False))
            steps.append(("x Variation (N/N-2)", f"{ilc_rev} / {ilc_n2}", False))
            formule = f"{loyer:.2f} × 1.035 × ({ilc_rev} ÷ {ilc_n2})"

    return {
        "indices": {"ref": ilc_ref, "rev": ilc_rev, "n1": ilc_n1, "n2": ilc_n2},
        "dates": {"ref": trimestre_ref, "rev": trimestre_rev},
        "result": {"montant": nouveau_loyer, "evolution": ((nouveau_loyer/loyer)-1)*100},
        "juridique": {"regime": regime, "plafonne": is_plafonne, "cas": cas},
        "detail": {"steps": steps, "formule": formule}
    }

# ==============================================================================
# 5. GÉNÉRATION DE LA VUE (HTML)
# ==============================================================================
data = calculate_revision(loyer_actuel, selected_trimestre)

if data:
    # Préparation des variables d'affichage
    date_jour = datetime.date.today().strftime('%d/%m/%Y')
    status_icon = "⚠️" if data['juridique']['plafonne'] and data['juridique']['cas'] != 'D' else "✅"
    status_text = "Plafonnement Activé" if data['juridique']['plafonne'] and data['juridique']['cas'] != 'D' else "Indice Réel (Non Plafonné)"
    
    # Construction des lignes de calcul HTML
    html_steps = ""
    for label, val, bold in data['detail']['steps']:
        weight = "font-weight:bold;" if bold else ""
        html_steps += f'<div class="calc-row"><span style="{weight}">{label}</span><span>{val}</span></div>'

    # Construction des indices HTML (gestion des valeurs nulles)
    val_n2 = data['indices']['n2'] if data['indices']['n2'] else '-'
    val_n1 = data['indices']['n1'] if data['indices']['n1'] else '-'

    # --- LE BLOC HTML FINAL (SANS INDENTATION) ---
    # Note : Tout est concaténé pour éviter que Markdown n'interprète des espaces comme du code.
    html_content = f"""
<div class="a4-sheet">
    <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2px solid #1a1a1a; padding-bottom:15px;">
        <div>
            <h1 class="doc-title">ComptaxSolutions</h1>
            <div class="doc-subtitle">Expertise Fiscale & Digitale</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:12px;">CERTIFICAT DE RÉVISION</div>
            <div style="font-size:12px; font-weight:bold;">{date_jour}</div>
        </div>
    </div>

    <div style="margin-top:30px;">
        <h3 class="section-title">1. Contexte de la Révision</h3>
        <div style="font-size:14px; margin-top:10px;">
            Conformément aux dispositions du bail et à l'article L.145-37 du Code de commerce, 
            la révision triennale s'opère sur la base de l'indice ILC du <b>{data['dates']['rev']}</b>.
        </div>
        <div style="margin-top:15px; background:#f4f4f4; padding:10px; font-size:13px; border-left:4px solid #a38f60;">
            <strong>Régime Juridique Identifié :</strong> {data['juridique']['regime']}<br>
            <em>Statut : {status_icon} {status_text}</em>
        </div>
    </div>

    <h3 class="section-title">2. Indices de Référence (ILC)</h3>
    <div class="data-grid">
        <div class="data-box">
            <div class="data-val">{data['indices']['ref']}</div>
            <div class="data-lbl">RÉFÉRENCE<br>{data['dates']['ref']}</div>
        </div>
        <div class="data-box" style="background:#fcfcfc; color:#999;">
            <div class="data-val">{val_n2}</div>
            <div class="data-lbl">INDICE N-2</div>
        </div>
        <div class="data-box" style="background:#fcfcfc; color:#999;">
            <div class="data-val">{val_n1}</div>
            <div class="data-lbl">INDICE N-1</div>
        </div>
        <div class="data-box" style="border-color:#1a1a1a;">
            <div class="data-val">{data['indices']['rev']}</div>
            <div class="data-lbl" style="color:#1a1a1a; font-weight:bold;">RÉVISION<br>{data['dates']['rev']}</div>
        </div>
    </div>

    <h3 class="section-title">3. Décomposition Arithmétique</h3>
    <div style="margin-top:20px;">
        <div style="margin-bottom:15px;">
            <span style="font-size:12px; text-transform:uppercase; color:#666;">Formule Appliquée :</span>
            <div class="math-formula">{data['detail']['formule']}</div>
        </div>
        {html_steps}
        <div class="calc-total">
            <span>NOUVEAU LOYER ANNUEL (H.T. H.C.)</span>
            <span>{data['result']['montant']:,.2f} €</span>
        </div>
    </div>

    <div class="hero-result">
        <div class="hero-lbl">Montant Révisé</div>
        <div class="hero-amount">{data['result']['montant']:,.2f} €</div>
        <div style="font-size:12px; margin-top:10px; color:#666;">
            Soit une évolution de <b>{data['result']['evolution']:+.2f}%</b> par rapport au loyer précédent.
        </div>
    </div>

    <div style="position:absolute; bottom:2cm; width:calc(100% - 4cm); text-align:center; font-size:10px; color:#999; border-top:1px solid #eee; padding-top:10px;">
        Ce document est généré par l'algorithme propriétaire de ComptaxSolutions.<br>
        La validité juridique dépend de l'exactitude des indices saisis.
    </div>
</div>
"""
    
    # Affichage
    st.markdown(html_content, unsafe_allow_html=True)

else:
    st.info("En attente de données valides pour générer le rapport.")
