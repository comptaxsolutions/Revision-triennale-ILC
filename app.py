import streamlit as st
import pandas as pd
import datetime

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="ComptaxSolutions | Lease Valuation",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. DESIGN SYSTEM (CSS)
# ==============================================================================
st.markdown("""
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

    .stApp { background-color: var(--bg-app); font-family: 'Lato', sans-serif; }
    header, footer, #MainMenu { visibility: hidden; }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* FEUILLE A4 */
    .a4-sheet {
        background-color: var(--paper);
        width: 21cm;
        min-height: 29.7cm;
        margin: 0 auto;
        padding: 2cm;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        color: var(--ink);
    }

    /* TYPO */
    h1 { font-family: 'Playfair Display', serif; font-size: 28px; color: var(--ink); margin: 0; padding: 0; border: none; }
    h2 { font-family: 'Lato', sans-serif; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: var(--gold); margin-top: 0; }
    h3 { font-family: 'Playfair Display', serif; font-size: 18px; color: var(--ink); margin-top: 30px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }

    /* GRILLE */
    .data-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px; }
    .data-box { border: 1px solid var(--border); padding: 15px; text-align: center; }
    .data-val { font-size: 16px; font-weight: bold; font-family: 'Playfair Display', serif; }
    .data-lbl { font-size: 9px; text-transform: uppercase; color: var(--subtle); margin-top: 5px; }

    /* RÉSULTAT */
    .hero-result { background-color: #f9f9f9; border: 1px solid var(--ink); padding: 30px; text-align: center; margin: 30px 0; }
    .hero-amount { font-family: 'Playfair Display', serif; font-size: 48px; font-weight: 700; color: var(--ink); }
    .hero-lbl { font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: var(--subtle); }

    /* MATHS */
    .calc-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed var(--border); font-size: 14px; }
    .calc-total { display: flex; justify-content: space-between; padding: 15px 0; font-weight: bold; border-top: 2px solid var(--ink); margin-top: 10px; font-size: 16px; }
    .math-formula { font-family: 'Courier New', monospace; background: #f4f4f4; padding: 10px; font-size: 12px; color: #333; margin: 10px 0; }

    @media print {
        .stApp { background-color: white; }
        section[data-testid="stSidebar"] { display: none; }
        .a4-sheet { box-shadow: none; margin: 0; width: 100%; padding: 0; }
        .block-container { padding: 0 !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. DONNÉES
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
# 4. BARRE LATÉRALE
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Paramètres")
    loyer_actuel = st.number_input("Loyer Annuel (€)", value=2155.28, step=100.0, format="%.2f")
    
    if not df_indices.empty:
        liste_trimestres = df_indices["Trimestre"].tolist()[::-1]
        trimestre_rev = st.selectbox("Trimestre Révision", liste_trimestres)
        
        # Auto-Calcul
        trimestre_ref = get_offset(trimestre_rev, 3)
        trimestre_n1 = get_offset(trimestre_rev, 1)
        trimestre_n2 = get_offset(trimestre_rev, 2)
        
        ilc_rev = get_indice(trimestre_rev)
        ilc_ref = get_indice(trimestre_ref)
        ilc_n1 = get_indice(trimestre_n1)
        ilc_n2 = get_indice(trimestre_n2)
        
        if not ilc_ref:
            st.error("Données historiques manquantes.")
    else:
        st.error("Fichier Excel manquant.")

# ==============================================================================
# 5. LOGIQUE & RENDU
# ==============================================================================
if ilc_rev and ilc_ref:
    # Qualification
    annee_float = int(trimestre_rev.split("-")[0]) + (int(trimestre_rev.split("-T")[1])/10)
    cas = "D"
    regime_txt = "Droit Commun (Code de Commerce L.145-37)"
    
    if 2022.2 <= annee_float <= 2023.1: cas = "A"; regime_txt = "Dispositif Bouclier Loyer (Période A)"
    elif 2023.2 <= annee_float <= 2024.1: cas = "B"; regime_txt = "Dispositif Bouclier Loyer (Période B)"
    elif 2024.2 <= annee_float <= 2026.1: cas = "C"; regime_txt = "Dispositif Bouclier Loyer (Période C)"

    # Calculs
    glissement = 0.0
    if cas == "C" and ilc_n1 and ilc_n2: glissement = (ilc_n1 / ilc_n2) - 1
    elif ilc_rev and ilc_n1: glissement = (ilc_rev / ilc_n1) - 1
    
    is_plafonne = glissement >= 0.035
    
    # Construction HTML des étapes de calcul
    steps_html = ""
    nouveau_loyer = 0.0
    formule_litterale = ""
    
    def add_row(label, val, bold=False):
        w = "font-weight:bold;" if bold else ""
        return f'<div class="calc-row"><span style="{w}">{label}</span><span>{val}</span></div>'

    if cas == "D":
        nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
        steps_html += add_row("Loyer de Base", f"{loyer_actuel:,.2f} €")
        steps_html += add_row("x Indice Révision / Indice Réf", f"{ilc_rev} / {ilc_ref}")
        formule_litterale = f"{loyer_actuel:.2f} × ({ilc_rev} ÷ {ilc_ref})"
        
    elif cas == "A":
        steps_html += add_row("Loyer de Base", f"{loyer_actuel:,.2f} €")
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (ilc_n1 / ilc_ref) * 1.035
            steps_html += add_row("x Variation (N-1/Ref)", f"{ilc_n1} / {ilc_ref}")
            steps_html += add_row("x Plafonnement", "1.035", True)
            formule_litterale = f"{loyer_actuel:.2f} × ({ilc_n1} ÷ {ilc_ref}) × 1.035"
        else:
            nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
            steps_html += add_row("x Variation (N/Ref)", f"{ilc_rev} / {ilc_ref}")
            formule_litterale = f"{loyer_actuel:.2f} × ({ilc_rev} ÷ {ilc_ref})"
            
    elif cas == "B":
        steps_html += add_row("Loyer de Base", f"{loyer_actuel:,.2f} €")
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * (1.035**2)
            steps_html += add_row("x Variation (N-2/Ref)", f"{ilc_n2} / {ilc_ref}")
            steps_html += add_row("x Double Plafond", "1.0712 (1.035²)", True)
            formule_litterale = f"{loyer_actuel:.2f} × ({ilc_n2} ÷ {ilc_ref}) × 1.035²"
        else:
            nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * 1.035 * (ilc_rev / ilc_n1)
            steps_html += add_row("x Variation (N-2/Ref)", f"{ilc_n2} / {ilc_ref}")
            steps_html += add_row("x Coeff 2023", "1.035")
            steps_html += add_row("x Variation (N/N-1)", f"{ilc_rev} / {ilc_n1}")
            formule_litterale = "Formule complexe Cas B (Non plafonné)"

    elif cas == "C":
        steps_html += add_row("Loyer de Base", f"{loyer_actuel:,.2f} €")
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (1.035**2) * (ilc_rev / ilc_n1)
            steps_html += add_row("x Double Plafond", "1.0712")
            steps_html += add_row("x Variation (N/N-1)", f"{ilc_rev} / {ilc_n1}")
            formule_litterale = f"{loyer_actuel:.2f} × 1.035² × ({ilc_rev} ÷ {ilc_n1})"
        else:
            nouveau_loyer = loyer_actuel * 1.035 * (ilc_rev / ilc_n2)
            steps_html += add_row("x Coeff 2023", "1.035")
            steps_html += add_row("x Variation (N/N-2)", f"{ilc_rev} / {ilc_n2}")
            formule_litterale = f"{loyer_actuel:.2f} × 1.035 × ({ilc_rev} ÷ {ilc_n2})"

    # Construction des variables HTML
    date_jour = datetime.date.today().strftime('%d/%m/%Y')
    status_icon = "⚠️" if is_plafonne and cas != 'D' else "✅"
    status_text = "Plafonnement Activé" if is_plafonne and cas != 'D' else "Indice Réel (Non Plafonné)"
    evolution = ((nouveau_loyer/loyer_actuel)-1)*100
    
    val_n2 = ilc_n2 if ilc_n2 else '-'
    val_n1 = ilc_n1 if ilc_n1 else '-'

    # IMPORTANT: On construit le HTML en une seule chaîne collée (sans indentation à gauche)
    # pour éviter que Streamlit n'interprète cela comme du code.
    
    final_html = f"""
<div class="a4-sheet">
    <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2px solid #1a1a1a; padding-bottom:15px;">
        <div>
            <div style="font-family:'Playfair Display'; font-size:24px; font-weight:bold;">ComptaxSolutions</div>
            <div style="font-size:10px; text-transform:uppercase; letter-spacing:3px; color:#a38f60;">Expertise Fiscale & Digitale</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:12px;">CERTIFICAT DE RÉVISION</div>
            <div style="font-size:12px; font-weight:bold;">{date_jour}</div>
        </div>
    </div>

    <div style="margin-top:30px;">
        <h2>1. Contexte de la Révision</h2>
        <div style="font-size:14px; margin-top:10px;">
            Conformément aux dispositions du bail et à l'article L.145-37 du Code de commerce, 
            la révision triennale s'opère sur la base de l'indice ILC du <b>{trimestre_rev}</b>.
        </div>
        <div style="margin-top:15px; background:#f4f4f4; padding:10px; font-size:13px; border-left:4px solid #a38f60;">
            <strong>Régime Juridique Identifié :</strong> {regime_txt}<br>
            <em>Statut : {status_icon} {status_text}</em>
        </div>
    </div>

    <h3>2. Indices de Référence (ILC)</h3>
    <div class="data-grid">
        <div class="data-box">
            <div class="data-val">{ilc_ref}</div>
            <div class="data-lbl">RÉFÉRENCE<br>{trimestre_ref}</div>
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
            <div class="data-val">{ilc_rev}</div>
            <div class="data-lbl" style="color:#1a1a1a; font-weight:bold;">RÉVISION<br>{trimestre_rev}</div>
        </div>
    </div>

    <h3>3. Décomposition Arithmétique</h3>
    <div style="margin-top:20px;">
        <div style="margin-bottom:15px;">
            <span style="font-size:12px; text-transform:uppercase; color:#666;">Formule Appliquée :</span>
            <div class="math-formula">{formule_litterale}</div>
        </div>
        
        {steps_html}
        
        <div class="calc-total">
            <span>NOUVEAU LOYER ANNUEL (H.T. H.C.)</span>
            <span>{nouveau_loyer:,.2f} €</span>
        </div>
    </div>

    <div class="hero-result">
        <div class="hero-lbl">Montant Révisé</div>
        <div class="hero-amount">{nouveau_loyer:,.2f} €</div>
        <div style="font-size:12px; margin-top:10px; color:#666;">
            Soit une évolution de <b>{evolution:+.2f}%</b> par rapport au loyer précédent.
        </div>
    </div>

    <div style="position:absolute; bottom:2cm; width:calc(100% - 4cm); text-align:center; font-size:10px; color:#999; border-top:1px solid #eee; padding-top:10px;">
        Ce document est généré par l'algorithme propriétaire de ComptaxSolutions.<br>
        La validité juridique dépend de l'exactitude des indices saisis.
    </div>
</div>
"""

    st.markdown(final_html, unsafe_allow_html=True)

else:
    st.info("Veuillez sélectionner un trimestre valide dans la barre latérale.")
