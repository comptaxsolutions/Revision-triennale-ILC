import streamlit as st
import pandas as pd
import datetime

# ==============================================================================
# 1. CONFIGURATION STRICTE
# ==============================================================================
st.set_page_config(
    page_title="ComptaxSolutions | Lease Valuation",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. DESIGN SYSTEM "GOLDMAN SACHS STYLE"
# ==============================================================================
st.markdown("""
    <style>
    /* IMPORTS FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap');

    :root {
        --bg-app: #e0e5ec;        /* Gris perle pour le fond d'écran */
        --paper: #ffffff;         /* Blanc pur pour la feuille */
        --ink: #1a1a1a;           /* Noir encre */
        --gold: #a38f60;          /* Or vieilli (Luxe) */
        --subtle: #666666;        /* Gris moyen */
        --border: #dcdcdc;
    }

    /* NETTOYAGE COMPLET DE L'INTERFACE STREAMLIT */
    .stApp { background-color: var(--bg-app); font-family: 'Lato', sans-serif; }
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* SUPPRESSION DES MARGES PARASITES */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* LA FEUILLE A4 - LE COEUR DU DESIGN */
    .a4-sheet {
        background-color: var(--paper);
        width: 21cm;
        min-height: 29.7cm;
        margin: 0 auto;
        padding: 2cm;
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
        position: relative;
    }

    /* TYPOGRAPHIE INTERNE */
    h1 { font-family: 'Playfair Display', serif; font-size: 28px; color: var(--ink); margin-bottom: 5px; border-bottom: none; }
    h2 { font-family: 'Lato', sans-serif; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: var(--gold); margin-top: 0; }
    h3 { font-family: 'Playfair Display', serif; font-size: 18px; color: var(--ink); margin-top: 30px; border-bottom: 1px solid var(--border); padding-bottom: 10px; }

    /* TABLEAUX DE DONNÉES */
    .data-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-top: 20px;
    }
    .data-box {
        border: 1px solid var(--border);
        padding: 15px;
        text-align: center;
    }
    .data-val { font-size: 16px; font-weight: bold; font-family: 'Playfair Display', serif; }
    .data-lbl { font-size: 9px; text-transform: uppercase; color: var(--subtle); margin-top: 5px; }

    /* ZONE DE RÉSULTAT */
    .hero-result {
        background-color: #f9f9f9;
        border: 1px solid var(--ink);
        padding: 30px;
        text-align: center;
        margin: 30px 0;
    }
    .hero-amount { font-family: 'Playfair Display', serif; font-size: 48px; font-weight: 700; color: var(--ink); }
    .hero-lbl { font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: var(--subtle); }

    /* DÉTAIL CALCUL (MATHS) */
    .calc-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px dashed var(--border);
        font-size: 14px;
    }
    .calc-total {
        display: flex;
        justify-content: space-between;
        padding: 15px 0;
        font-weight: bold;
        border-top: 2px solid var(--ink);
        border-bottom: none;
        margin-top: 10px;
        font-size: 16px;
    }
    .math-formula {
        font-family: 'Courier New', monospace;
        background: #f4f4f4;
        padding: 10px;
        font-size: 12px;
        color: #333;
        margin: 10px 0;
    }

    /* PRINT FIX */
    @media print {
        .stApp { background-color: white; }
        section[data-testid="stSidebar"] { display: none; }
        .a4-sheet { box-shadow: none; margin: 0; width: 100%; padding: 0; }
        .block-container { padding: 0 !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. DONNÉES ET FONCTIONS
# ==============================================================================
@st.cache_data
def load_data():
    try:
        # Création d'un DataFrame vide robuste si fichier manquant
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
# 4. SIDEBAR (CONTROLES)
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
# 5. LOGIQUE DE CALCUL DÉTAILLÉE
# ==============================================================================
if ilc_rev and ilc_ref:
    # Qualification
    annee_float = int(trimestre_rev.split("-")[0]) + (int(trimestre_rev.split("-T")[1])/10)
    cas = "D"
    regime_txt = "Droit Commun (Code de Commerce L.145-37)"
    
    if 2022.2 <= annee_float <= 2023.1: cas = "A"; regime_txt = "Dispositif Bouclier Loyer (Période A)"
    elif 2023.2 <= annee_float <= 2024.1: cas = "B"; regime_txt = "Dispositif Bouclier Loyer (Période B)"
    elif 2024.2 <= annee_float <= 2026.1: cas = "C"; regime_txt = "Dispositif Bouclier Loyer (Période C)"

    # Glissement
    glissement = 0.0
    glissement_txt = ""
    formule_litterale = ""
    
    if cas == "C" and ilc_n1 and ilc_n2:
        glissement = (ilc_n1 / ilc_n2) - 1
        glissement_txt = f"({ilc_n1} / {ilc_n2}) - 1"
    elif ilc_rev and ilc_n1:
        glissement = (ilc_rev / ilc_n1) - 1
        glissement_txt = f"({ilc_rev} / {ilc_n1}) - 1"
    
    is_plafonne = glissement >= 0.035
    
    # Construction du calcul détaillé
    nouveau_loyer = 0.0
    steps_html = ""
    
    # Fonction helper pour le HTML des étapes
    def add_step(label, value, is_bold=False):
        style = "font-weight:bold;" if is_bold else ""
        return f'<div class="calc-row"><span style="{style}">{label}</span><span>{value}</span></div>'

    if cas == "D":
        nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
        steps_html += add_step("Loyer de Base", f"{loyer_actuel:,.2f} €")
        steps_html += add_step("x Coefficient Variation", f"{ilc_rev} / {ilc_ref}")
        steps_html += add_step("= Ratio Multiplicateur", f"{ilc_rev/ilc_ref:.5f}")
        formule_litterale = f"{loyer_actuel:.2f} × ({ilc_rev} ÷ {ilc_ref})"

    elif cas == "A":
        steps_html += add_step("Loyer de Base", f"{loyer_actuel:,.2f} €")
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (ilc_n1 / ilc_ref) * 1.035
            steps_html += add_step("x Variation Historique (N-1/Ref)", f"{ilc_n1} / {ilc_ref} = {ilc_n1/ilc_ref:.5f}")
            steps_html += add_step("x Coefficient Plafonnement", "1.035 (+3.5%)", True)
            formule_litterale = f"{loyer_actuel:.2f} × ({ilc_n1} ÷ {ilc_ref}) × 1,035"
        else:
            nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
            steps_html += add_step("x Variation Réelle (N/Ref)", f"{ilc_rev} / {ilc_ref} = {ilc_rev/ilc_ref:.5f}")
            steps_html += add_step("Note", "Glissement < 3.5%, pas de plafonnement.")
            formule_litterale = f"{loyer_actuel:.2f} × ({ilc_rev} ÷ {ilc_ref})"

    elif cas == "B":
        steps_html += add_step("Loyer de Base", f"{loyer_actuel:,.2f} €")
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * (1.035**2)
            steps_html += add_step("x Variation Historique (N-2/Ref)", f"{ilc_n2} / {ilc_ref} = {ilc_n2/ilc_ref:.5f}")
            steps_html += add_step("x Double Plafonnement (1.035²)", f"{(1.035**2):.5f} (+7.12%)", True)
            formule_litterale = f"{loyer_actuel:.2f} × ({ilc_n2} ÷ {ilc_ref}) × 1,035²"
        else:
            nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * 1.035 * (ilc_rev / ilc_n1)
            steps_html += add_step("x Variation Historique (N-2/Ref)", f"{ilc_n2} / {ilc_ref}")
            steps_html += add_step("x Coefficient 2022-2023", "1.035")
            steps_html += add_step("x Variation Récente (N/N-1)", f"{ilc_rev} / {ilc_n1}")
            formule_litterale = "Formule complexe Cas B (Non plafonné)"

    elif cas == "C":
        steps_html += add_step("Loyer de Base", f"{loyer_actuel:,.2f} €")
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (1.035**2) * (ilc_rev / ilc_n1)
            steps_html += add_step("x Double Plafonnement (1.035²)", f"{(1.035**2):.5f}")
            steps_html += add_step("x Variation Récente (N/N-1)", f"{ilc_rev} / {ilc_n1} = {ilc_rev/ilc_n1:.5f}")
            formule_litterale = f"{loyer_actuel:.2f} × 1,035² × ({ilc_rev} ÷ {ilc_n1})"
        else:
            nouveau_loyer = loyer_actuel * 1.035 * (ilc_rev / ilc_n2)
            steps_html += add_step("x Coefficient 2022-2023", "1.035")
            steps_html += add_step("x Variation Récente (N/N-2)", f"{ilc_rev} / {ilc_n2}")
            formule_litterale = f"{loyer_actuel:.2f} × 1,035 × ({ilc_rev} ÷ {ilc_n2})"

    # ==============================================================================
    # 6. VISUALISATION A4 (CONSTRUCTION ROBUSTE)
    # ==============================================================================
    
    # On prépare les variables pour l'affichage propre
    evolution_pct = ((nouveau_loyer/loyer_actuel)-1)*100
    date_jour = datetime.date.today().strftime('%d/%m/%Y')
    
    # BLOC 1 : EN-TÊTE
    html_header = f"""
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
    """

    # BLOC 2 : CONTEXTE
    status_msg = "⚠️ Plafonnement Activé" if is_plafonne and cas != 'D' else "✅ Indice Réel (Non Plafonné)"
    html_context = f"""
        <div style="margin-top:30px;">
            <h2>1. Contexte de la Révision</h2>
            <div style="font-size:14px; margin-top:10px;">
                Conformément aux dispositions du bail et à l'article L.145-37 du Code de commerce, 
                la révision triennale s'opère sur la base de l'indice ILC du <b>{trimestre_rev}</b>.
            </div>
            <div style="margin-top:15px; background:#f4f4f4; padding:10px; font-size:13px; border-left:4px solid #a38f60;">
                <strong>Régime Juridique Identifié :</strong> {regime_txt}<br>
                <em>Statut : {status_msg}</em>
            </div>
        </div>
    """

    # BLOC 3 : INDICES
    val_n2 = ilc_n2 if ilc_n2 else '-'
    val_n1 = ilc_n1 if ilc_n1 else '-'
    html_indices = f"""
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
    """

    # BLOC 4 : CALCUL
    html_calc = f"""
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
    """

    # BLOC 5 : RÉSULTAT & FOOTER
    html_footer = f"""
        <div class="hero-result">
            <div class="hero-lbl">Montant Révisé</div>
            <div class="hero-amount">{nouveau_loyer:,.2f} €</div>
            <div style="font-size:12px; margin-top:10px; color:#666;">
                Soit une évolution de <b>{evolution_pct:+.2f}%</b> par rapport au loyer précédent.
            </div>
        </div>

        <div style="position:absolute; bottom:2cm; width:calc(100% - 4cm); text-align:center; font-size:10px; color:#999; border-top:1px solid #eee; padding-top:10px;">
            Ce document est généré par l'algorithme propriétaire de ComptaxSolutions.<br>
            La validité juridique dépend de l'exactitude des indices saisis.
        </div>
    </div>
    """

    # ASSEMBLAGE FINAL
    final_html = html_header + html_context + html_indices + html_calc + html_footer
    st.markdown(final_html, unsafe_allow_html=True)

else:
    st.info("Veuillez sélectionner un trimestre valide dans la barre latérale.")
