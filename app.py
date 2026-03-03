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
st.set_page_config(page_title="AEEMG - Community", page_icon="🌙", layout="wide")

# =========================================================
# CONNEXION SUPABASE
# =========================================================
SUPABASE_URL = "https://ryfrekltrgaqyryzozhc.supabase.co"
SUPABASE_KEY = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# FONCTIONS
# =========================================================
def hasher_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_cotisation_du_mois(user_id) -> str:
    if not user_id: return "non_paye"
    today = date.today()
    first_day = today.replace(day=1).isoformat()
    try:
        res = supabase.table("cotisations").select("statut").eq("user_id", user_id).gte("date_paiement", first_day).execute()
        if not res.data: return "non_paye"
        statuts = [r['statut'] for r in res.data]
        return "valide" if "valide" in statuts else ("en_attente" if "en_attente" in statuts else "non_paye")
    except: return "non_paye"

# =========================================================
# DESIGN "MODERN GLASS" (STYLE EXACT DE L'IMAGE)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

/* FOND D'ÉCRAN AVEC IMAGE */
.stApp {
    background: linear-gradient(rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.8)), 
                url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

/* TYPOGRAPHIE ET COULEURS DE TEXTE */
html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #1e293b; }
h1, h2, h3, h4 { color: white !important; font-weight: 800 !important; }

/* CARTES BLANCHES (DESIGN DE L'IMAGE) */
.glass-card {
    background: #FFFFFF !important;
    border-radius: 24px !important;
    padding: 30px !important;
    border: none !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
    margin-bottom: 25px;
    color: #1e293b !important;
}

/* BOUTONS STYLE PILULE (STYLE IMAGE) */
div.stButton > button {
    background: #10b981 !important; /* Vert émeraude */
    color: white !important;
    border-radius: 50px !important;
    padding: 10px 25px !important;
    font-weight: 700 !important;
    border: none !important;
    transition: 0.3s;
}
div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.4); }

/* INPUTS LISIBLES */
.stTextInput input, .stTextArea textarea {
    background-color: #f8fafc !important;
    color: #1e293b !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

/* SIDEBAR MODERNE */
[data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(10px); border-right: 1px solid rgba(255, 255, 255, 0.1); }
[data-testid="stSidebarNav"] span { color: white !important; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# NAVIGATION & SESSION
# =========================================================
if "connecte" not in st.session_state: st.session_state.connecte = False

with st.sidebar:
    st.markdown("<h1 style='text-align:center; font-size: 1.5rem;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
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
        col_c, col_v = st.columns([1, 1])
        with col_c:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color:#1e293b !important;'>Se connecter</h3>", unsafe_allow_html=True)
            em = st.text_input("VOTRE EMAIL")
            pw = st.text_input("MOT DE PASSE", type="password")
            if st.button("Se connecter"):
                res = supabase.table("membres").select("*").eq("email", em).eq("password", hasher_password(pw)).execute()
                if res.data and res.data[0].get("statut") == "approuve":
                    st.session_state.connecte, st.session_state.user_info = True, res.data[0]
                    st.rerun()
                else: st.error("Identifiants incorrects ou compte non validé.")
            st.markdown("</div>", unsafe_allow_html=True)
    
    elif menu == "📝 Inscription":
        st.markdown("<h1>Rejoindre l'AEEMG</h1>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("reg"):
            c1, c2 = st.columns(2)
            n, p = c1.text_input("NOM"), c2.text_input("PRÉNOM")
            v, o = c1.text_input("VILLE"), c2.selectbox("ORGANE", ["National", "Universitaire", "Scolaire"])
            e, pw = st.text_input("EMAIL"), st.text_input("MOT DE PASSE", type="password")
            if st.form_submit_button("S'INSCRIRE"):
                data = {"nom": n.upper(), "prenom": p.capitalize(), "email": e.lower(), "password": hasher_password(pw), "ville": v, "organe_de_base": o, "statut": "en_attente"}
                supabase.table("membres").insert(data).execute()
                st.success("Dossier envoyé !")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    u = st.session_state.user_info
    c_status = check_cotisation_du_mois(u['id'])
    
    if menu == "🏠 Fil d'actualité":
        st.markdown(f"<h1>Bienvenue, {u['prenom']}</h1>", unsafe_allow_html=True)
        
        col_l, col_r = st.columns([1, 1.5])
        
        with col_l:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color:#1e293b !important;'>Votre Profil</h3>", unsafe_allow_html=True)
            st.write(f"**Organe:** {u['organe_de_base']}")
            st.write(f"**Ville:** {u['ville']}")
            status_color = "#10b981" if c_status == "valide" else "#f59e0b"
            st.markdown(f"**Cotisation:** <span style='color:{status_color}; font-weight:800;'>{c_status.upper()}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_r:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color:#1e293b !important;'>Cotisations</h3>", unsafe_allow_html=True)
            st.write("Vérifiez votre statut du mois et générez votre carte.")
            if st.button("Vérifier mes paiements"):
                st.info("Redirection vers l'onglet Cotisation...")
            st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "💳 Cotisations":
        st.markdown("<h1>Cotisations du mois</h1>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("pay"):
            mt = st.number_input("MONTANT GNF", value=5000)
            rf = st.text_input("RÉFÉRENCE DE TRANSACTION")
            if st.form_submit_button("ENVOYER LA PREUVE"):
                supabase.table("cotisations").insert({"user_id": u['id'], "montant": mt, "reference": rf, "statut": "en_attente", "date_paiement": datetime.now().isoformat()}).execute()
                st.success("Preuve enregistrée !")
        st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()
