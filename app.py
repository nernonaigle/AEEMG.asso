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
# DESIGN / CSS MODERN LIGHT GLASS (CORRIGÉ LISIBILITÉ)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="st-"] { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
    color: #0f172a; /* Texte plus sombre pour contraste */
}

.stApp {
    background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.4)),
    url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

/* --- AMÉLIORATION DES SAISIES ET ÉCRITURES --- */
.stTextInput input, .stTextArea textarea {
    background-color: rgba(255, 255, 255, 0.98) !important; /* Fond bien blanc */
    color: #0f172a !important;
    font-weight: 600 !important; /* Écriture plus grasse */
    font-size: 1rem !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: 14px !important;
}

label p {
    font-weight: 800 !important; /* Titres de champs plus épais */
    color: #064e3b !important;
    font-size: 1.05rem !important;
}

/* Sidebar plus lisible */
[data-testid="stSidebar"] {
    background-color: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(20px);
}

.glass-card {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(25px);
    border-radius: 24px;
    padding: 25px;
    border: 1px solid rgba(255,255,255,0.9);
    box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}

.post-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 22px;
    padding: 25px;
    border-left: 7px solid #D4AF37;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    margin-bottom: 10px;
}

.post-card p {
    font-weight: 500 !important; /* Texte des posts plus épais */
    font-size: 1.1rem !important;
    color: #1e293b;
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
    font-weight: 700;
    padding: 0.6rem 2.5rem;
}
div.stButton > button:hover {
    background: #D4AF37;
    transform: translateY(-2px);
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
        <div style="position: relative; margin-bottom: 90px;">
            <div style="height: 190px; background: linear-gradient(90deg, #064e3b, #D4AF37); border-radius: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.15);"></div>
            <div style="position: absolute; bottom: -55px; left: 40px; display: flex; align-items: flex-end; gap: 20px;">
                <img src="{u.get('photo_url') or 'https://www.w3schools.com/howto/img_avatar.png'}" 
                     style="width: 130px; height: 130px; border-radius: 50%; border: 5px solid rgba(255,255,255,1); object-fit: cover; box-shadow: 0 8px 15px rgba(0,0,0,0.2); background: white;">
                <div style="padding-bottom: 12px;">
                    <h1 style="margin: 0; color: #064e3b; font-size: 2.3rem; font-weight: 800;">{u.get('prenom')} {u.get('nom')}</h1>
                    <p style="margin: 0; color: #334155; font-weight: 700; font-size: 1.1rem;">💎 Membre Actif AEEMG</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_info, col_feed = st.columns([1, 2], gap="large")

        with col_info:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #064e3b; margin-top:0;'>📌 À propos</h3>", unsafe_allow_html=True)
            est_a_jour = check_cotisation_du_mois(u.get("id"))
            statut_badge = "✅ Membre en règle" if est_a_jour else "⚠️ Cotisation en attente"
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; gap: 15px;">
                    <div style="background: rgba(255,255,255,0.8); padding: 12px; border-radius: 12px; border: 1px solid #e2e8f0;">
                        <small style="color: #64748b; font-weight: 600;">Contact</small><br><b>{u.get('email')}</b>
                    </div>
                    <div style="background: rgba(255,255,255,0.8); padding: 12px; border-radius: 12px; border: 1px solid #e2e8f0;">
                        <small style="color: #64748b; font-weight: 600;">État Financier</small><br><b style="color: {'#10b981' if est_a_jour else '#ef4444'};">{statut_badge}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_feed:
            # Zone de Publication
            st.markdown("<div class='glass-card' style='padding: 25px;'>", unsafe_allow_html=True)
            with st.form("post_form", clear_on_submit=True):
                txt = st.text_area("Exprimez-vous", placeholder=f"Quoi de neuf, {u.get('prenom')} ?")
                media = st.file_uploader("Ajouter un média", type=['jpg','png','mp4'])
                if st.form_submit_button("🚀 Publier sur mon mur"):
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
                    st.markdown(f"""
                    <div class="post-card">
                        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                            <img src="{post.get('auteur_photo') or 'https://www.w3schools.com/howto/img_avatar.png'}" 
                                 style="width:50px; height:50px; border-radius:50%; object-fit: cover; border: 2.5px solid #D4AF37;">
                            <div>
                                <b style="color: #064e3b; display: block; font-size: 1.1rem;">{post.get('auteur_nom')}</b>
                                <small style="color: #64748b; font-weight: 500;">{post.get('date_pub')[:10]}</small>
                            </div>
                        </div>
                        <p>{post.get('contenu')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if post.get("media_url"):
                        if post.get("media_type") == "image": st.image(post["media_url"], use_container_width=True)
                        else: st.video(post["media_url"])
                    
                    # Boutons d'interaction
                    c1, c2, c3 = st.columns([1, 1, 2])
                    with c1:
                        if st.button(f"❤️ Like", key=f"like_{post['id']}"):
                            st.toast(f"Coup de cœur sur le post de {post['auteur_nom']} !")
                    with c2:
                        if st.button(f"💬 Commenter", key=f"comm_{post['id']}"):
                            st.info("La zone de commentaires est en cours de développement.")
                    
                    st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()

else:
    st.warning("Veuillez vous connecter pour accéder à votre espace.")
