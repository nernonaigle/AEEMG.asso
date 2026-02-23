import streamlit as st
from supabase import create_client

# 1. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- 🎨 CONFIGURATION DESIGN & COULEURS ---
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    /* Fond dégradé et couleurs */
    .stApp {
        background: linear-gradient(to right, #ece9e6, #ffffff);
    }
    .sidebar .sidebar-content {
        background-color: #1E3A8A;
    }
    h1 {
        color: #1E3A8A;
        font-family: 'Arial Black', sans-serif;
        text-shadow: 2px 2px 4px #0000001a;
    }
    .stButton>button {
        background: linear-gradient(to right, #1E3A8A, #3B82F6);
        color: white;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        font-size: 18px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        color: #FFD700;
    }
    /* Cartes stylisées */
    .css-1r6slb0 { 
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Gestion Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- BARRE LATÉRALE ---
with st.sidebar:
    # Image Logo (Remplace par ton vrai logo si tu as un lien)
    st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=120)
    st.title("AEEMG")
    st.write("---")
    
    if not st.session_state.connecte:
        menu = st.radio("Navigation", ["🔑 Connexion", "📝 Inscription"])
    else:
        st.success(f"Connecté : {st.session_state.user_info['prenom']}")
        menu = st.radio("Espace Privé", ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "🚪 Déconnexion"])

# --- PAGES ---

if menu == "📝 Inscription":
    # Image de couverture
    st.image("https://images.unsplash.com/photo-1523240715181-014b9e30f06e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", caption="Rejoignez la communauté AEEMG")
    st.title("📝 Devenir Membre")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("inscription"):
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
            pwd = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer mon compte"):
                supabase.table("membres").insert({"nom":nom,"prenom":p,"email":e,"password":pwd,"cotisation":False}).execute()
                st.success("Compte créé ! Connectez-vous.")

elif menu == "🔑 Connexion":
    st.image("https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", width=800)
    st.title("🔑 Accès Membre")
    e_l = st.text_input("Email")
    p_l = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        res = supabase.table("membres").select("*").eq("email", e_l).eq("password", p_l).execute()
        if res.data:
            st.session_state.connecte, st.session_state.user_info = True, res.data[0]
            st.rerun()

elif st.session_state.connecte:
    user = st.session_state.user_info
    
    if menu == "🏠 Tableau de Bord":
        st.title(f"👋 Bienvenue, {user['prenom']} !")
        # Cartes de couleurs
        c1, c2, c3 = st.columns(3)
        c1.markdown("<div style='background-color:#1E3A8A; color:white; padding:20px; border-radius:10px;'><h3>Statut</h3><p>Membre Actif</p></div>", unsafe_allow_html=True)
        
        status_color = "#10B981" if user.get('cotisation') else "#EF4444"
        status_text = "À JOUR" if user.get('cotisation') else "À RÉGLER"
        c2.markdown(f"<div style='background-color:{status_color}; color:white; padding:20px; border-radius:10px;'><h3>Cotisation</h3><p>{status_text}</p></div>", unsafe_allow_html=True)
        
        c3.markdown("<div style='background-color:#F59E0B; color:white; padding:20px; border-radius:10px;'><h3>Points</h3><p>150 XP</p></div>", unsafe_allow_html=True)

    elif menu == "🚪 Déconnexion":
        st.session_state.connecte = False
        st.rerun()

# (Ajoute ici les autres pages Cotisations/Documents avec le même style)
