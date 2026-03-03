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
# DESIGN / CSS MODERN LIGHT GLASS (Theme Blanc)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

html, body, [class*="st-"] { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    color: #1e293b;
}

/* Fond avec image bien visible et voile blanc léger */
.stApp {
    background: linear-gradient(135deg, rgba(255,255,255,0.3), rgba(255,255,255,0.5)),
    url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

/* Sidebar en mode blanc flou */
[data-testid="stSidebar"] {
    background-color: rgba(255, 255, 255, 0.7) !important;
    backdrop-filter: blur(15px);
    border-right: 1px solid rgba(255,255,255,0.3);
}

/* Cartes blanches effet "Verre Dépoli" */
.glass-card {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.8);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
    margin-bottom: 20px;
    color: #1e293b;
}

/* Posts avec bordure dorée */
.post-card {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 20px;
    padding: 20px;
    border-left: 5px solid #D4AF37;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    margin-bottom: 25px;
    color: #1e293b;
}

/* Titres en dégradé Doré/Sombre */
.gold-text {
    background: linear-gradient(90deg, #B8860B, #D4AF37);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

/* Inputs plus élégants */
.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.9) !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
}

/* Boutons */
div.stButton > button {
    border-radius: 12px;
    background: #064e3b;
    color: white;
    border: none;
    transition: 0.3s;
    font-weight: 600;
}
div.stButton > button:hover {
    background: #D4AF37;
    color: white;
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
    st.markdown("<h1 style='text-align:center; color:#064e3b; font-size: 1.8rem;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    
    if st.session_state.connecte:
        u = st.session_state.user_info
        est_a_jour = check_cotisation_du_mois(u.get("id"))
        
        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            avatar = u.get("photo_url") if u.get("photo_url") else "https://www.w3schools.com/howto/img_avatar.png"
            st.image(avatar, width=65)
        with col_s2:
            st.markdown(f"**{u.get('prenom')}**")
            badge = "✅" if est_a_jour else "⚠️"
            st.caption(f"{badge} Cotisation")
        
        st.write("---")
        menu = st.radio("Navigation", ["🏠 Tableau de Bord", "💳 Cotisations", "🪪 Carte de Membre", "📂 Documents", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# =========================================================
# PAGES
# =========================================================
if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text'>Connexion</h2>", unsafe_allow_html=True)
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
    st.markdown("<h2 class='gold-text'>Demande d'adhésion</h2>", unsafe_allow_html=True)
    with st.form("inscription"):
        col1, col2 = st.columns(2)
        nom = col1.text_input("Nom")
        prenom = col2.text_input("Prénom")
        email = col1.text_input("Email")
        password = col2.text_input("Mot de passe", type="password")
        photo = st.file_uploader("Photo de profil", type=['jpg', 'png'])
        if st.form_submit_button("Envoyer le dossier"):
            p_url, _ = process_media(photo, is_profile=True)
            data = {"nom": nom, "prenom": prenom, "email": email, "password": hasher_password(password), "statut": "en_attente", "photo_url": p_url}
            supabase.table("membres").insert(data).execute()
            st.success("Dossier envoyé !")

elif st.session_state.connecte:
    u = st.session_state.user_info

    if menu == "🏠 Tableau de Bord":
        st.markdown(f"<h1 class='gold-text'>Salam, {u.get('prenom')}</h1>", unsafe_allow_html=True)
        
        # Publication
        with st.container():
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            with st.form("post_form", clear_on_submit=True):
                txt = st.text_area("Quoi de neuf ?", placeholder="Partagez avec la communauté...")
                media = st.file_uploader("Image/Vidéo", type=['jpg','png','mp4'])
                if st.form_submit_button("Publier"):
                    m_url, m_type = process_media(media)
                    new_post = {
                        "user_id": u['id'], "auteur_nom": f"{u['prenom']} {u['nom']}",
                        "auteur_photo": u.get("photo_url"), "contenu": txt,
                        "media_url": m_url, "media_type": m_type, "date_pub": datetime.now().isoformat()
                    }
                    supabase.table("posts").insert(new_post).execute()
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Fil d'actu
        res_posts = supabase.table("posts").select("*").order("date_pub", desc=True).limit(10).execute()
        for post in res_posts.data:
            with st.container():
                st.markdown(f"""
                <div class="post-card">
                    <img src="{post.get('auteur_photo') or 'https://www.w3schools.com/howto/img_avatar.png'}" style="width:35px; height:35px; border-radius:50%; margin-right:10px; vertical-align:middle; border: 1px solid #D4AF37;">
                    <b style="color: #064e3b;">{post.get('auteur_nom')}</b> • <small style="color: #64748b;">{post.get('date_pub')[:10]}</small>
                    <p style="margin-top:10px; color: #334155;">{post.get('contenu')}</p>
                </div>
                """, unsafe_allow_html=True)
                if post.get("media_url"):
                    if post.get("media_type") == "image": st.image(post["media_url"])
                    else: st.video(post["media_url"])

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()

else:
    st.warning("Veuillez vous connecter.")
