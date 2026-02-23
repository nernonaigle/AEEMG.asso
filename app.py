import streamlit as st
from supabase import create_client

# 1. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- 🎨 DESIGN "ÉMERAUDE & SÉRÉNITÉ" ---
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

st.markdown("""

<style>
.stApp {
background-image: linear-gradient(rgba(18, 54, 38, 0.8), rgba(18, 54, 38, 0.8)),
url("");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: fixed;
}
[data-testid="stHeader"] {
background: rgba(0,0,0,0);
}
h1, h2, h3, label, p {
color: white !important;
text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}
</style>

""", unsafe_allow_html=True)
# 2. Gestion de Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    st.write("---")
    if not st.session_state.connecte:
        menu = st.radio("Navigation", ["🔑 Connexion", "📝 Inscription"])
    else:
        st.success(f"Bienvenue {st.session_state.user_info['prenom']}")
        menu = st.radio("Espace Privé", ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "🚪 Déconnexion"])

# --- CONTENU DES PAGES ---

if menu == "📝 Inscription":
    st.markdown("<h1>✨ Rejoindre la communauté</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form("inscription"):
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
            pwd = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer mon compte"):
                supabase.table("membres").insert({"nom":nom,"prenom":prenom,"email":email,"password":pwd,"cotisation":False}).execute()
                st.success("Compte créé avec succès !")
    with col2:
        st.markdown("""
        ### Pourquoi adhérer ?
        - Accès aux ressources éducatives
        - Participation aux événements fraternels
        - Soutien à la vie étudiante
        """)

elif menu == "🔑 Connexion":
    st.markdown("<h1 style='text-align: center;'>🔑 Accès Membre</h1>", unsafe_allow_html=True)
    _, cent, _ = st.columns([1, 1, 1])
    with cent:
        e_l = st.text_input("Email")
        p_l = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", e_l).eq("password", p_l).execute()
            if res.data:
                st.session_state.connecte, st.session_state.user_info = True, res.data[0]
                st.rerun()
            else:
                st.error("Identifiants incorrects")

elif menu == "🏠 Tableau de Bord":
    u = st.session_state.user_info
    st.markdown(f"<h1>👋 Paix sur toi, {u['prenom']}</h1>", unsafe_allow_html=True)
    
    # Statistiques en cartes transparentes
    c1, c2, c3 = st.columns(3)
    c1.metric("Statut", "Membre Actif")
    c2.metric("Année", "2026")
    c3.metric("Cotisation", "✅ Payée" if u.get('cotisation') else "❌ À régler")

elif menu == "🚪 Déconnexion":
    st.session_state.connecte = False
    st.rerun()
