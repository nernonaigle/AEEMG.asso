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
# DESIGN / CSS HAUTE PERFORMANCE (DIMENSIONS & VISIBILITÉ)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

html, body, [class*="st-"] { 
    font-family: 'Plus Jakarta Sans', sans-serif; 
}

/* --- AJUSTEMENT LARGEUR ET LONGUEUR DU CONTENU --- */
.main .block-container { 
    max-width: 1000px !important; /* Réduit la largeur pour éviter l'étirement */
    padding-top: 2rem;
    padding-bottom: 5rem;
}

.stApp {
    background: linear-gradient(135deg, rgba(255,255,255,0.5), rgba(255,255,255,0.7)),
    url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

/* --- CHAMPS DE SAISIE (PLUS LONGS ET LISIBLES) --- */
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    border: 2px solid #000000 !important; /* Bordure noire pour un max de contraste */
    border-radius: 14px !important;
    padding: 15px !important; /* Augmente la "longueur" visuelle du champ */
}

div[data-baseweb="select"] > div {
    color: #000000 !important;
    font-weight: 700 !important;
}

label p { 
    font-weight: 800 !important; 
    color: #064e3b !important; 
    font-size: 1.1rem !important;
    margin-bottom: 10px !important;
}

/* --- CARTES ET POSTS --- */
.glass-card {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 24px;
    padding: 35px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
}

.post-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 25px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.post-text {
    color: #000000 !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    margin: 15px 0;
}

.gold-text {
    background: linear-gradient(90deg, #B8860B, #D4AF37);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

/* --- BOUTONS --- */
div.stButton > button {
    border-radius: 12px;
    background: #064e3b;
    color: white;
    font-weight: 800;
    font-size: 1.1rem;
    height: 3.5rem;
    border: none;
    width: 100%;
}

div.stButton > button:hover {
    background: #D4AF37;
}

/* --- SIDEBAR --- */
[data-testid="stSidebar"] { 
    background-color: #ffffff !important; 
    border-right: 2px solid #edf2f7; 
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span { 
    color: #000000 !important; 
    font-weight: 700 !important;
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
        st.write("---")
        menu = st.radio("Navigation", ["🏠 Tableau de Bord", "💳 Cotisations", "🪪 Carte de Membre", "📂 Documents", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# =========================================================
# PAGES
# =========================================================
if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>CONNEXION</h2>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        email = st.text_input("VOTRE EMAIL")
        password = st.text_input("MOT DE PASSE", type="password")
        if st.button("SE CONNECTER"):
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
    st.markdown("<h1 class='gold-text' style='text-align:center;'>🤝 REJOINDRE L'AEEMG</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("inscription"):
            c1, c2 = st.columns(2)
            nom = c1.text_input("NOM DE FAMILLE")
            prenom = c2.text_input("PRÉNOM")
            ville = c1.text_input("VILLE DE RÉSIDENCE")
            organe_de_base = c2.selectbox("ORGANE DE BASE", ["Bureau National", "Section Universitaire", "Section Scolaire", "Section Communale", "Antenne Régionale"], index=None)
            email = st.text_input("EMAIL")
            p1, p2 = st.columns(2)
            password = p1.text_input("MOT DE PASSE", type="password")
            confirm = p2.text_input("CONFIRMATION", type="password")
            motivation = st.text_area("MOTIVATION")
            
            # Plus de champ photo ici comme demandé 🙃
            
            if st.form_submit_button("🚀 ENVOYER LE DOSSIER"):
                if not all([nom, prenom, email, password, ville, organe_de_base]): st.error("⚠️ Remplissez tout !")
                elif password != confirm: st.error("❌ Mots de passe différents !")
                else:
                    data = {"nom": nom.upper(), "prenom": prenom.capitalize(), "email": email.lower(), "password": hasher_password(password), "ville": ville, "organe_de_base": organe_de_base, "motivation": motivation, "statut": "en_attente"}
                    supabase.table("membres").insert(data).execute()
                    st.success("✅ Dossier envoyé !")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.connecte:
    u = st.session_state.user_info
    
    if menu == "🏠 Tableau de Bord":
        # HEADER SOCIAL
        st.markdown(f"""
        <div style="position: relative; margin-bottom: 80px;">
            <div style="height: 180px; background: linear-gradient(90deg, #064e3b, #D4AF37); border-radius: 20px;"></div>
            <div style="position: absolute; bottom: -40px; left: 30px; display: flex; align-items: flex-end; gap: 20px;">
                <img src="{u.get('photo_url') or 'https://www.w3schools.com/howto/img_avatar.png'}" style="width: 120px; height: 120px; border-radius: 50%; border: 5px solid white; object-fit: cover; background: white;">
                <div style="padding-bottom: 10px;">
                    <h1 style="margin: 0; color: #064e3b; font-size: 2rem; font-weight: 800;">{u.get('prenom')} {u.get('nom')}</h1>
                    <p style="margin: 0; font-weight: 800; color: #1e293b;">⭐ {u.get('organe_de_base')}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 2], gap="large")

        with col_left:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### 📌 INFOS")
            st.markdown(f"**Email:** {u.get('email')}")
            st.markdown(f"**Ville:** {u.get('ville')}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            # ZONE DE PUBLICATION
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            with st.form("post_form", clear_on_submit=True):
                txt = st.text_area("EXPRIMEZ-VOUS...", placeholder=f"Quoi de neuf, {u.get('prenom')} ?")
                media = st.file_uploader("AJOUTER IMAGE/VIDÉO", type=['jpg','png','mp4'])
                if st.form_submit_button("🚀 PUBLIER"):
                    m_url, m_type = process_media(media)
                    new_post = {"user_id": u['id'], "auteur_nom": f"{u['prenom']} {u['nom']}", "auteur_photo": u.get("photo_url"), "contenu": txt, "media_url": m_url, "media_type": m_type, "date_pub": datetime.now().isoformat()}
                    supabase.table("posts").insert(new_post).execute()
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            # FILUX DE PUBLICATIONS AVEC LIKE/COMM
            res_posts = supabase.table("posts").select("*").order("date_pub", desc=True).limit(10).execute()
            for post in res_posts.data:
                with st.container():
                    st.markdown(f"""
                    <div class="post-card">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <img src="{post.get('auteur_photo') or 'https://www.w3schools.com/howto/img_avatar.png'}" style="width:50px; height:50px; border-radius:50%; object-fit: cover; border: 2px solid #D4AF37;">
                            <div>
                                <b style="font-size: 1.1rem; color: #064e3b;">{post.get('auteur_nom')}</b><br>
                                <small style="color: #64748b;">{post.get('date_pub')[:10]}</small>
                            </div>
                        </div>
                        <div class="post-text">{post.get('contenu')}</div>
                    """, unsafe_allow_html=True)
                    
                    if post.get("media_url"):
                        if post.get("media_type") == "image": st.image(post["media_url"], use_container_width=True)
                        else: st.video(post["media_url"])
                    
                    # --- RESTAURATION DES BOUTONS LIKE ET COMMENTAIRE ---
                    st.markdown("<hr style='margin: 15px 0; opacity: 0.2;'>", unsafe_allow_html=True)
                    c_lk, c_cm, c_void = st.columns([1, 1, 1.5])
                    with c_lk:
                        if st.button(f"❤️ J'aime", key=f"lk_{post['id']}"):
                            st.toast(f"Vous aimez le post de {post['auteur_nom']} !")
                    with c_cm:
                        if st.button(f"💬 Commenter", key=f"cm_{post['id']}"):
                            st.info("Espace commentaire bientôt disponible.")
                    st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()
