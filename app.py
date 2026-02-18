import streamlit as st
import pandas as pd
import math

# ==============================================================================
# 1. CONFIGURATION & DESIGN
# ==============================================================================
st.set_page_config(page_title="Simulateur Révision ILC", page_icon="⚖️", layout="centered")

# Style CSS pour faire "Pro" (Couleurs Cabinet)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-style { font-size:24px; color: #2c3e50; font-weight: bold; }
    .result-box { background-color: #d4edda; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745; }
    .warning-box { background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 5px solid #ffc107; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. CHARGEMENT DES DONNÉES (Le lien avec votre Excel)
# ==============================================================================
@st.cache_data
def load_data():
    try:
        # On lit le fichier Excel qui est à côté du script
        df = pd.read_excel("indices_ilc.xlsx")
        # On s'assure que les colonnes sont propres
        df.columns = ["Trimestre", "Indice"]
        return df
    except FileNotFoundError:
        st.error("❌ ERREUR CRITIQUE : Le fichier 'indices_ilc.xlsx' est introuvable.")
        st.stop()

df_indices = load_data()

# ==============================================================================
# 3. INTERFACE UTILISATEUR (SIDEBAR)
# ==============================================================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2237/2237587.png", width=100)
st.sidebar.title("Paramètres du Bail")

loyer_actuel = st.sidebar.number_input("Loyer Annuel Actuel (€)", min_value=0.0, value=2155.28, step=10.0)

# Liste déroulante alimentée par le fichier Excel (Tri inversé pour avoir le récent en haut)
liste_trimestres = df_indices["Trimestre"].tolist()[::-1]
trimestre_rev = st.sidebar.selectbox("Trimestre de Révision (N)", liste_trimestres)

indice_ref_base = st.sidebar.number_input("Indice de Référence (Bail initial)", value=116.73, step=0.1)

# ==============================================================================
# 4. MOTEUR DE CALCUL (LOGIQUE JURIDIQUE)
# ==============================================================================
def get_indice(trimestre_cherché):
    # Cherche l'indice dans le dataframe Excel
    row = df_indices[df_indices["Trimestre"] == trimestre_cherché]
    if not row.empty:
        return row.iloc[0]["Indice"]
    return None

def get_prev_quarter(trimestre, n_back):
    # Fonction utilitaire pour trouver T-4 (N-1) ou T-8 (N-2)
    # Format attendu : "YYYY-TX"
    try:
        annee = int(trimestre.split("-")[0])
        t_num = int(trimestre.split("-T")[1])
        
        # On recule de n_back trimestres
        total_quarters = (annee * 4) + (t_num - 1) - n_back
        new_year = total_quarters // 4
        new_t = (total_quarters % 4) + 1
        return f"{new_year}-T{new_t}"
    except:
        return "Erreur"

# Récupération des indices clés
ilc_rev = get_indice(trimestre_rev)
trimestre_n1 = get_prev_quarter(trimestre_rev, 4)
ilc_n1 = get_indice(trimestre_n1)
trimestre_n2 = get_prev_quarter(trimestre_rev, 8)
ilc_n2 = get_indice(trimestre_n2)

# ==============================================================================
# 5. AFFICHAGE PRINCIPAL
# ==============================================================================
st.markdown('<p class="header-style">Simulateur de Révision (Loi Pouvoir d\'Achat)</p>', unsafe_allow_html=True)

if ilc_rev and ilc_n1 and ilc_n2:
    
    # --- A. Diagnostic Temporel (Le Cas A/B/C/D) ---
    annee_decimale = int(trimestre_rev.split("-")[0]) + (int(trimestre_rev.split("-T")[1])/10)
    
    cas_juridique = "D" # Par défaut
    if 2022.2 <= annee_decimale <= 2023.1: cas_juridique = "A"
    elif 2023.2 <= annee_decimale <= 2024.1: cas_juridique = "B"
    elif 2024.2 <= annee_decimale <= 2026.1: cas_juridique = "C"

    st.write(f"**Période détectée :** Cas {cas_juridique}")
    
    # --- B. Calcul du Glissement ---
    # Le glissement pertinent dépend du cas (Cf vos règles)
    glissement = 0.0
    if cas_juridique == "C":
        glissement = (ilc_n1 / ilc_n2) - 1
    else:
        glissement = (ilc_rev / ilc_n1) - 1
        
    plafond_active = glissement >= 0.035
    
    # Affichage des indices
    col1, col2, col3 = st.columns(3)
    col1.metric("Indice Rev (N)", ilc_rev)
    col2.metric("Indice N-1", ilc_n1, delta=f"Glissement {glissement:.2%}", delta_color="inverse")
    col3.metric("Indice N-2", ilc_n2)

    # --- C. Calcul Final (La Matrice) ---
    loyer_revise = 0.0
    formule_txt = ""

    if cas_juridique == "D":
        loyer_revise = loyer_actuel * (ilc_rev / indice_ref_base)
        formule_txt = "Droit commun : Loyer x (Rev / Ref)"
        
    elif cas_juridique == "A":
        if plafond_active:
            loyer_revise = loyer_actuel * (ilc_n1 / indice_ref_base) * 1.035
            formule_txt = "Plafond Actif : Loyer x (N-1 / Ref) x 1,035"
        else:
            loyer_revise = loyer_actuel * (ilc_rev / indice_ref_base)
            formule_txt = "Standard : Loyer x (Rev / Ref)"
            
    elif cas_juridique == "B":
        if plafond_active:
            loyer_revise = loyer_actuel * (ilc_n2 / indice_ref_base) * (1.035**2)
            formule_txt = "Double Plafond : Loyer x (N-2 / Ref) x 1,035²"
        else:
            loyer_revise = loyer_actuel * (ilc_n2 / indice_ref_base) * 1.035 * (ilc_rev / ilc_n1)
            formule_txt = "Complexe : Loyer x (N-2/Ref) x 1,035 x (Rev/N-1)"
            
    elif cas_juridique == "C":
        if plafond_active:
            loyer_revise = loyer_actuel * (1.035**2) * (ilc_rev / ilc_n1)
            formule_txt = "Post-Plafond (Haut) : Loyer x 1,035² x (Rev / N-1)"
        else:
            loyer_revise = loyer_actuel * 1.035 * (ilc_rev / ilc_n2)
            formule_txt = "Post-Plafond (Bas) : Loyer x 1,035 x (Rev / N-2)"

    # --- D. Affichage Résultat ---
    st.markdown("---")
    st.subheader("Résultat de la Révision")
    
    st.markdown(f"""
    <div class="result-box">
        <h2 style="margin:0; color:#155724;">{loyer_revise:,.2f} €</h2>
        <p style="margin:0;">Nouveau Loyer Annuel</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Explication Pédagogique
    st.markdown("### 📝 Analyse Juridique")
    msg_plafond = "⚠️ Le plafond de 3,5% est activé." if plafond_active else "✅ Le glissement est inférieur à 3,5%."
    
    st.info(f"""
    **Régime applicable :** {cas_juridique}
    \n**Diagnostic Inflation :** {msg_plafond}
    \n**Formule appliquée :** {formule_txt}
    """)
    
    # Petit détail calcul
    with st.expander("Voir le détail mathématique"):
        st.write(f"Loyer Base : {loyer_actuel}")
        st.write(f"Indices utilisés : Rev={ilc_rev}, N-1={ilc_n1}, N-2={ilc_n2}, Ref={indice_ref_base}")
        st.code(f"Calcul Python : {loyer_revise}")

else:
    st.warning("⚠️ Données insuffisantes dans le fichier Excel pour calculer sur ce trimestre (Besoin de N, N-1 et N-2).")