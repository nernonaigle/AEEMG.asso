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
# DESIGN / CSS OPTIMISÉ (SIDEBAR CLAIRE & LISIBILITÉ)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="st-"] { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
}

/* Centrage et réduction de la largeur du bloc principal */
.main .block-container {
    max-width: 1000px;
    padding-top: 2rem;
}

.stApp {
    background: linear-gradient(135deg, rgba(255,255,255,0.4), rgba(255,255,255,0.6)),
    url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

/* --- SIDEBAR CLAIRE (LUMINEUSE) --- */
[data-testid="stSidebar"] {
    background-color: #ffffff !important; /* Fond blanc pur */
    border-right: 1px solid #e2e8f0;
}

/* Texte du menu radio dans la sidebar */
[data-testid="stSidebar"] .st-emotion-cache-1647it7, 
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] span {
    color: #0f172a !important;
    font-weight: 600 !important;
}

/* --- CHAMPS DE SAISIE (LISIBILITÉ MAX) --- */
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    font-weight: 600 !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 12px !important;
}

/* Correction texte Selectbox */
div[data-baseweb="select"] > div {
    color: #000000 !important;
}

label p {
    font-weight: 800 !important;
    color: #064e3b !important;
    font-size: 1rem !important;
}

.glass-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 30px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
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
# SIDEBAR (CONTENU)
# =========================================================
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#064e3b; font-size: 1.8rem; margin-bottom: 20px;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        u = st.session_state.user_info
        st.markdown(f"<p style='text-align:center;'>Bienvenue,<br><b>{u['prenom']}</b></p>", unsafe_allow_html=True)
        st.write("---")
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
    st.markdown("<h1 class='gold-text' style='text-align:center;'>🤝 Rejoindre l'AEEMG</h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("inscription", clear_on_submit=False):
            st.markdown("<h4 style='color: #064e3b;'>👤 Identité & Localisation</h4>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom de famille")
            prenom = c2.text_input("Prénom")
            ville = c1.text_input("Ville de résidence")
            
            organe_de_base = c2.selectbox(
                "Organe de base",
                ["Bureau National", "Section Universitaire", "Section Scolaire", "Section Communale", "Antenne Régionale"],
                index=None,
                placeholder="Sélectionnez..."
            )
            
            st.markdown("<br><h4 style='color: #064e3b;'>🔐 Sécurité</h4>", unsafe_allow_html=True)
            email = st.text_input("Email")
            p1, p2 = st.columns(2)
            password = p1.text_input("Mot de passe", type="password")
            confirm = p2.text_input("Confirmer le mot de passe", type="password")
            
            st.markdown("<br><h4 style='color: #064e3b;'>📝 Motivation</h4>", unsafe_allow_html=True)
            motivation = st.text_area("Pourquoi souhaitez-vous nous rejoindre ?")
            
            if st.form_submit_button("🚀 ENVOYER MON DOSSIER"):
                if not all([nom, prenom, email, password, ville, organe_de_base, motivation]):
                    st.error("⚠️ Tous les champs sont obligatoires.")
                elif password != confirm:
                    st.error("❌ Les mots de passe ne correspondent pas.")
                else:
                    with st.spinner("Enregistrement..."):
                        data = {
                            "nom": nom.upper(), 
                            "prenom": prenom.capitalize(), 
                            "email": email.lower().strip(), 
                            "password": hasher_password(password),
                            "ville": ville, 
                            "organe_de_base": organe_de_base,
                            "motivation": motivation, 
                            "statut": "en_attente"
                        }
                        try:
                            supabase.table("membres").insert(data).execute()
                            st.balloons()
                            st.success("🎉 Dossier envoyé ! Votre compte est en attente de validation.")
                        except Exception as e:
                            st.error(f"Erreur : {e}")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.connecte:
    u = st.session_state.user_info
    if menu == "🏠 Tableau de Bord":
        st.markdown(f"<h2 class='gold-text'>Bienvenue, {u['prenom']} !</h2>", unsafe_allow_html=True)
        st.info("Espace membre en cours de mise à jour.")

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()
