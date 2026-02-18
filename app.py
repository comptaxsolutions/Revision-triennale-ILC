import streamlit as st
import pandas as pd

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
st.set_page_config(page_title="Révision ILC Expert", page_icon="⚖️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    h1 { color: #2C3E50; }
    /* Style spécifique pour l'expander (le détail) */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #2E86C1;
        background-color: white;
        border-radius: 5px;
    }
    .badge-warning {
        background-color: #FEF9E7; color: #D35400; 
        padding: 5px 10px; border-radius: 4px; border: 1px solid #F5B041; 
        font-weight: bold;
    }
    .badge-success {
        background-color: #EAFAF1; color: #27AE60; 
        padding: 5px 10px; border-radius: 4px; border: 1px solid #ABEBC6; 
        font-weight: bold;
    }
    .badge-info {
        background-color: #EBF5FB; color: #2980B9;
        padding: 5px 10px; border-radius: 4px; border: 1px solid #AED6F1;
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
        df['Trimestre'] = df['Trimestre'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Erreur Excel : {e}")
        return pd.DataFrame()

df_indices = load_data()

def get_indice_value(trimestre_str):
    if df_indices.empty: return None
    row = df_indices[df_indices["Trimestre"] == trimestre_str]
    if not row.empty: return row.iloc[0]["Indice"]
    return None

def get_offset_trimestre(trimestre, years_back=0):
    try:
        parts = trimestre.split("-T")
        year = int(parts[0])
        quarter = int(parts[1])
        new_year = year - years_back
        return f"{new_year}-T{quarter}"
    except: return None

# ==============================================================================
# 3. INTERFACE
# ==============================================================================

st.title("⚖️ Simulateur de Révision ILC")
st.caption("Conforme Loi Pouvoir d'Achat (Plafonnement) & Droit Commun")

if df_indices.empty:
    st.warning("⚠️ Veuillez charger le fichier 'indices_ilc.xlsx'.")
    st.stop()

col_left, col_right = st.columns([1, 2], gap="large")

# --- COLONNE GAUCHE : SAISIE ---
with col_left:
    with st.container(border=True):
        st.subheader("1. Paramètres du Bail")
        loyer_actuel = st.number_input("Loyer Annuel Actuel (€)", value=2155.28, step=100.0, format="%.2f")
        st.divider()
        
        liste_trimestres = df_indices["Trimestre"].tolist()[::-1]
        trimestre_rev = st.selectbox("📅 Trimestre de Révision (N)", liste_trimestres)
        
        # AUTO-LOCK 3 ANS
        trimestre_ref_auto = get_offset_trimestre(trimestre_rev, years_back=3)
        ilc_rev = get_indice_value(trimestre_rev)
        ilc_ref = get_indice_value(trimestre_ref_auto)
        
        if ilc_ref:
            st.success(f"📌 Réf (-3 ans) : **{trimestre_ref_auto}**")
        else:
            st.error(f"⚠️ Indice {trimestre_ref_auto} manquant.")

# --- COLONNE DROITE : CALCUL & RAISONNEMENT ---
with col_right:
    if ilc_rev and ilc_ref:
        
        # Calculs indices intermédiaires
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
        
        # Glissement
        glissement = 0.0
        txt_glissement = ""
        if cas == "C" and ilc_n1 and ilc_n2:
            glissement = (ilc_n1 / ilc_n2) - 1
            txt_glissement = "(Indice N-1 / Indice N-2)"
        elif ilc_rev and ilc_n1:
            glissement = (ilc_rev / ilc_n1) - 1
            txt_glissement = "(Indice N / Indice N-1)"
            
        is_plafonne = glissement >= 0.035
        
        # Calcul Montant
        nouveau_loyer = 0.0
        formule_latex = ""
        raisonnement_txt = ""
        
        if cas == "D":
            nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
            raisonnement_txt = "Nous sommes hors période de plafonnement. Application du droit commun."
            formule_latex = r"L_{révisé} = L_{actuel} \times \frac{ILC_{rev}}{ILC_{ref}}"
            
        elif cas == "A":
            raisonnement_txt = "Période de Plafonnement Initial (Cas A)."
            if is_plafonne:
                nouveau_loyer = loyer_actuel * (ilc_n1 / ilc_ref) * 1.035
                formule_latex = r"L_{révisé} = L_{actuel} \times \frac{ILC_{N-1}}{ILC_{ref}} \times 1,035"
            else:
                nouveau_loyer = loyer_actuel * (ilc_rev / ilc_ref)
                formule_latex = r"L_{révisé} = L_{actuel} \times \frac{ILC_{rev}}{ILC_{ref}}"

        elif cas == "B":
            raisonnement_txt = "Période de Plafonnement Intermédiaire (Cas B)."
            if is_plafonne:
                nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * (1.035**2)
                formule_latex = r"L_{révisé} = L_{actuel} \times \frac{ILC_{N-2}}{ILC_{ref}} \times (1 + 3,5\%)^2"
            else:
                nouveau_loyer = loyer_actuel * (ilc_n2 / ilc_ref) * 1.035 * (ilc_rev / ilc_n1)
                formule_latex = r"L_{révisé} = L_{actuel} \times \frac{ILC_{N-2}}{ILC_{ref}} \times 1,035 \times \frac{ILC_{rev}}{ILC_{N-1}}"

        elif cas == "C":
            raisonnement_txt = "Période Post-Plafonnement (Cas C)."
            if is_plafonne:
                nouveau_loyer = loyer_actuel * (1.035**2) * (ilc_rev / ilc_n1)
                formule_latex = r"L_{révisé} = L_{actuel} \times (1 + 3,5\%)^2 \times \frac{ILC_{rev}}{ILC_{N-1}}"
            else:
                nouveau_loyer = loyer_actuel * 1.035 * (ilc_rev / ilc_n2)
                formule_latex = r"L_{révisé} = L_{actuel} \times 1,035 \times \frac{ILC_{rev}}{ILC_{N-2}}"

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
            st.subheader("3. Résultat Final")
            cr1, cr2 = st.columns([2, 1])
            with cr1:
                if is_plafonne and cas != "D":
                    st.markdown(f'<div class="badge-warning">⚠️ PLAFONNEMENT ACTIVÉ (>3.5%)</div>', unsafe_allow_html=True)
                elif cas != "D":
                    st.markdown(f'<div class="badge-success">✅ SOUS LE PLAFOND (<3.5%)</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="badge-info">⚖️ DROIT COMMUN</div>', unsafe_allow_html=True)
            with cr2:
                st.metric("Nouveau Loyer", f"{nouveau_loyer:,.2f} €")
        
        # --- BLOC 3 : LE DÉTAIL JURIDIQUE (ACCORDÉON) ---
        with st.expander("🔎 VOIR LE DÉTAIL EXACT & LE RAISONNEMENT JURIDIQUE", expanded=False):
            
            st.markdown("### 1. Qualification de la période")
            st.info(f"**{raisonnement_txt}**")
            st.write(f"La révision intervenant au **{trimestre_rev}**, elle relève des règles spécifiques définies par la Loi portant mesures d'urgence pour la protection du pouvoir d'achat.")

            st.markdown("### 2. Test du Glissement Annuel")
            st.write(f"Le mécanisme compare l'évolution de l'indice sur la période pertinente {txt_glissement} au seuil de 3,5%.")
            
            col_test1, col_test2 = st.columns(2)
            col_test1.metric("Glissement Constaté", f"{glissement:.2%}")
            col_test2.metric("Seuil Légal", "3.50%")
            
            if is_plafonne and cas != "D":
                st.warning("👉 Le glissement est supérieur à 3,5%. La formule de plafonnement s'applique.")
            elif cas != "D":
                st.success("👉 Le glissement est inférieur à 3,5%. Le plafonnement ne s'applique pas.")

            st.markdown("### 3. Application Mathématique")
            st.write("La formule applicable est la suivante :")
            st.latex(formule_latex)
            
            st.write("**Détail numérique :**")
            # Affichage "Brut" pour vérification
            st.code(f"""
            Loyer Actuel : {loyer_actuel}
            Indice Ref (N-3) : {ilc_ref}
            Indice N-2 : {ilc_n2}
            Indice N-1 : {ilc_n1}
            Indice Rev (N) : {ilc_rev}
            
            Résultat calculé : {nouveau_loyer}
            """)
