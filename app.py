import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime, date
import calendar
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

# --- FONCTIONS LOGIQUES ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_cotisation_du_mois(user_id):
    today = date.today()
    first_day = today.replace(day=1).isoformat()
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1]).isoformat()
    try:
        res = supabase.table("cotisations").select("*").eq("user_id", user_id).eq("statut", "valide").gte("date_paiement", first_day).lte("date_paiement", last_day).execute()
        return len(res.data) > 0
    except:
        return False

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
    .profile-img { width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 3px solid #D4AF37; margin-bottom: 10px; }
    .gold-text { color: #D4AF37; font-weight: 800; }
    .badge-paye { background: #10b981; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em; }
    .badge-impaye { background: #ef4444; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em; }
</style>
""", unsafe_allow_html=True)

# 3. Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        u = st.session_state.user_info
        est_a_jour = check_cotisation_du_mois(u['id'])
        img_p = u.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f"<div style='text-align:center;'><img src='{img_p}' style='width:70px;height:70px;border-radius:50%;border:2px solid #D4AF37; object-fit: cover;'></div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:white; margin-bottom:0;'><b>{u['prenom']}</b></p>", unsafe_allow_html=True)
        status_html = "<span class='badge-paye'>✅ À JOUR</span>" if est_a_jour else "<span class='badge-impaye'>⚠️ À RÉGLER</span>"
        st.markdown(f"<div style='text-align:center;'>{status_html}</div>", unsafe_allow_html=True)
        menu = st.radio("Menu", ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# --- PAGES ---

if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>Connexion</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", email).eq("password", hasher_password(password)).execute()
            if res.data:
                user = res.data[0]
                if user.get('statut') == "approuve":
                    st.session_state.connecte = True
                    st.session_state.user_info = user
                    st.rerun()
                else:
                    st.warning("⏳ Votre compte est en attente de validation par un admin.")
            else:
                st.error("Identifiants incorrects.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📝 Inscription":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>Créer un compte</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("inscription_form"):
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            organe = st.selectbox("Organe de base", ["Bureau National", "Section Universitaire", "Antenne Régionale"])
            if st.form_submit_button("Envoyer ma demande"):
                if nom and prenom and email and password:
                    data = {"nom": nom, "prenom": prenom, "email": email, "password": hasher_password(password), "organe_base": organe, "statut": "en_attente"}
                    supabase.table("membres").insert(data).execute()
                    st.success("✅ Demande envoyée ! Attendez la validation d'un administrateur.")
                else:
                    st.error("Veuillez remplir tous les champs.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏠 Tableau de Bord" and st.session_state.connecte:
    u = st.session_state.user_info
    est_a_jour = check_cotisation_du_mois(u['id'])
    st.markdown(f"<h1 class='gold-text'>👋 Salam, {u['prenom']} !</h1>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 2.2])
    with col_left:
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown(f"<img src='{u.get('photo_url') or 'https://www.w3schools.com/howto/img_avatar.png'}' class='profile-img'>", unsafe_allow_html=True)
        st.write(f"**{u['prenom']} {u['nom']}**")
        st.markdown(f"Statut {datetime.now().strftime('%B')}: {'<b style=\"color:#10b981\">Payé</b>' if est_a_jour else '<b style=\"color:#ef4444\">Non payé</b>'}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="glass-card"><small style="color:#D4AF37;">Organe de base</small><br><b>{u['organe_base']}</b><hr style="opacity:0.1"><small style="color:#D4AF37;">ID Membre</small><br><b>#AE-{u['id']}</b></div>""", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        txt = st.text_area("Quoi de neuf ?", placeholder="Partagez une info...", label_visibility="collapsed")
        media = st.file_uploader("Image/Vidéo", type=['jpg','png','mp4'], key="post_file")
        if st.button("🚀 Publier"):
            if txt or media:
                m_url, m_type = process_media(media)
                supabase.table("publications").insert({"auteur_nom": f"{u['prenom']} {u['nom']}", "auteur_photo": u.get('photo_url'), "contenu_texte": txt, "media_url": m_url, "media_type": m_type}).execute()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        posts = supabase.table("publications").select("*").order("created_at", desc=True).limit(5).execute()
        for p in posts.data:
            st.markdown(f"""<div class="glass-card"><img src="{p['auteur_photo'] or 'https://www.w3schools.com/howto/img_avatar.png'}" style="width:35px;height:35px;border-radius:50%; vertical-align:middle; margin-right:10px;"><b>{p['auteur_nom']}</b> <small style="color:#888;">• {p['created_at'][:10]}</small><br><br>{p['contenu_texte']}</div>""", unsafe_allow_html=True)
            if p['media_url']:
                if p['media_type']=="image": st.image(p['media_url'])
                else: st.video(p['media_url'])

elif menu == "💳 Cotisations" and st.session_state.connecte:
    u = st.session_state.user_info
    st.markdown(f"<h1 class='gold-text'>💳 Cotisation de {datetime.now().strftime('%B %Y')}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("Montant : **10.000 GNF**")
        with st.form("pay"):
            tid = st.text_input("ID Transaction")
            file = st.file_uploader("Capture reçu", type=['jpg','png'])
            if st.form_submit_button("Déclarer le paiement"):
                if tid and file:
                    b64, _ = process_media(file, True)
                    supabase.table("cotisations").insert({"user_id": u['id'], "user_nom": u['prenom'], "transaction_id": tid, "preuve_image": b64, "statut": "en_attente"}).execute()
                    st.success("Reçu envoyé !")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("### Historique")
        hist = supabase.table("cotisations").select("*").eq("user_id", u['id']).order("date_paiement", desc=True).execute()
        for h in hist.data:
            st.write(f"📅 {h['date_paiement'][:10]} - {h['statut'].upper()}")

elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()
