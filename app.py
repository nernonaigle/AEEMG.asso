import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime
import time
import base64
from io import BytesIO
from PIL import Image

# 1. Configuration de la page
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

# 2. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- FONCTIONS DE SÉCURITÉ & MÉDIA ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def process_media(file):
    if file is None: return None, None
    file_type = file.type.split('/')[0] # 'image' ou 'video'
    
    if file_type == 'image':
        img = Image.open(file)
        img.thumbnail((800, 800)) # Optimisation
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}", "image"
    else:
        # Pour la vidéo, on la garde telle quelle en base64 (Attention à la taille < 50MB)
        return f"data:{file.type};base64,{base64.b64encode(file.read()).decode()}", "video"

# --- 🎨 DESIGN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp {
        background: linear-gradient(135deg, rgba(2, 44, 34, 0.95) 0%, rgba(1, 20, 15, 0.98) 100%),
        url("https://images.unsplash.com/photo-1564115484-a4aaa88d5449?q=80&w=2000") no-repeat center center fixed;
        background-size: cover !important;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        margin-bottom: 15px;
    }
    .post-header { display: flex; align-items: center; margin-bottom: 10px; }
    .post-avatar { width: 40px; height: 40px; border-radius: 50%; border: 2px solid #D4AF37; margin-right: 10px; object-fit: cover; }
    .profile-img { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 3px solid #D4AF37; margin-bottom: 10px; }
    .gold-text { color: #D4AF37; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

# 3. Gestion de Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if not st.session_state.connecte:
        menu = st.radio("Navigation", ["🔑 Connexion", "📝 Inscription"])
    else:
        img_url = st.session_state.user_info.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f"<div style='text-align:center;'><img src='{img_url}' style='width:70px;height:70px;border-radius:50%;border:2px solid #D4AF37; object-fit: cover;'></div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:white;'><b>{st.session_state.user_info.get('prenom')}</b></p>", unsafe_allow_html=True)
        options = ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"]
        if st.session_state.user_info.get('email') == "nernonedouard99@gmail.com":
            options.insert(4, "🛠️ Admin")
        menu = st.radio("Menu Principal", options)

# --- CONTENU ---

if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>Accès Membre</h2>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        e_l, p_l = st.text_input("Email"), st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", e_l).eq("password", hasher_password(p_l)).execute()
            if res.data:
                user = res.data[0]
                if user.get('statut') == "approuve":
                    st.session_state.connecte, st.session_state.user_info = True, user
                    st.rerun()
                else: st.warning("⏳ Compte en attente de validation.")
            else: st.error("Identifiants incorrects.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏠 Tableau de Bord":
    u = st.session_state.user_info
    st.markdown(f"<h1 class='gold-text'>👋 Salam, {u['prenom']} !</h1>", unsafe_allow_html=True)
    
    col_p, col_i = st.columns([1, 2.5])
    
    with col_p:
        # --- PROFIL ---
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        img_p = u.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f"<img src='{img_p}' class='profile-img'>", unsafe_allow_html=True)
        st.write(f"**{u['prenom']} {u['nom']}**")
        with st.expander("📸 Changer ma photo"):
            up_p = st.file_uploader("Nouvelle photo", type=['jpg', 'png'], key="prof")
            if up_p:
                b64, _ = process_media(up_p)
                if st.button("Confirmer photo"):
                    supabase.table("membres").update({"photo_url": b64}).eq("id", u['id']).execute()
                    st.session_state.user_info['photo_url'] = b64
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_i:
        # --- ZONE DE PUBLICATION ---
        st.markdown("### ✍️ Partager avec l'AEEMG")
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            txt_pub = st.text_area("Quoi de neuf ?", placeholder="Écrivez votre message ici...", label_visibility="collapsed")
            media_pub = st.file_uploader("Ajouter une photo ou vidéo", type=['jpg', 'png', 'mp4', 'mov'])
            if st.button("🚀 Publier"):
                if txt_pub or media_pub:
                    m_url, m_type = process_media(media_pub)
                    pub_data = {
                        "auteur_nom": f"{u['prenom']} {u['nom']}",
                        "auteur_photo": u.get('photo_url'),
                        "contenu_texte": txt_pub,
                        "media_url": m_url,
                        "media_type": m_type
                    }
                    supabase.table("publications").insert(pub_data).execute()
                    st.success("Publié !")
                    time.sleep(1)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # --- FIL D'ACTUALITÉ ---
        st.markdown("### 📢 Actualités de la communauté")
        posts = supabase.table("publications").select("*").order("created_at", desc=True).limit(10).execute()
        
        for p in posts.data:
            with st.container():
                st.markdown(f"""
                <div class="glass-card">
                    <div class="post-header">
                        <img src="{p['auteur_photo'] or 'https://www.w3schools.com/howto/img_avatar.png'}" class="post-avatar">
                        <div><b>{p['auteur_nom']}</b><br><small style="color:#888;">{p['created_at'][:10]}</small></div>
                    </div>
                    <p>{p['contenu_texte']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Affichage du média s'il existe
                if p['media_url']:
                    if p['media_type'] == "image":
                        st.image(p['media_url'], use_container_width=True)
                    elif p['media_type'] == "video":
                        st.video(p['media_url'])
                st.markdown("<br>", unsafe_allow_html=True)

elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()

# Note: Pour garder le code court, j'ai omis les autres menus (Inscription, Cotisation, etc.) 
# mais ils restent identiques à ta version précédente.
