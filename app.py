import streamlit as st
from supabase import create_client

# 1. Connexion Supabase (Inchangée)
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- 🎨 DESIGN "ÉMERAUDE & MOSQUÉE" ---
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

css_style = """
    <style>
    .stApp {
        background: linear-gradient(rgba(18, 54, 38, 0.9), rgba(18, 54, 38, 0.9)), 
                    url("https://images.unsplash.com/photo-1590076214667-cda9e7b1ff34?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    [data-testid="stForm"], [data-testid="stMetric"], .stChatMessage {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(15px);
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 20px !important;
    }

    h1, h2, h3, label, p, span {
        color: white !important;
    }

    .stButton>button {
        background-color: #2D6A4F !important;
        color: white !important;
        border-radius: 12px;
        border: 1px solid #40916C;
        font-weight: bold;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(8, 28, 21, 0.95) !important;
    }
    </style>
"""
st.markdown(css_style, unsafe_allow_html=True)

# 2. Gestion de la Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- LA SUITE DE TON CODE (MENU, PAGES...) ---
    <style>
    /* Image de fond floue sur toute l'application */
    .stApp {
        background: linear-gradient(st.markdown("""
    <style>
    /* Image de fond : Intérieur de mosquée avec voile vert */
    .stApp {
        background: linear-gradient(rgba(18, 54, 38, 0.88), rgba(18, 54, 38, 0.88)), 
                    url("https://images.unsplash.com/photo-1590076214667-cda9e7b1ff34?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Boites de lecture (Glassmorphism) */
    .stForm, .css-1r6slb0, .stMetric {
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        color: white !important;
    }
    
    h1, h2, h3, label, p {
        color: #F0FDF4 !important; /* Un blanc légèrement teinté de vert */
    }
    </style>
    """, unsafe_allow_html=True));
        background-size: cover;
        background-attachment: fixed;
    }

    /* Style des textes */
    h1, h2, h3, p {
        color: white !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Boites blanches semi-transparentes pour les formulaires */
    .stForm, .css-1r6slb0, .stMetric {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 20px !important;
        color: white !important;
    }

    /* Bouton vert AEEMG */
    .stButton>button {
        background-color: #2D6A4F !important;
        color: white !important;
        border: 1px solid #40916C !important;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #40916C !important;
        border: 1px solid #FFD700 !important; /* Or au survol */
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(8, 28, 21, 0.95) !important;
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
