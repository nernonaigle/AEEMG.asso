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
# DESIGN / CSS MODERN LIGHT GLASS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

html, body, [class*="st-"] { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    color: #1e293b;
}

.stApp {
    background: linear-gradient(135deg, rgba(255,255,255,0.3), rgba(255,255,255,0.5)),
    url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

[data-testid="stSidebar"] {
    background-color: rgba(255, 255, 255, 0.7) !important;
    backdrop-filter: blur(15px);
    border-right: 1px solid rgba(255,255,255,0.3);
}

.glass-card {
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.8);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
    margin-bottom: 20px;
}

.post-card {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 20px;
    padding: 20px;
    border-left: 5px solid #D4AF37;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    margin-bottom: 10px;
}

.gold-text {
    background: linear-gradient(90deg, #B8860B, #D4AF37);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

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
}

/* Style spécifique pour les boutons de like/comment sous les posts */
.stButton button[key^="like_"], .stButton button[key^="comm_"] {
    padding: 0.2rem 1rem !important;
    font-size: 0.8rem !important;
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
        # HEADER DE PROFIL (STYLE FACEBOOK)
        st.markdown(f"""
        <div style="position: relative; margin-bottom: 80px;">
            <div style="height: 180px; background: linear-gradient(90deg, #064e3b, #D4AF37); border-radius: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);"></div>
            <div style="position: absolute; bottom: -50px; left: 40px; display: flex; align-items: flex-end; gap: 20px;">
                <img src="{u.get('photo_url') or 'https://www.w3schools.com/howto/img_avatar.png'}" 
                     style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid rgba(255,255,255,0.9); object-fit: cover; box-shadow: 0 4px 12px rgba(0,0,0,0.15); background: white;">
                <div style="padding-bottom: 10px;">
                    <h1 style="margin: 0; color: #064e3b; font-size: 2.2rem; font-weight: 800;">{u.get('prenom')} {u.get('nom')}</h1>
                    <p style="margin: 0; color: #475569; font-weight: 500;">📍 Membre de la communauté AEEMG</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_info, col_feed = st.columns([1, 2], gap="large")

        with col_info:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #064e3b; margin-top:0;'>📋 Informations</h4>", unsafe_allow_html=True)
            est_a_jour = check_cotisation_du_mois(u.get("id"))
            statut_badge = "✅ À jour" if est_a_jour else "⚠️ Cotisation due"
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; gap: 12px;">
                    <div style="background: white; padding: 10px; border-radius: 10px;">
                        <small style="color: #64748b;">Email</small><br><b>{u.get('email')}</b>
                    </div>
                    <div style="background: white; padding: 10px; border-radius: 10px;">
                        <small style="color: #64748b;">Statut</small><br><b style="color: {'#10b981' if est_a_jour else '#ef4444'};">{statut_badge}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_feed:
            # Zone de Publication
            st.markdown("<div class='glass-card' style='padding: 20px;'>", unsafe_allow_html=True)
            with st.form("post_form", clear_on_submit=True):
                txt = st.text_area("", placeholder=f"Quoi de neuf, {u.get('prenom')} ?")
                media = st.file_uploader("📷 Photo ou Vidéo", type=['jpg','png','mp4'])
                if st.form_submit_button("Publier sur mon mur"):
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
            res_posts = supabase.table("posts").select("*").order("date_pub", desc=True).limit(15).execute()
            for post in res_posts.data:
                with st.container():
                    # Carte du Post
                    st.markdown(f"""
                    <div class="post-card">
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 15px;">
                            <img src="{post.get('auteur_photo') or 'https://www.w3schools.com/howto/img_avatar.png'}" 
                                 style="width:45px; height:45px; border-radius:50%; object-fit: cover; border: 2px solid #D4AF37;">
                            <div>
                                <b style="color: #064e3b; display: block;">{post.get('auteur_nom')}</b>
                                <small style="color: #94a3b8;">{post.get('date_pub')[:10]}</small>
                            </div>
                        </div>
                        <p style="color: #334155; font-size: 1.05rem;">{post.get('contenu')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Media
                    if post.get("media_url"):
                        if post.get("media_type") == "image": 
                            st.image(post["media_url"], use_container_width=True)
                        else: 
                            st.video(post["media_url"])
                    
                    # Barre Like / Comment
                    c1, c2, c3 = st.columns([1, 1, 2])
                    with c1:
                        if st.button(f"❤️ Like", key=f"like_{post['id']}"):
                            st.toast(f"Vous aimez le post de {post['auteur_nom']}")
                    with c2:
                        if st.button(f"💬 Commenter", key=f"comm_{post['id']}"):
                            st.info("Espace commentaire bientôt disponible !")
                    
                    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()

else:
    st.warning("Veuillez vous connecter.")
