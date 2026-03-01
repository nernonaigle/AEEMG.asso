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

# --- FONCTIONS UTILES ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def process_media(file, is_profile=False):
    if file is None: return None, None
    file_type = file.type.split('/')[0]
    
    if file_type == 'image':
        img = Image.open(file)
        # Taille différente si c'est profil ou post
        size = (300, 300) if is_profile else (800, 800)
        img.thumbnail(size)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}", "image"
    else:
        return f"data:{file.type};base64,{base64.b64encode(file.read()).decode()}", "video"

# --- 🎨 DESIGN GLOBAL ---
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
    .profile-img { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 3px solid #D4AF37; margin-bottom: 10px; }
    .post-avatar { width: 45px; height: 45px; border-radius: 50%; border: 2px solid #D4AF37; margin-right: 12px; object-fit: cover; }
    .gold-text { color: #D4AF37; font-weight: 800; }
    .badge { padding: 4px 10px; border-radius: 15px; font-size: 0.75em; font-weight: bold; }
    .statut-en_attente { background: #f59e0b; }
    .statut-valide { background: #10b981; }
</style>
""", unsafe_allow_html=True)

# 3. Gestion de Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        u = st.session_state.user_info
        img_p = u.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f"<div style='text-align:center;'><img src='{img_p}' style='width:70px;height:70px;border-radius:50%;border:2px solid #D4AF37; object-fit: cover;'></div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:white;'><b>{u.get('prenom')}</b></p>", unsafe_allow_html=True)
        menu = st.radio("Menu", ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"])
        if u.get('email') == "nernonedouard99@gmail.com":
            st.info("🛠️ Mode Admin Activé")
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# --- CONTENU DES PAGES ---

if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>Accès Membre</h2>", unsafe_allow_html=True)
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        e_l = st.text_input("Email")
        p_l = st.text_input("Mot de passe", type="password")
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
    
    col_left, col_right = st.columns([1, 2.2])
    
    with col_left:
        # 1. Carte Profil & Photo
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        img_url = u.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f"<img src='{img_url}' class='profile-img'>", unsafe_allow_html=True)
        st.write(f"**{u['prenom']} {u['nom']}**")
        with st.expander("📸 Changer ma photo"):
            up_p = st.file_uploader("Galerie", type=['jpg', 'png'], key="prof_up")
            if up_p:
                b64, _ = process_media(up_p, is_profile=True)
                if st.button("Valider la photo"):
                    supabase.table("membres").update({"photo_url": b64}).eq("id", u['id']).execute()
                    st.session_state.user_info['photo_url'] = b64
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. Stats rapides
        st.markdown(f"""
        <div class="glass-card">
            <p style="margin:0; font-size:0.9em; color:#D4AF37;">Statut Cotisation</p>
            <h3 style="margin:0;">{'✅ À jour' if u['cotisation'] else '⚠️ À régler'}</h3>
            <hr style="opacity:0.1">
            <p style="margin:0; font-size:0.9em; color:#D4AF37;">Organe</p>
            <p style="margin:0;">{u['organe_base']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # 3. Zone de Publication
        st.markdown("### ✍️ Partager une actualité")
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            txt_msg = st.text_area("Exprimez-vous...", placeholder="Quoi de neuf dans la communauté ?", label_visibility="collapsed")
            media_file = st.file_uploader("Photo ou Vidéo", type=['jpg', 'png', 'mp4'])
            if st.button("🚀 Publier sur le fil"):
                if txt_msg or media_file:
                    m_url, m_type = process_media(media_file)
                    pub_data = {
                        "auteur_nom": f"{u['prenom']} {u['nom']}",
                        "auteur_photo": u.get('photo_url'),
                        "contenu_texte": txt_msg,
                        "media_url": m_url,
                        "media_type": m_type
                    }
                    supabase.table("publications").insert(pub_data).execute()
                    st.success("Message publié !")
                    time.sleep(0.5)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # 4. Fil d'actualité interactif
        st.markdown("### 📢 Fil d'Actualité")
        posts = supabase.table("publications").select("*").order("created_at", desc=True).limit(10).execute()
        for p in posts.data:
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; align-items:center; margin-bottom:12px;">
                    <img src="{p['auteur_photo'] or 'https://www.w3schools.com/howto/img_avatar.png'}" class="post-avatar">
                    <div><b>{p['auteur_nom']}</b><br><small style="color:#888;">{p['created_at'][:10]}</small></div>
                </div>
                <p style="font-size:1em;">{p['contenu_texte']}</p>
            </div>
            """, unsafe_allow_html=True)
            if p['media_url']:
                if p['media_type'] == "image": st.image(p['media_url'], use_container_width=True)
                else: st.video(p['media_url'])
            st.markdown("<br>", unsafe_allow_html=True)

elif menu == "💳 Cotisations":
    u = st.session_state.user_info
    st.markdown("<h1 class='gold-text'>💳 Espace Cotisations</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.markdown("### 📤 Déclarer un paiement")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("Frais annuels : **10.000 GNF**")
        with st.form("pay_form"):
            tid = st.text_input("Numéro de Transaction")
            preuve = st.file_uploader("Reçu (Photo)", type=['jpg', 'png'])
            if st.form_submit_button("Envoyer pour vérification"):
                if tid and preuve:
                    b64, _ = process_media(preuve)
                    data = {"user_id": u['id'], "user_nom": f"{u['prenom']} {u['nom']}", "transaction_id": tid, "preuve_image": b64, "statut": "en_attente"}
                    supabase.table("cotisations").insert(data).execute()
                    st.success("Enregistré ! En attente de validation admin.")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("### 📜 Historique")
        hist = supabase.table("cotisations").select("*").eq("user_id", u['id']).order("date_paiement", desc=True).execute()
        for h in hist.data:
            st.markdown(f'<div class="glass-card">📅 {h["date_paiement"][:10]} | ID: {h["transaction_id"]} <br>Statut: <span class="badge statut-{h["statut"]}">{h["statut"]}</span></div>', unsafe_allow_html=True)

elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()

# --- AUTRES PAGES (STUBS) ---
elif menu == "📂 Documents": st.markdown("<h1 class='gold-text'>📂 Bibliothèque</h1>")
elif menu == "📸 Galerie": st.markdown("<h1 class='gold-text'>📸 Galerie</h1>")
