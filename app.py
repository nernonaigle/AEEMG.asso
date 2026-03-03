import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime, date
import calendar
import base64
from io import BytesIO
from PIL import Image

# =========================================================
# CONFIGURATION PAGE
# =========================================================
st.set_page_config(
    page_title="AEEMG - Community",
    page_icon="🌙",
    layout="wide"
)

# =========================================================
# CONNEXION SUPABASE
# =========================================================
SUPABASE_URL = "https://ryfrekltrgaqyryzozhc.supabase.co"
SUPABASE_KEY = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# FONCTIONS UTILES
# =========================================================
def hasher_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_cotisation_du_mois(user_id) -> bool:
    if not user_id: return False
    today = date.today()
    first_day = today.replace(day=1).isoformat()
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1]).isoformat()
    try:
        res = supabase.table("cotisations").select("*").eq("user_id", user_id).eq("statut", "valide").gte("date_paiement", first_day).lte("date_paiement", last_day).execute()
        return len(res.data) > 0
    except Exception: return False

# =========================================================
# DESIGN / CSS OPTIMISÉ (LARGUEUR ET LISIBILITÉ)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="st-"] { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    color: #0f172a; 
}

/* Limiter la largeur centrale pour éviter que ce soit trop large */
.main .block-container {
    max-width: 900px;
    padding-top: 2rem;
}

.stApp {
    background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.4)),
    url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

/* --- CORRECTION LISIBILITÉ SELECTBOX & INPUTS --- */
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #0f172a !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    border: 1px solid #cbd5e1 !important;
}

/* Forcer la couleur du texte dans la liste déroulante */
div[data-baseweb="select"] > div {
    color: #0f172a !important;
}

label p {
    font-weight: 800 !important;
    color: #064e3b !important;
    font-size: 1rem !important;
}

.glass-card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 30px;
    border: 1px solid rgba(255,255,255,0.5);
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}

.gold-text {
    background: linear-gradient(90deg, #B8860B, #D4AF37);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

div.stButton > button {
    border-radius: 10px;
    background: #064e3b;
    color: white;
    font-weight: 700;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# INITIALISATION SESSION
# =========================================================
if "connecte" not in st.session_state: st.session_state.connecte = False
if "user_info" not in st.session_state: st.session_state.user_info = None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#064e3b;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        u = st.session_state.user_info
        menu = st.radio("Navigation", ["🏠 Tableau de Bord", "💳 Cotisations", "🪪 Carte de Membre", "📂 Documents", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# =========================================================
# PAGES
# =========================================================
if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>Connexion</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", email).eq("password", hasher_password(password)).execute()
            if res.data:
                user = res.data[0]
                if user.get("statut") == "approuve":
                    st.session_state.connecte = True
                    st.session_state.user_info = user
                    st.rerun()
                else: st.warning("Compte en attente de validation.")
            else: st.error("Identifiants incorrects.")
        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "📝 Inscription":
    st.markdown("<h1 class='gold-text' style='text-align:center;'>🤝 Inscription</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("inscription"):
            # Lignes réduites avec colonnes
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom de famille")
            prenom = c2.text_input("Prénom")
            
            email = c1.text_input("Email")
            ville = c2.text_input("Ville")
            
            organe_de_base = st.selectbox(
                "Organe de base",
                ["Bureau National", "Section Universitaire", "Section Scolaire", "Section Communale", "Antenne Régionale"],
                index=None, placeholder="Choisissez votre organe..."
            )
            
            p1, p2 = st.columns(2)
            password = p1.text_input("Mot de passe", type="password")
            confirm = p2.text_input("Confirmer le mot de passe", type="password")
            
            motivation = st.text_area("Motivation (Pourquoi nous rejoindre ?)")
            
            # Plus de champ photo ici 🙃
            
            if st.form_submit_button("🚀 VALIDER MON INSCRIPTION"):
                if not all([nom, prenom, email, password, ville, organe_de_base, motivation]):
                    st.error("⚠️ Veuillez remplir tous les champs.")
                elif password != confirm:
                    st.error("❌ Les mots de passe ne correspondent pas.")
                else:
                    data = {
                        "nom": nom.upper(), "prenom": prenom.capitalize(), 
                        "email": email.lower().strip(), "password": hasher_password(password),
                        "ville": ville, "organe_de_base": organe_de_base,
                        "motivation": motivation, "statut": "en_attente"
                    }
                    supabase.table("membres").insert(data).execute()
                    st.success("✅ Dossier envoyé ! En attente de validation.")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.connecte:
    # ... (Le reste du code pour le Tableau de Bord reste identique)
    st.write(f"Bienvenue {st.session_state.user_info['prenom']} !")
    if menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()
