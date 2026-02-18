import streamlit as st
import pandas as pd
import datetime

# ==============================================================================
# 1. CONFIGURATION INITIALE
# ==============================================================================
st.set_page_config(
    page_title="ComptaxSolutions | Lease Valuation",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. DESIGN SYSTEM (CSS GLOBAL)
# ==============================================================================
# On injecte le CSS en une seule fois pour garantir le style
st.markdown("""
<style>
    /* Import des Polices de Luxe */
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Playfair+Display:wght@400;600;700&display=swap');

    /* Reset Global */
    .stApp {
        background-color: #f0f2f5; /* Gris très doux pour le fond de l'application */
        font-family: 'Lato', sans-serif;
    }
    
    /* Masquer les éléments parasites */
    header, footer, #MainMenu { visibility: hidden; }
    
    /* Le Conteneur "Feuille A4" */
    .report-container {
        background-color: #ffffff;
        max-width: 21cm;
        min-height: 29.7cm;
        margin: 0 auto; /* Centré horizontalement */
        padding: 60px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); /* Ombre portée élégante */
        color: #333;
        border-top: 5px solid #1a1a1a; /* La barre noire signature */
    }

    /* Titres */
    h1.brand { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 700; color: #1a1a1a; margin: 0; }
    div.tagline { font-size: 10px; text-transform: uppercase; letter-spacing: 3px; color: #a38f60; margin-top: 5px; }
    
    h2.section { 
        font-family: 'Playfair Display', serif; 
        font-size: 18px; 
        color: #1a1a1a; 
        border-bottom: 1px solid #eee; 
        padding-bottom: 10px; 
        margin-top: 40px; 
        margin-bottom: 20px;
    }

    /* Grille de données (Indices) */
    .indices-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
    }
    .index-box {
        border: 1px solid #e0e0e0;
        padding: 15px;
        text-align: center;
        border-radius: 4px;
    }
    .index-val { font-family: 'Playfair Display', serif; font-size: 18px; font-weight: bold; color: #1a1a1a; }
    .index-lbl { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: #666; margin-top: 5px; }
    
    /* Lignes de calcul */
    .calc-row {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px dashed #eee;
        font-size: 14px;
    }
    
    /* Résultat Final (Hero) */
    .result-box {
        background-color: #fafafa;
        border: 1px solid #1a1a1a;
        padding: 30px;
        text-align: center;
        margin-top: 40px;
    }
    .result-amount { font-family: 'Playfair Display', serif; font-size: 48px; font-weight: 700; color: #1a1a1a; }
    
    /* Mode Impression (CTRL+P) */
    @media print {
        .stApp { background-color: white; }
        section[data-testid="stSidebar"] { display: none; } /* Cache la barre latérale */
        .report-container { box-shadow: none; margin: 0; width: 100%; max-width: 100%; border: none; }
        .block-container { padding: 0 !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. MOTEUR DE DONNÉES (Chargement & Fonctions)
# ==============================================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("indices_ilc.xlsx")
        df.columns = ["Trimestre", "Indice"]
        df['Trimestre'] = df['Trimestre'].astype(str).str.strip()
        return df
    except:
        return pd.DataFrame()

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
# 4. BARRE LATÉRALE (CONTROLES)
# ==============================================================================
with st.sidebar:
    st.header("Paramètres")
    loyer_actuel = st.number_input("Loyer Annuel (€)", value=2155.28, step=100.0, format="%.2f")
    
    if not df_indices.empty:
        # Tri inversé pour avoir les dates récentes en haut
        liste_trimestres = df_indices["Trimestre"].tolist()[::-1]
        trimestre_rev = st.selectbox("Trimestre de Révision", liste_trimestres)
        
        # Calcul automatique des dates
        trimestre_ref = get_offset(trimestre_rev, 3)
        trimestre_n1 = get_offset(trimestre_rev, 1)
        trimestre_n2 = get_offset(trimestre_rev, 2)
        
        # Récupération des valeurs
        ilc_rev = get_indice(trimestre_rev)
        ilc_ref = get_indice(trimestre_ref)
        ilc_n1 = get_indice(trimestre_n1)
        ilc_n2 = get_indice(trimestre_n2)
        
        if not ilc_ref:
            st.warning(f"⚠️ Données manquantes pour {trimestre_ref} dans le fichier Excel.")
    else:
        st.error("Fichier 'indices_ilc.xlsx' introuvable.")
        st.stop()

# ==============================================================================
# 5. LOGIQUE DE CALCUL (BACKEND)
# ==============================================================================
if ilc_rev and ilc_ref:
    # 1. Identification du Cas Juridique
    annee_float = int(trimestre_rev.split("-")[0]) + (int(trimestre_rev.split("-T")[1])/10)
    
    cas = "D"
    regime_nom = "Droit Commun (Code de Commerce)"
    
    if 2022.2 <= annee_float <= 2023.1: cas, regime_nom = "A", "Dispositif Bouclier (Période A)"
    elif 2023.2 <= annee_float <= 2024.1: cas, regime_nom = "B", "Dispositif Bouclier (Période B)"
    elif 2024.2 <= annee_float <= 2026.1: cas, regime_nom = "C", "Dispositif Bouclier (Période C)"

    # 2. Test du Glissement
    glissement = 0.0
    if cas == "C" and ilc_n1 and ilc_n2: glissement = (ilc_n1 / ilc_n2) - 1
    elif ilc_rev and ilc_n1: glissement = (ilc_rev / ilc_n1) - 1
    
    is_plafonne = glissement >= 0.035
    
    # 3. Exécution du Calcul
    nouveau_loyer = 0.0
    lignes_calcul = "" # On va stocker le HTML des lignes ici
    formule_txt = ""

    # Helper pour créer une ligne HTML sans risque d'indentation
    def row_html(label, value, is_bold=False):
        style = "font-weight:bold; color:#1a1a1a;" if is_bold else "color:#666;"
        return f"""<div class="calc-row"><span style="{style}">{label}</span><span style="font-weight:bold; color:#1a1a1a;">{value}</span></div>"""

    if cas == "D":
        nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
        lignes_calcul += row_html("Loyer de Base", f"{loyer_actuel:,.2f} €")
        lignes_calcul += row_html(f"Ratio Variation ({ilc_rev} / {ilc_ref})", f"x {ilc_rev/ilc_ref:.5f}")
        formule_txt = f"{loyer_actuel:.2f} × ({ilc_rev} ÷ {ilc_ref})"
        
    elif cas == "A":
        lignes_calcul += row_html("Loyer de Base", f"{loyer_actuel:,.2f} €")
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (ilc_n1 / ilc_ref) * 1.035
            lignes_calcul += row_html("Variation Historique (N-1)", f"x {ilc_n1/ilc_ref:.5f}")
            lignes_calcul += row_html("Plafonnement Légal", "x 1.035 (+3.5%)", True)
        else:
            nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
            lignes_calcul += row_html("Variation Réelle (N)", f"x {ilc_rev/ilc_ref:.5f}")

    elif cas == "B":
        lignes_calcul += row_html("Loyer de Base", f"{loyer_actuel:,.2f} €")
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * (1.035**2)
            lignes_calcul += row_html("Variation Historique (N-2)", f"x {ilc_n2/ilc_ref:.5f}")
            lignes_calcul += row_html("Double Plafonnement", "x 1.0712 (+7.12%)", True)
        else:
            nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * 1.035 * (ilc_rev / ilc_n1)
            lignes_calcul += row_html("Variation N-2", f"x {ilc_n2/ilc_ref:.5f}")
            lignes_calcul += row_html("Coeff 2023", "x 1.035")
            lignes_calcul += row_html("Variation N", f"x {ilc_rev/ilc_n1:.5f}")

    elif cas == "C":
        lignes_calcul += row_html("Loyer de Base", f"{loyer_actuel:,.2f} €")
        if is_plafonne:
            nouveau_loyer = loyer_actuel * (1.035**2) * (ilc_rev / ilc_n1)
            lignes_calcul += row_html("Double Plafonnement", "x 1.0712 (+7.12%)", True)
            lignes_calcul += row_html("Variation Récente (N/N-1)", f"x {ilc_rev/ilc_n1:.5f}")
        else:
            nouveau_loyer = loyer_actuel * 1.035 * (ilc_rev / ilc_n2)
            lignes_calcul += row_html("Coeff 2023", "x 1.035")
            lignes_calcul += row_html("Variation Récente (N/N-2)", f"x {ilc_rev/ilc_n2:.5f}")

    evolution = ((nouveau_loyer/loyer_actuel)-1)*100
    date_jour = datetime.date.today().strftime('%d/%m/%Y')
    
    # Statut
    statut_icon = "⚠️ PLAFONNÉ" if is_plafonne and cas != 'D' else "✅ NON PLAFONNÉ"
    statut_color = "#e67e22" if is_plafonne and cas != 'D' else "#27ae60"

    # ==========================================================================
    # 6. GÉNÉRATION DU RAPPORT HTML (CONCATÉNATION PROPRE)
    # ==========================================================================
    # On construit le HTML morceau par morceau pour éviter les bugs d'affichage
    
    html = f"""
    <div class="report-container">
        <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:2px solid #1a1a1a; padding-bottom:20px;">
            <div>
                <h1 class="brand">ComptaxSolutions</h1>
                <div class="tagline">Expertise Fiscale & Digitale</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:11px; color:#666;">CERTIFICAT DE RÉVISION</div>
                <div style="font-size:14px; font-weight:bold;">{date_jour}</div>
            </div>
        </div>

        <h2 class="section">1. Contexte Juridique</h2>
        <div style="font-size:14px; line-height:1.6;">
            Révision triennale indexée sur l'ILC du <b>{trimestre_rev}</b>.<br>
            Régime applicable : <b>{regime_nom}</b><br>
            <span style="display:inline-block; margin-top:5px; padding:5px 10px; background-color:{statut_color}; color:white; font-size:11px; border-radius:3px; font-weight:bold;">
                {statut_icon}
            </span>
        </div>

        <h2 class="section">2. Indices de Référence</h2>
        <div class="indices-grid">
            <div class="index-box">
                <div class="index-val">{ilc_ref}</div>
                <div class="index-lbl">RÉF ({trimestre_ref})</div>
            </div>
            <div class="index-box" style="background-color:#f9f9f9; color:#aaa;">
                <div class="index-val">{ilc_n2 if ilc_n2 else '-'}</div>
                <div class="index-lbl">N-2</div>
            </div>
            <div class="index-box" style="background-color:#f9f9f9; color:#aaa;">
                <div class="index-val">{ilc_n1 if ilc_n1 else '-'}</div>
                <div class="index-lbl">N-1</div>
            </div>
            <div class="index-box" style="border-color:#1a1a1a;">
                <div class="index-val">{ilc_rev}</div>
                <div class="index-lbl" style="color:#1a1a1a; font-weight:bold;">RÉVISION ({trimestre_rev})</div>
            </div>
        </div>

        <h2 class="section">3. Décomposition</h2>
        <div style="margin-top:20px;">
            {lignes_calcul}
        </div>

        <div class="result-box">
            <div style="font-size:11px; text-transform:uppercase; letter-spacing:2px; color:#666; margin-bottom:10px;">Nouveau Loyer Annuel</div>
            <div class="result-amount">{nouveau_loyer:,.2f} €</div>
            <div style="font-size:13px; margin-top:15px; color:#666;">
                Évolution : <b>{evolution:+.2f}%</b>
            </div>
        </div>

        <div style="text-align:center; font-size:10px; color:#999; margin-top:60px;">
            Document généré automatiquement par l'algorithme ComptaxSolutions.<br>
            La validité juridique dépend de l'exactitude des indices saisis.
        </div>
    </div>
    """

    # Affichage final avec interpretation HTML forcée
    st.markdown(html, unsafe_allow_html=True)

else:
    # État vide (attente de saisie)
    st.info("Veuillez sélectionner un trimestre valide dans la barre latérale pour générer le rapport.")
