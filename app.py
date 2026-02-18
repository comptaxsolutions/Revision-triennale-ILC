import streamlit as st
import pandas as pd

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Révision ILC Pro", page_icon="🏢", layout="wide")

# CSS : On garde juste le "Maquillage" (Couleurs), on enlève la "Structure" (Divs)
st.markdown("""
    <style>
    /* Fond général */
    .stApp { background-color: #F8F9FA; }
    
    /* Titres */
    h1 { color: #2C3E50; }
    h3 { color: #2E86C1; font-size: 1.2rem !important; }
    
    /* Métriques */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        color: #2E4053;
    }
    
    /* Badges (Alertes) */
    .badge-warning {
        background-color: #FEF9E7; color: #D35400; 
        padding: 5px 10px; border-radius: 4px; border: 1px solid #F5B041; 
        font-weight: bold; display: inline-block; margin-bottom: 10px;
    }
    .badge-success {
        background-color: #EAFAF1; color: #27AE60; 
        padding: 5px 10px; border-radius: 4px; border: 1px solid #ABEBC6; 
        font-weight: bold; display: inline-block; margin-bottom: 10px;
    }
    .badge-info {
        background-color: #EBF5FB; color: #2980B9;
        padding: 5px 10px; border-radius: 4px; border: 1px solid #AED6F1;
        font-weight: bold; display: inline-block; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DES DONNÉES
# ==============================================================================
@st.cache_data
def load_data():
    try:
        # Lecture du fichier Excel
        df = pd.read_excel("indices_ilc.xlsx")
        df.columns = ["Trimestre", "Indice"]
        df['Trimestre'] = df['Trimestre'].astype(str).str.strip()
        return df
    except Exception as e:
        # En cas d'erreur locale ou fichier manquant
        st.error(f"Erreur Excel : {e}")
        return pd.DataFrame() # Retourne vide pour ne pas crasher

df_indices = load_data()

# --- Fonctions Utilitaires ---
def get_indice_value(trimestre_str):
    if df_indices.empty: return None
    row = df_indices[df_indices["Trimestre"] == trimestre_str]
    if not row.empty:
        return row.iloc[0]["Indice"]
    return None

def get_offset_trimestre(trimestre, years_back=0):
    """Calcule automatiquement T - 3 ans"""
    try:
        parts = trimestre.split("-T")
        year = int(parts[0])
        quarter = int(parts[1])
        
        # On recule de X années
        new_year = year - years_back
        return f"{new_year}-T{quarter}"
    except:
        return None

# ==============================================================================
# 3. INTERFACE (Layout Natif)
# ==============================================================================

st.title("🏢 Simulateur de Révision ILC")
st.caption("Conforme Loi Pouvoir d'Achat (Plafonnement & Droit Commun)")

if df_indices.empty:
    st.warning("⚠️ Veuillez charger le fichier 'indices_ilc.xlsx' dans le dossier.")
    st.stop()

col_left, col_right = st.columns([1, 2], gap="large")

# --- COLONNE GAUCHE : SAISIE ---
with col_left:
    # Utilisation du conteneur natif avec bordure (Stable)
    with st.container(border=True):
        st.subheader("1. Paramètres du Bail")
        
        loyer_actuel = st.number_input("Loyer Annuel Actuel (€)", value=2155.28, step=100.0, format="%.2f")
        
        st.divider()
        
        # Sélecteur Triennal (Inversé pour avoir les récents en haut)
        liste_trimestres = df_indices["Trimestre"].tolist()[::-1]
        trimestre_rev = st.selectbox("📅 Trimestre de la Révision (N)", liste_trimestres)
        
        # AUTOMATISME 3 ANS (MASTER/SLAVE)
        trimestre_ref_auto = get_offset_trimestre(trimestre_rev, years_back=3)
        
        # Récupération indices
        ilc_rev = get_indice_value(trimestre_rev)
        ilc_ref = get_indice_value(trimestre_ref_auto)
        
        if ilc_ref:
            st.success(f"📌 Réf auto (-3 ans) : **{trimestre_ref_auto}**")
        else:
            st.error(f"⚠️ Indice {trimestre_ref_auto} manquant dans l'Excel.")

# --- COLONNE DROITE : RÉSULTAT ---
with col_right:
    if ilc_rev and ilc_ref:
        
        # Calcul des dates intermédiaires pour le plafonnement
        trimestre_n1 = get_offset_trimestre(trimestre_rev, years_back=1)
        trimestre_n2 = get_offset_trimestre(trimestre_rev, years_back=2)
        
        ilc_n1 = get_indice_value(trimestre_n1)
        ilc_n2 = get_indice_value(trimestre_n2)
        
        # --- LOGIQUE JURIDIQUE ---
        annee_float = int(trimestre_rev.split("-")[0]) + (int(trimestre_rev.split("-T")[1])/10)
        
        cas = "D"
        if 2022.2 <= annee_float <= 2023.1: cas = "A"
        elif 2023.2 <= annee_float <= 2024.1: cas = "B"
        elif 2024.2 <= annee_float <= 2026.1: cas = "C"
        
        # Calcul glissement
        glissement = 0.0
        if cas == "C" and ilc_n1 and ilc_n2:
            glissement = (ilc_n1 / ilc_n2) - 1
        elif ilc_rev and ilc_n1:
            glissement = (ilc_rev / ilc_n1) - 1
            
        is_plafonne = glissement >= 0.035
        
        # Calcul Montant
        nouveau_loyer = 0.0
        explication = ""
        
        # Formules
        if cas == "D":
            nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
            explication = f"{loyer_actuel:.2f} x ({ilc_rev} / {ilc_ref})"
        elif cas == "A":
            if is_plafonne:
                nouveau_loyer = loyer_actuel * (ilc_n1 / ilc_ref) * 1.035
                explication = f"{loyer_actuel:.2f} x ({ilc_n1} / {ilc_ref}) x 1,035"
            else:
                nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
                explication = f"{loyer_actuel:.2f} x ({ilc_rev} / {ilc_ref})"
        elif cas == "B":
            if is_plafonne:
                nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * (1.035**2)
                explication = f"{loyer_actuel:.2f} x ({ilc_n2} / {ilc_ref}) x 1,035²"
            else:
                nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * 1.035 * (ilc_rev / ilc_n1)
                explication = "Formule complexe (Non plafonné)"
        elif cas == "C":
            if is_plafonne:
                nouveau_loyer = loyer_actuel * (1.035**2) * (ilc_rev / ilc_n1)
                explication = f"{loyer_actuel:.2f} x 1,035² x ({ilc_rev} / {ilc_n1})"
            else:
                nouveau_loyer = loyer_actuel * 1.035 * (ilc_rev / ilc_n2)
                explication = f"{loyer_actuel:.2f} x 1,035 x ({ilc_rev} / {ilc_n2})"

        # --- AFFICHAGE STABLE ---
        
        # Bloc 1 : Indices
        with st.container(border=True):
            st.subheader("2. Indices Retenus")
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Ref (N-3)", ilc_ref, delta=trimestre_ref_auto, delta_color="off")
            k2.metric("N-2", ilc_n2 if ilc_n2 else "-")
            k3.metric("N-1", ilc_n1 if ilc_n1 else "-")
            k4.metric("Rev (N)", ilc_rev, delta=trimestre_rev, delta_color="off")

        # Bloc 2 : Résultat
        with st.container(border=True):
            st.subheader("3. Résultat & Analyse")
            
            cr1, cr2 = st.columns([2, 1])
            
            with cr1:
                # Affichage des Badges via HTML sécurisé (sans structure div complexe)
                if is_plafonne and cas != "D":
                    st.markdown(f'<div class="badge-warning">⚠️ PLAFONNEMENT ACTIVÉ (>3.5%)</div>', unsafe_allow_html=True)
                    st.caption(f"Glissement : {glissement:.2%}. Le bouclier loyer s'applique.")
                elif cas != "D":
                    st.markdown(f'<div class="badge-success">✅ SOUS LE PLAFOND (<3.5%)</div>', unsafe_allow_html=True)
                    st.caption(f"Glissement : {glissement:.2%}. Application de l'indice réel.")
                else:
                    st.markdown(f'<div class="badge-info">⚖️ DROIT COMMUN</div>', unsafe_allow_html=True)
                    st.caption("Hors période de plafonnement.")

                st.write(f"**Formule :** {explication}")
            
            with cr2:
                st.metric("Nouveau Loyer", f"{nouveau_loyer:,.2f} €")
