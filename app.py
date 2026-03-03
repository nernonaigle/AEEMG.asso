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
# DESIGN / CSS HAUTE PERFORMANCE
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }

.main .block-container { max-width: 1000px !important; padding-top: 2rem; padding-bottom: 5rem; }

.stApp {
    background: linear-gradient(135deg, rgba(255,255,255,0.5), rgba(255,255,255,0.7)),
    url("https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}

.stTextInput input, .stTextArea textarea, [data-baseweb="select"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    font-weight: 700 !important;
    border: 2px solid #000000 !important;
    border-radius: 14px !important;
}

.comment-bubble {
    background-color: #f0f2f5;
    border-radius: 18px;
    padding: 10px 15px;
    margin: 5px 0 5px 50px;
    border: none;
}
.comment-author { font-weight: 800; color: #050505; font-size: 0.9rem; }
.comment-text { color: #050505; font-size: 0.95rem; }

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
        u = st.session_state.user_info
        st.write("---")
        menu = st.radio("Navigation", ["🏠 Tableau de Bord", "💳 Cotisations", "🪪 Carte de Membre", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# =========================================================
# LOGIQUE DES PAGES
# =========================================================
if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>CONNEXION</h2>", unsafe_allow_html=True)
    with st.container():
        email = st.text_input("EMAIL")
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
    st.markdown("<h1 class='gold-text' style='text-align:center;'>🤝 INSCRIPTION</h1>", unsafe_allow_html=True)
    with st.form("inscription"):
        c1, c2 = st.columns(2)
        nom = c1.text_input("NOM")
        prenom = c2.text_input("PRÉNOM")
        ville = c1.text_input("VILLE")
        organe = c2.selectbox("ORGANE", ["Bureau National", "Section Universitaire", "Section Scolaire", "Section Communale"])
        email_reg = st.text_input("EMAIL")
        pass_reg = st.text_input("MOT DE PASSE", type="password")
        if st.form_submit_button("🚀 ENVOYER"):
            data = {"nom": nom.upper(), "prenom": prenom.capitalize(), "email": email_reg.lower(), "password": hasher_password(pass_reg), "ville": ville, "organe_de_base": organe, "statut": "en_attente"}
            supabase.table("membres").insert(data).execute()
            st.success("✅ Inscrit ! Attendez l'approbation.")

elif st.session_state.connecte:
    u = st.session_state.user_info
    
    if menu == "🏠 Tableau de Bord":
        # HEADER SOCIAL (Utilisation de .get() pour éviter le KeyError)
        st.markdown(f"""
        <div style="position: relative; margin-bottom: 80px;">
            <div style="height: 180px; background: linear-gradient(90deg, #064e3b, #D4AF37); border-radius: 20px;"></div>
            <div style="position: absolute; bottom: -40px; left: 30px; display: flex; align-items: flex-end; gap: 20px;">
                <img src="https://www.w3schools.com/howto/img_avatar.png" style="width: 120px; height: 120px; border-radius: 50%; border: 5px solid white; background: white; object-fit: cover;">
                <div style="padding-bottom: 10px;">
                    <h1 style="margin: 0; color: #064e3b; font-size: 2rem; font-weight: 800;">{u.get('prenom', '')} {u.get('nom', '')}</h1>
                    <p style="margin: 0; font-weight: 800; color: #1e293b;">⭐ {u.get('organe_de_base', 'Membre AEEMG')}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 2], gap="large")

        with col_left:
            st.markdown(f"**Email:** {u.get('email', 'Non renseigné')}\n\n**Ville:** {u.get('ville', 'Non renseignée')}")

        with col_right:
            # ZONE PUBLICATION
            with st.form("post_form", clear_on_submit=True):
                txt = st.text_area("Quoi de neuf ?", placeholder=f"Exprimez-vous {u.get('prenom', '')}...")
                media = st.file_uploader("Média", type=['jpg','png','mp4'])
                if st.form_submit_button("🚀 PUBLIER"):
                    m_url, m_type = process_media(media)
                    supabase.table("posts").insert({"user_id": u['id'], "auteur_nom": f"{u['prenom']} {u['nom']}", "contenu": txt, "media_url": m_url, "media_type": m_type, "likes": 0, "date_pub": datetime.now().isoformat()}).execute()
                    st.rerun()

            # FLUX SOCIAL
            res_posts = supabase.table("posts").select("*").order("date_pub", desc=True).limit(10).execute()
            for post in res_posts.data:
                res_c = supabase.table("commentaires").select("*").eq("post_id", post['id']).order("created_at").execute()
                
                with st.container():
                    st.markdown(f"""
                    <div class="post-card">
                        <b>{post.get('auteur_nom', 'Anonyme')}</b> • <small>{post.get('date_pub', '')[:10]}</small>
                        <div style="font-size:1.15rem; font-weight:600; margin:15px 0;">{post.get('contenu', '')}</div>
                    """, unsafe_allow_html=True)
                    
                    if post.get("media_url"):
                        if post.get("media_type") == "image": st.image(post["media_url"])
                        else: st.video(post["media_url"])
                    
                    st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; color: #65676b; font-weight: 700; font-size: 0.9rem; margin-top: 10px;">
                            <span>❤️ {post.get('likes', 0)} J'aime</span>
                            <span>{len(res_c.data)} commentaires</span>
                        </div>
                        <hr style="margin:10px 0; opacity:0.1;">
                    """, unsafe_allow_html=True)

                    cl, cc = st.columns(2)
                    with cl:
                        if st.button(f"👍 Like", key=f"lk_{post['id']}", use_container_width=True):
                            supabase.table("posts").update({"likes": post.get('likes', 0) + 1}).eq("id", post['id']).execute()
                            st.rerun()
                    with cc:
                        show_c = st.toggle("💬 Commenter", key=f"tg_{post['id']}")

                    if show_c:
                        with st.form(f"f_c_{post['id']}", clear_on_submit=True):
                            c_in = st.text_input("Votre avis...")
                            if st.form_submit_button("Envoyer"):
                                supabase.table("commentaires").insert({"post_id": post['id'], "auteur_nom": u.get('prenom', 'Membre'), "contenu": c_in}).execute()
                                st.rerun()
                        
                        for c in res_c.data:
                            st.markdown(f"""<div class="comment-bubble"><b>{c.get('auteur_nom', 'Anonyme')}</b><br>{c.get('contenu', '')}</div>""", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()
