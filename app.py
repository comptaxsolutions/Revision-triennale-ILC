import streamlit as st
import pandas as pd

# ==============================================================================
# 1. CONFIGURATION & DESIGN SYSTEM (CSS)
# ==============================================================================
st.set_page_config(page_title="Révision ILC Pro", page_icon="🏢", layout="wide")

# Injection de CSS pour un look "App Mobile / SaaS"
st.markdown("""
    <style>
    /* Fond général plus doux */
    .stApp { background-color: #F0F2F6; }
    
    /* Style des Cartes (Box blanches) */
    .css-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Style du Résultat Final */
    .result-metric {
        font-size: 36px;
        font-weight: bold;
        color: #2E86C1;
    }
    
    /* Titres de section */
    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #566573;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Alerte Plafonnement */
    .badge-warning {
        background-color: #FEF9E7;
        color: #D35400;
        padding: 5px 10px;
        border-radius: 5px;
        border: 1px solid #F5B041;
        font-weight: bold;
    }
    .badge-success {
        background-color: #EAFAF1;
        color: #27AE60;
        padding: 5px 10px;
        border-radius: 5px;
        border: 1px solid #ABEBC6;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DES DONNÉES
# ==============================================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("indices_ilc.xlsx")
        df.columns = ["Trimestre", "Indice"]
        # On s'assure que tout est propre
        df['Trimestre'] = df['Trimestre'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Erreur de lecture du fichier Excel: {e}")
        st.stop()

df_indices = load_data()

# Fonctions utilitaires
def get_indice_value(trimestre_str):
    row = df_indices[df_indices["Trimestre"] == trimestre_str]
    if not row.empty:
        return row.iloc[0]["Indice"]
    return None

def get_offset_trimestre(trimestre, years_back=0, quarters_back=0):
    """Calcule un trimestre dans le passé (ex: T1 2024 - 3 ans = T1 2021)"""
    try:
        parts = trimestre.split("-T")
        year = int(parts[0])
        quarter = int(parts[1])
        
        total_quarters = (year * 4) + (quarter - 1)
        target_quarters = total_quarters - (years_back * 4) - quarters_back
        
        new_year = target_quarters // 4
        new_quarter = (target_quarters % 4) + 1
        return f"{new_year}-T{new_quarter}"
    except:
        return None

# ==============================================================================
# 3. INTERFACE UTILISATEUR (Layout 2 colonnes)
# ==============================================================================

# En-tête
st.markdown("<h1 style='text-align: center; color: #2C3E50;'>🏢 Simulateur de Révision Triennale</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7F8C8D;'>Conforme Loi Pouvoir d'Achat (Plafonnement ILC)</p>", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 2])

# --- COLONNE GAUCHE : SAISIE (INPUTS) ---
with col_left:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">1. Paramètres du Bail</div>', unsafe_allow_html=True)
    
    # Saisie Loyer
    loyer_actuel = st.number_input("Loyer Annuel Actuel (€)", value=2155.28, step=100.0, format="%.2f")
    
    st.markdown("---")
    
    # 1. Choix du Trimestre de Révision (Le "Maître")
    # On trie pour avoir les dates récentes en haut
    liste_trimestres = df_indices["Trimestre"].tolist()[::-1]
    trimestre_rev = st.selectbox("📅 Trimestre de la Révision", liste_trimestres)
    
    # 2. Calcul Automatique du Trimestre de Référence (L'Esclave - 3 ans)
    trimestre_ref_auto = get_offset_trimestre(trimestre_rev, years_back=3)
    
    # Récupération des indices
    ilc_rev = get_indice_value(trimestre_rev)
    ilc_ref = get_indice_value(trimestre_ref_auto)
    
    # Affichage en "Lecture Seule" pour l'utilisateur (Feedback visuel)
    st.info(f"**Trimestre de Réf (Auto -3 ans) :** {trimestre_ref_auto}")
    
    if ilc_ref is None:
        st.error(f"⚠️ Attention : L'indice pour {trimestre_ref_auto} n'est pas dans votre fichier Excel !")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- COLONNE DROITE : RÉSULTATS & ANALYSE ---
with col_right:
    if ilc_rev and ilc_ref:
        
        # Récupération des indices intermédiaires (N-1 et N-2 pour plafonnement)
        trimestre_n1 = get_offset_trimestre(trimestre_rev, years_back=1)
        trimestre_n2 = get_offset_trimestre(trimestre_rev, years_back=2)
        
        ilc_n1 = get_indice_value(trimestre_n1)
        ilc_n2 = get_indice_value(trimestre_n2)
        
        # --- MOTEUR DE CALCUL (LOGIQUE) ---
        annee_float = int(trimestre_rev.split("-")[0]) + (int(trimestre_rev.split("-T")[1])/10)
        
        cas = "D"
        if 2022.2 <= annee_float <= 2023.1: cas = "A"
        elif 2023.2 <= annee_float <= 2024.1: cas = "B"
        elif 2024.2 <= annee_float <= 2026.1: cas = "C"
        
        # Calcul du glissement pertinent
        if cas == "C":
            glissement = (ilc_n1 / ilc_n2) - 1 if (ilc_n1 and ilc_n2) else 0
        else:
            glissement = (ilc_rev / ilc_n1) - 1 if (ilc_rev and ilc_n1) else 0
            
        is_plafonne = glissement >= 0.035
        
        # Calcul du Montant Final
        nouveau_loyer = 0.0
        explication_calc = ""
        
        if cas == "D":
            nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
            explication_calc = f"{loyer_actuel:.2f} x ({ilc_rev} / {ilc_ref})"
        elif cas == "A":
            if is_plafonne:
                nouveau_loyer = loyer_actuel * (ilc_n1 / ilc_ref) * 1.035
                explication_calc = f"{loyer_actuel:.2f} x ({ilc_n1} / {ilc_ref}) x 1,035"
            else:
                nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
                explication_calc = f"{loyer_actuel:.2f} x ({ilc_rev} / {ilc_ref})"
        elif cas == "B":
            if is_plafonne:
                nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * (1.035**2)
                explication_calc = f"{loyer_actuel:.2f} x ({ilc_n2} / {ilc_ref}) x 1,035²"
            else:
                nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * 1.035 * (ilc_rev / ilc_n1)
                explication_calc = "Formule complexe Cas B (Non plafonné)"
        elif cas == "C":
            if is_plafonne:
                nouveau_loyer = loyer_actuel * (1.035**2) * (ilc_rev / ilc_n1)
                explication_calc = f"{loyer_actuel:.2f} x 1,035² x ({ilc_rev} / {ilc_n1})"
            else:
                nouveau_loyer = loyer_actuel * 1.035 * (ilc_rev / ilc_n2)
                explication_calc = f"{loyer_actuel:.2f} x 1,035 x ({ilc_rev} / {ilc_n2})"

        # --- AFFICHAGE DASHBOARD ---
        
        # 1. Carte Indices
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">2. Données ILC Retenues</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Réf (N-3)", ilc_ref, f"{trimestre_ref_auto}")
        c2.metric("N-2", ilc_n2 if ilc_n2 else "?")
        c3.metric("N-1", ilc_n1 if ilc_n1 else "?")
        c4.metric("Rev (N)", ilc_rev, f"{trimestre_rev}")
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. Carte Résultat
        st.markdown('<div class="css-card" style="border-left: 5px solid #2E86C1;">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">3. Nouveau Loyer Révisé</div>', unsafe_allow_html=True)
        
        col_res_txt, col_res_val = st.columns([2, 1])
        
        with col_res_txt:
            # Badge Plafond
            if is_plafonne and cas != "D":
                st.markdown(f'<span class="badge-warning">⚠️ PLAFONNEMENT ACTIVÉ (>3.5%)</span>', unsafe_allow_html=True)
                st.caption(f"Le glissement constaté est de {glissement:.2%}. Le bouclier loyer s'applique.")
            elif cas != "D":
                st.markdown(f'<span class="badge-success">✅ SOUS LE PLAFOND (<3.5%)</span>', unsafe_allow_html=True)
                st.caption(f"Le glissement constaté est de {glissement:.2%}. Application de l'indice réel.")
            else:
                st.markdown(f'<span class="badge-success">⚖️ DROIT COMMUN</span>', unsafe_allow_html=True)
                st.caption("Hors période de plafonnement.")

            st.markdown(f"**Formule :** {explication_calc}")
            
        with col_res_val:
            st.markdown(f'<div class="result-metric">{nouveau_loyer:,.2f} €</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.warning("En attente de données valides (Vérifiez que les trimestres existent dans l'Excel).")
