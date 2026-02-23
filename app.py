import streamlit as st
from supabase import create_client

# 1. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- CONFIGURATION DU DESIGN ---
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🎓", layout="centered")

# Petit CSS pour personnaliser les couleurs (Exemple : Bleu et Or)
# --- CONFIGURATION DU DESIGN ---
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🎓", layout="centered")

# CSS corrigé pour personnaliser les couleurs
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #1E3A8A; color: white; }
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True) # <-- C'était ici l'erreur, c'est 'html' et non 'status'
# 2. Gestion de la connexion
if "connecte" not in st.session_state:
    st.session_state.connecte = False
    st.session_state.user_info = None

# --- BARRE LATÉRALE ---
st.sidebar.image("https://img.icons8.com/fluency/96/education.png", width=80) # Un petit logo par défaut
st.sidebar.title("AEEMG")

if not st.session_state.connecte:
    menu = st.sidebar.radio("Menu", ["Connexion", "S'inscrire"])
else:
    st.sidebar.success(f"Connecté : {st.session_state.user_info['prenom']}")
    menu = st.sidebar.radio("Menu", ["🏠 Tableau de Bord", "📂 Mes Documents", "💳 Cotisations", "🚪 Déconnexion"])

# --- LOGIQUE DE DÉCONNEXION ---
if menu == "🚪 Déconnexion":
    st.session_state.connecte = False
    st.session_state.user_info = None
    st.rerun()

# --- PAGE D'INSCRIPTION ---
if menu == "S'inscrire":
    st.title("📝 Rejoindre l'AEEMG")
    with st.container():
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        email = st.text_input("Email")
        pwd = st.text_input("Mot de passe", type="password")
        if st.button("Valider l'inscription"):
            if nom and prenom and email and pwd:
                data = {"nom": nom, "prenom": prenom, "email": email, "password": pwd}
                supabase.table("membres").insert(data).execute()
                st.success("Compte créé avec succès !")
            else:
                st.error("Champs manquants")

# --- PAGE DE CONNEXION ---
elif menu == "Connexion":
    st.title("🔑 Espace Membre")
    col1, col2 = st.columns([1, 2]) # Pour centrer un peu
    with col2:
        email_login = st.text_input("Email")
        pwd_login = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", email_login).eq("password", pwd_login).execute()
            if len(res.data) > 0:
                st.session_state.connecte = True
                st.session_state.user_info = res.data[0]
                st.rerun()
            else:
                st.error("Identifiants incorrects")

# --- ESPACE MEMBRE PRIVÉ ---
elif st.session_state.connecte:
    user = st.session_state.user_info
    
    if menu == "🏠 Tableau de Bord":
        st.title(f"👋 Bienvenue, {user['prenom']} !")
        
        # Affichage avec des colonnes pour faire "Dashboard"
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**Statut :** Membre Actif")
        with c2:
            st.info(f"**Cotisation :** ❌ Non payée") # On gérera ça après
            
        st.write("---")
        st.subheader("Dernières annonces")
        st.write("📢 Prochaine réunion de l'association prévue samedi prochain.")

    elif menu == "📂 Mes Documents":
        st.title("📁 Documents utiles")
        st.write("- Statuts de l'AEEMG")
        st.write("- Guide de l'étudiant")

    elif menu == "💳 Cotisations":
        st.title("💳 Ma Cotisation")
        st.write("Le paiement en ligne sera bientôt disponible.")
