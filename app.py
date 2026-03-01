import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime, date
import calendar
import time
import base64
from io import BytesIO
from PIL import Image

# 1. CONFIGURATION PAGE
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

# 2. CONNEXION SUPABASE
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- FONCTIONS LOGIQUES ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_cotisation_du_mois(user_id):
    today = date.today()
    first_day = today.replace(day=1).isoformat()
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1]).isoformat()
    res = supabase.table("cotisations").select("*").eq("user_id", user_id).eq("statut", "valide").gte("date_paiement", first_day).lte("date_paiement", last_day).execute()
    return len(res.data) > 0

def process_media(file, is_profile=False):
    if file is None: return None, None
    file_type = file.type.split('/')[0]
    if file_type == 'image':
        img = Image.open(file)
        size = (300, 300) if is_profile else (800, 800)
        img.thumbnail(size)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}", "image"
    else:
        return f"data:{file.type};base64,{base64.b64encode(file.read()).decode()}", "video"

# --- 🎨 DESIGN CSS ---
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
    .profile-img { width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 3px solid #D4AF37; margin-bottom: 10px; }
    .gold-text { color: #D4AF37; font-weight: 800; }
    .badge-paye { background: #10b981; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em; }
    .badge-impaye { background: #ef4444; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em; }
    .stButton>button { border-radius: 12px !important; background: linear-gradient(135deg, #065f46 0%, #047857 100%) !important; color: white !important; border: 1px solid rgba(212, 175, 55, 0.5) !important; }
</style>
""", unsafe_allow_html=True)

# 3. GESTION DE SESSION
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        u = st.session_state.user_info
        est_a_jour = check_cotisation_du_mois(u['id'])
        img_p = u.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f"<div style='text-align:center;'><img src='{img_p}' style='width:75px;height:75px;border-radius:50%;border:2px solid #D4AF37; object-fit: cover;'></div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:white; margin-bottom:5px;'><b>{u['prenom']}</b></p>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;'>{'<span class=\"badge-paye\">✅ À JOUR</span>' if est_a_jour else '<span class=\"badge-impaye\">⚠️ À RÉGLER</span>'}</div>", unsafe_allow_html=True)
        menu = st.radio("Menu Principal", ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# --- PAGES ---

if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>Connexion Membre</h2>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.5, 1])
    with c:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        e_l = st.text_input("Email")
        p_l = st.text_input("Mot de passe", type="password")
        if st.button("Entrer dans l'espace"):
            res = supabase.table("membres").select("*").eq("email", e_l).eq("password", hasher_password(p_l)).execute()
            if res.data:
                user = res.data[0]
                if user.get('statut') == "approuve":
                    st.session_state.connecte, st.session_state.user_info = True, user
                    st.rerun()
                else: st.warning("⏳ Compte en attente de validation.")
            else: st.error("Identifiants incorrects.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏠 Tableau de Bord" and st.session_state.connecte:
    u = st.session_state.user_info
    est_a_jour = check_cotisation_du_mois(u['id'])
    st.markdown(f"<h1 class='gold-text'>👋 Salam, {u['prenom']} !</h1>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns([1, 2.2])
    with col_l:
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown(f"<img src='{u.get('photo_url') or 'https://www.w3schools.com/howto/img_avatar.png'}' class='profile-img'>", unsafe_allow_html=True)
        st.write(f"**{u['prenom']} {u['nom']}**")
        with st.expander("📸 Modifier photo"):
            up = st.file_uploader("Galerie", type=['jpg', 'png'], key="prof_up")
            if up:
                b64, _ = process_media(up, True)
                if st.button("Sauvegarder"):
                    supabase.table("membres").update({"photo_url": b64}).eq("id", u['id']).execute()
                    st.session_state.user_info['photo_url'] = b64
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="glass-card"><small style="color:#D4AF37;">Organe :</small><br>{u["organe_base"]}<hr style="opacity:0.1"><small style="color:#D4AF37;">ID :</small><br>#AE-{u["id"]}</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        txt = st.text_area("Quoi de neuf ?", placeholder="Partagez un message...", label_visibility="collapsed")
        med = st.file_uploader("Ajouter Photo/Vidéo", type=['jpg','png','mp4'])
        if st.button("🚀 Publier"):
            if txt or med:
                m_url, m_type = process_media(med)
                supabase.table("publications").insert({"auteur_nom": f"{u['prenom']} {u['nom']}", "auteur_photo": u.get('photo_url'), "contenu_texte": txt, "media_url": m_url, "media_type": m_type}).execute()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        posts = supabase.table("publications").select("*").order("created_at", desc=True).limit(5).execute()
        for p in posts.data:
            st.markdown(f'<div class="glass-card"><b>{p["auteur_nom"]}</b> • <small>{p["created_at"][:10]}</small><br><br>{p["contenu_texte"]}</div>', unsafe_
