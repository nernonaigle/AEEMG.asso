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
        if "valide" in statuts: return "valide"
        if "en_attente" in statuts: return "en_attente"
        return "non_paye"
    except: return "non_paye"

def process_media(file):
    if file is None: return None, None
    try:
        encoded = base64.b64encode(file.read()).decode()
        return f"data:{file.type};base64,{encoded}", file.type.split("/")[0]
    except: return None, None

# =========================================================
# DESIGN "ULTRA-LUMINEUX" (STYLE APPLE/FACEBOOK LIGHT)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

/* Reset global pour éviter le sombre */
.stApp {
    background: #F0F2F5 !important; /* Gris très clair style Facebook */
    color: #1c1e21 !important;
}

/* Container principal */
.main .block-container { max-width: 1100px !important; padding-top: 2rem; }

/* Cartes Blanches Lumineuses */
.glass-card {
    background: #FFFFFF !important;
    border-radius: 16px;
    padding: 25px;
    border: 1px solid #E4E6EB;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
    color: #1c1e21 !important;
}

/* Post Card */
.post-card {
    background: #FFFFFF !important;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 15px;
    border: 1px solid #E4E6EB;
}

/* Badges de Statut */
.badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 800;
}
.bg-success { background: #E7F3FF; color: #1877F2; } /* Bleu/Vert clair */
.bg-warning { background: #FFF9E0; color: #F7B928; } /* Jaune clair */
.bg-danger { background: #FFEBEB; color: #FA383E; }  /* Rouge clair */

/* Inputs & Boutons */
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] {
    background-color: #F0F2F5 !important;
    color: #1c1e21 !important;
    border: 1px solid #E4E6EB !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

div.stButton > button {
    background: #064e3b !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    border: none !important;
    width: 100% !important;
}

/* Sidebar Light */
[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E4E6EB; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# NAVIGATION & SESSION
# =========================================================
if "connecte" not in st.session_state: st.session_state.connecte = False

with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#064e3b;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        menu = st.radio("Navigation", ["🏠 Fil d'actualité", "💳 Cotisations", "🪪 Carte de Membre", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# =========================================================
# PAGES
# =========================================================
if not st.session_state.connecte:
    if menu == "🔑 Connexion":
        st.markdown("<div class='glass-card' style='max-width:500px; margin:auto;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:#064e3b;'>Connexion</h2>", unsafe_allow_html=True)
        em = st.text_input("Email")
        pw = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", em).eq("password", hasher_password(pw)).execute()
            if res.data and res.data[0].get("statut") == "approuve":
                st.session_state.connecte, st.session_state.user_info = True, res.data[0]
                st.rerun()
            else: st.error("Accès refusé.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    elif menu == "📝 Inscription":
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("reg"):
            c1, c2 = st.columns(2)
            n, p = c1.text_input("Nom"), c2.text_input("Prénom")
            v, o = c1.text_input("Ville"), c2.selectbox("Organe", ["National", "Universitaire", "Scolaire"])
            e, pw = st.text_input("Email"), st.text_input("Pass", type="password")
            if st.form_submit_button("S'inscrire"):
                data = {"nom": n.upper(), "prenom": p.capitalize(), "email": e.lower(), "password": hasher_password(pw), "ville": v, "organe_de_base": o, "statut": "en_attente"}
                supabase.table("membres").insert(data).execute()
                st.success("Demande envoyée !")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    u = st.session_state.user_info
    c_status = check_cotisation_du_mois(u['id'])
    
    if menu == "🏠 Fil d'actualité":
        # HEADER PROFIL FACEBOOK STYLE
        badge_html = f'<span class="badge bg-success">À Jour</span>' if c_status == "valide" else (f'<span class="badge bg-warning">En attente</span>' if c_status == "en_attente" else f'<span class="badge bg-danger">Non Payé</span>')
        
        st.markdown(f"""
        <div style="background: white; border-radius: 0 0 15px 15px; border: 1px solid #E4E6EB; margin-bottom: 20px;">
            <div style="height: 150px; background: linear-gradient(90deg, #064e3b, #D4AF37); border-radius: 15px 15px 0 0;"></div>
            <div style="padding: 20px; display: flex; align-items: center; gap: 20px; margin-top: -50px;">
                <img src="https://www.w3schools.com/howto/img_avatar.png" style="width: 100px; height: 100px; border-radius: 50%; border: 4px solid white; background: white;">
                <div style="margin-top: 30px;">
                    <h2 style="margin:0; color:#1c1e21;">{u['prenom']} {u['nom']}</h2>
                    <p style="margin:0; color:#65676b; font-weight:600;">{u['organe_de_base']} • {badge_html}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_l, col_r = st.columns([1, 1.8])
        with col_l:
            st.markdown(f"<div class='glass-card'><h4>Infos</h4><b>Ville:</b> {u['ville']}<br><b>Email:</b> {u['email']}</div>", unsafe_allow_html=True)
            if c_status != "valide":
                st.warning("Pensez à régulariser votre cotisation !")

        with col_r:
            with st.form("post", clear_on_submit=True):
                t = st.text_area("Quoi de neuf ?", placeholder=f"Exprimez-vous {u['prenom']}...")
                if st.form_submit_button("Publier"):
                    supabase.table("posts").insert({"user_id": u['id'], "auteur_nom": f"{u['prenom']} {u['nom']}", "contenu": t, "date_pub": datetime.now().isoformat()}).execute()
                    st.rerun()
            
            # Posts
            posts = supabase.table("posts").select("*").order("date_pub", desc=True).limit(5).execute()
            for p in posts.data:
                st.markdown(f"<div class='post-card'><b>{p['auteur_nom']}</b><br><small>{p['date_pub'][:10]}</small><p>{p['contenu']}</p></div>", unsafe_allow_html=True)

    elif menu == "💳 Cotisations":
        st.markdown(f"### Cotisation de {calendar.month_name[date.today().month]}")
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("pay"):
            mt = st.number_input("Montant (GNF)", value=5000)
            rf = st.text_input("Référence de transaction (Orange/Momo)")
            if st.form_submit_button("Envoyer la preuve"):
                supabase.table("cotisations").insert({"user_id": u['id'], "montant": mt, "reference": rf, "statut": "en_attente", "date_paiement": datetime.now().isoformat()}).execute()
                st.success("Preuve envoyée à l'administration !")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("#### Historique")
        hist = supabase.table("cotisations").select("*").eq("user_id", u['id']).execute()
        for h in hist.data:
            st.info(f"{h['date_paiement'][:10]} - {h['montant']} GNF - Statut: {h['statut']}")

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()
