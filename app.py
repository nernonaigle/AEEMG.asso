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
# DESIGN / CSS HAUTE VISIBILITÉ (STYLE FACEBOOK)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; color: #000000; }

.main .block-container { max-width: 1000px !important; padding-top: 2rem; }

/* SIDEBAR CLAIRE */
[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 2px solid #f1f5f9; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span { color: #000000 !important; font-weight: 700 !important; }

/* CHAMPS SAISIE NOIR SUR BLANC */
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    font-weight: 700 !important;
    border: 2px solid #000000 !important;
    border-radius: 12px !important;
}

/* BULLES COMMENTAIRES STYLE FB */
.comment-bubble {
    background-color: #f0f2f5;
    border-radius: 18px;
    padding: 12px 16px;
    margin: 8px 0 8px 50px;
    border: none;
}
.comment-author { font-weight: 800; color: #050505; font-size: 0.95rem; }
.comment-text { color: #050505; font-size: 1rem; line-height: 1.4; }

.post-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 25px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.gold-text {
    background: linear-gradient(90deg, #B8860B, #D4AF37);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
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
        menu = st.radio("Menu", ["🏠 Fil d'actualité", "💳 Cotisations", "🪪 Carte", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# =========================================================
# LOGIQUE DES PAGES
# =========================================================
if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>CONNEXION</h2>", unsafe_allow_html=True)
    with st.container():
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

elif menu == "📝 Inscription":
    st.markdown("<h1 class='gold-text' style='text-align:center;'>INSCRIPTION</h1>", unsafe_allow_html=True)
    with st.form("inscription_form"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("NOM")
        prenom = c2.text_input("PRÉNOM")
        ville = c1.text_input("VILLE")
        organe = c2.selectbox("ORGANE", ["Bureau National", "Section Universitaire", "Section Scolaire", "Section Communale", "Antenne Régionale"])
        email_reg = st.text_input("EMAIL")
        pass_reg = st.text_input("MOT DE PASSE", type="password")
        if st.form_submit_button("S'INSCRIRE"):
            if not all([nom, prenom, email_reg, pass_reg]): st.error("Champs obligatoires")
            else:
                data = {"nom": nom.upper(), "prenom": prenom.capitalize(), "email": email_reg.lower(), "password": hasher_password(pass_reg), "ville": ville, "organe_de_base": organe, "statut": "en_attente"}
                supabase.table("membres").insert(data).execute()
                st.success("Inscription envoyée ! Attendez l'approbation de l'admin.")

elif st.session_state.connecte:
    u = st.session_state.user_info

    if menu == "🏠 Fil d'actualité":
        # HEADER
        st.markdown(f"<h2 class='gold-text'>Bienvenue, {u['prenom']} !</h2>", unsafe_allow_html=True)
        
        # ZONE DE PUBLICATION
        with st.expander("📝 Publier quelque chose sur le mur"):
            with st.form("post_form", clear_on_submit=True):
                txt = st.text_area("Quoi de neuf ?", placeholder="Exprimez-vous...")
                media = st.file_uploader("Image/Vidéo", type=['jpg','png','mp4'])
                if st.form_submit_button("PUBLIER"):
                    m_url, m_type = process_media(media)
                    new_post = {"user_id": u['id'], "auteur_nom": f"{u['prenom']} {u['nom']}", "contenu": txt, "media_url": m_url, "media_type": m_type, "date_pub": datetime.now().isoformat()}
                    supabase.table("posts").insert(new_post).execute()
                    st.rerun()

        # FLUX DES POSTS
        res_posts = supabase.table("posts").select("*").order("date_pub", desc=True).limit(10).execute()
        for post in res_posts.data:
            # Récupérer comms
            res_c = supabase.table("commentaires").select("*").eq("post_id", post['id']).order("created_at").execute()
            
            st.markdown(f"""
            <div class="post-card">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom:15px;">
                    <img src="https://www.w3schools.com/howto/img_avatar.png" style="width:45px; height:45px; border-radius:50%;">
                    <div><b>{post['auteur_nom']}</b><br><small>{post['date_pub'][:10]}</small></div>
                </div>
                <p style="font-size:1.1rem; font-weight:600; color:#000;">{post['contenu']}</p>
            """, unsafe_allow_html=True)
            
            if post.get("media_url"):
                if post.get("media_type") == "image": st.image(post["media_url"])
                else: st.video(post["media_url"])

            st.markdown(f"<div style='color:#65676b; font-weight:700; margin-top:10px;'>❤️ {post.get('likes', 0)} J'aime • 💬 {len(res_c.data)} commentaires</div>", unsafe_allow_html=True)
            
            # ACTIONS
            col_l, col_c = st.columns([1, 1])
            with col_l:
                if st.button(f"👍 J'aime", key=f"lk_{post['id']}"): st.toast("C'est noté !")
            with col_c:
                show_input = st.toggle("💬 Commenter", key=f"tg_{post['id']}")

            if show_input:
                with st.form(f"f_c_{post['id']}", clear_on_submit=True):
                    c_txt = st.text_input("Écrire un commentaire...", key=f"i_{post['id']}")
                    if st.form_submit_button("Envoyer"):
                        supabase.table("commentaires").insert({"post_id": post['id'], "auteur_nom": u['prenom'], "contenu": c_txt}).execute()
                        st.rerun()

            # AFFICHAGE DES BULLES DE COMM
            for c in res_c.data:
                st.markdown(f"""
                <div class="comment-bubble">
                    <div class="comment-author">{c['auteur_nom']}</div>
                    <div class="comment-text">{c['contenu']}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()
