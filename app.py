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

def process_media(file, is_profile=False):
    if file is None: return None, None
    try:
        file_type = file.type.split("/")[0]
        if file_type == "image":
            img = Image.open(file)
            size = (300, 300) if is_profile else (800, 800)
            img.thumbnail(size)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            encoded = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{encoded}", "image"
        else:
            encoded = base64.b64encode(file.read()).decode()
            return f"data:{file.type};base64,{encoded}", "video"
    except Exception as e:
        st.error(f"Erreur média : {e}")
        return None, None

# =========================================================
# DESIGN / CSS OPTIMISÉ
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }

.main .block-container { max-width: 1100px; padding-top: 2rem; }

.stApp {
    background: linear-gradient(135deg, rgba(255,255,255,0.4), rgba(255,255,255,0.6)),
    url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

/* --- SIDEBAR BLANCHE --- */
[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #0f172a !important; font-weight: 600 !important; }

/* --- CHAMPS DE SAISIE LISIBLES --- */
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    font-weight: 600 !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 12px !important;
}
div[data-baseweb="select"] > div { color: #000000 !important; }

label p { font-weight: 800 !important; color: #064e3b !important; }

.glass-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 25px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}

.post-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 20px;
    border-left: 6px solid #D4AF37;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    margin-bottom: 15px;
}

.gold-text {
    background: linear-gradient(90deg, #B8860B, #D4AF37);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

div.stButton > button { border-radius: 10px; background: #064e3b; color: white; font-weight: 700; width: 100%; }
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
    st.markdown("<h1 style='text-align:center; color:#064e3b; font-size: 1.6rem;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        u = st.session_state.user_info
        st.markdown(f"<p style='text-align:center;'>Membre : <b>{u['prenom']}</b></p>", unsafe_allow_html=True)
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
    st.markdown("<h1 class='gold-text' style='text-align:center;'>🤝 Inscription</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("inscription"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("Nom de famille")
            prenom = c2.text_input("Prénom")
            ville = c1.text_input("Ville de résidence")
            organe_de_base = c2.selectbox("Organe de base", ["Bureau National", "Section Universitaire", "Section Scolaire", "Section Communale", "Antenne Régionale"], index=None, placeholder="Choisir...")
            email = st.text_input("Email")
            p1, p2 = st.columns(2)
            password = p1.text_input("Mot de passe", type="password")
            confirm = p2.text_input("Confirmer le mot de passe", type="password")
            motivation = st.text_area("Motivation")
            
            if st.form_submit_button("🚀 VALIDER"):
                if not all([nom, prenom, email, password, ville, organe_de_base]): st.error("Champs requis !")
                elif password != confirm: st.error("Mots de passe différents !")
                else:
                    data = {"nom": nom.upper(), "prenom": prenom.capitalize(), "email": email.lower(), "password": hasher_password(password), "ville": ville, "organe_de_base": organe_de_base, "motivation": motivation, "statut": "en_attente"}
                    supabase.table("membres").insert(data).execute()
                    st.success("Dossier envoyé !")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.connecte:
    u = st.session_state.user_info
    
    if menu == "🏠 Tableau de Bord":
        # HEADER (BANNIÈRE + AVATAR)
        st.markdown(f"""
        <div style="position: relative; margin-bottom: 80px;">
            <div style="height: 180px; background: linear-gradient(90deg, #064e3b, #D4AF37); border-radius: 20px;"></div>
            <div style="position: absolute; bottom: -40px; left: 30px; display: flex; align-items: flex-end; gap: 15px;">
                <img src="{u.get('photo_url') or 'https://www.w3schools.com/howto/img_avatar.png'}" style="width: 110px; height: 110px; border-radius: 50%; border: 4px solid white; object-fit: cover; background: white;">
                <div style="padding-bottom: 10px;">
                    <h2 style="margin: 0; color: #064e3b;">{u.get('prenom')} {u.get('nom')}</h2>
                    <p style="margin: 0; font-weight: 700; color: #475569;">📍 {u.get('organe_de_base')}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 2], gap="medium")

        with col_left:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 📌 Infos")
            st.write(f"📧 **Email:** {u.get('email')}")
            st.write(f"🏙️ **Ville:** {u.get('ville')}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            # FORMULAIRE DE POST
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            with st.form("post_form", clear_on_submit=True):
                txt = st.text_area("Exprimez-vous...", placeholder=f"Quoi de neuf, {u.get('prenom')} ?")
                media = st.file_uploader("Image ou Vidéo", type=['jpg','png','mp4'])
                if st.form_submit_button("🚀 Publier"):
                    m_url, m_type = process_media(media)
                    new_post = {"user_id": u['id'], "auteur_nom": f"{u['prenom']} {u['nom']}", "auteur_photo": u.get("photo_url"), "contenu": txt, "media_url": m_url, "media_type": m_type, "date_pub": datetime.now().isoformat()}
                    supabase.table("posts").insert(new_post).execute()
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            # FLUX DE POSTS
            res_posts = supabase.table("posts").select("*").order("date_pub", desc=True).limit(10).execute()
            for post in res_posts.data:
                st.markdown(f"""
                <div class="post-card">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                        <img src="{post.get('auteur_photo') or 'https://www.w3schools.com/howto/img_avatar.png'}" style="width:40px; height:40px; border-radius:50%; object-fit: cover;">
                        <b>{post.get('auteur_nom')}</b>
                    </div>
                    <p>{post.get('contenu')}</p>
                </div>
                """, unsafe_allow_html=True)
                if post.get("media_url"):
                    if post.get("media_type") == "image": st.image(post["media_url"])
                    else: st.video(post["media_url"])

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()
