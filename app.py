import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime, date
import calendar

# =========================================================
# CONFIGURATION ET CONNEXION
# =========================================================
st.set_page_config(page_title="AEEMG - Community", page_icon="🌙", layout="wide")

SUPABASE_URL = "https://ryfrekltrgaqyryzozhc.supabase.co"
SUPABASE_KEY = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# DESIGN "ULTRA-LISIBLE" (CORRECTION CONTRASTE)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

/* FOND D'ÉCRAN AVEC COUCHE SOMBRE POUR LISIBILITÉ */
.stApp {
    background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

/* TEXTE GLOBAL (SUR LE FOND SOMBRE) -> BLANC */
html, body, [class*="st-"], .stMarkdown p { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    color: #FFFFFF !important; 
}

/* TITRES EN OR/BLANC */
h1, h2, h3 { color: #D4AF37 !important; font-weight: 800 !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }

/* --- CARTES BLANCHES (CONTENU INTERNE) --- */
.glass-card {
    background: #FFFFFF !important;
    border-radius: 24px !important;
    padding: 30px !important;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
    margin-bottom: 25px;
    border: none !important;
}

/* TEXTE À L'INTÉRIEUR DES CARTES -> NOIR PROFOND */
.glass-card p, .glass-card span, .glass-card label, .glass-card div {
    color: #0f172a !important; 
    font-weight: 600;
}

/* CHAMPS DE SAISIE (INPUTS) */
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

/* BOUTONS STYLE PILULE VERTE */
div.stButton > button {
    background: #10b981 !important;
    color: white !important;
    border-radius: 50px !important;
    font-weight: 800 !important;
    border: none !important;
    height: 3.5rem;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

/* SIDEBAR TEXTE */
[data-testid="stSidebar"] { background-color: rgba(0,0,0,0.8) !important; }
[data-testid="stSidebar"] * { color: white !important; }

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGIQUE DE SESSION
# =========================================================
if "connecte" not in st.session_state: st.session_state.connecte = False

def hasher_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================
# NAVIGATION SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("<h1 style='text-align:center; font-size: 1.8rem; color:#D4AF37 !important;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        menu = st.radio("MENU", ["🏠 Fil d'actualité", "💳 Cotisations", "🪪 Ma Carte", "🚪 Déconnexion"])
    else:
        menu = st.radio("ACCÈS", ["🔑 Connexion", "📝 Inscription"])

# =========================================================
# PAGES
# =========================================================
if not st.session_state.connecte:
    if menu == "🔑 Connexion":
        st.markdown("<h1 style='text-align:center;'>Fil d'actualité</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h2 style='color:#0f172a !important; text-align:center;'>Se connecter</h2>", unsafe_allow_html=True)
            em = st.text_input("EMAIL")
            pw = st.text_input("MOT DE PASSE", type="password")
            if st.button("ACCÉDER AU RÉSEAU"):
                res = supabase.table("membres").select("*").eq("email", em).eq("password", hasher_password(pw)).execute()
                if res.data and res.data[0].get("statut") == "approuve":
                    st.session_state.connecte, st.session_state.user_info = True, res.data[0]
                    st.rerun()
                else: st.error("Identifiants incorrects ou compte non validé.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "📝 Inscription":
        st.markdown("<h1 style='text-align:center;'>Rejoindre la Communauté</h1>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            # Les champs ici seront écrits en noir car ils sont dans 'glass-card'
            with st.form("inscription_form"):
                c1, c2 = st.columns(2)
                nom = c1.text_input("NOM")
                pre = c2.text_input("PRÉNOM")
                if st.form_submit_button("ENVOYER MA DEMANDE"):
                    st.success("Dossier envoyé !")
            st.markdown("</div>", unsafe_allow_html=True)

else:
    u = st.session_state.user_info
    
    if menu == "🏠 Fil d'actualité":
        st.markdown(f"<h1>Ravi de vous voir, {u['prenom']} !</h1>", unsafe_allow_html=True)
        
        col_l, col_r = st.columns([1, 2])
        
        with col_l:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 👤 Mon Profil")
            st.markdown(f"**Nom:** {u['nom']} {u['prenom']}")
            st.markdown(f"**Organe:** {u['organe_de_base']}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_r:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 💳 Cotisations du mois")
            st.markdown("Votre statut est actuellement : **En attente**")
            if st.button("Payer maintenant"):
                st.write("Redirection...")
            st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()
