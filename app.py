import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime
import time

# 1. Configuration de la page
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

# 2. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- FONCTIONS DE SÉCURITÉ ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 🎨 DESIGN MODERNISÉ ---
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
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        margin-bottom: 20px;
    }
    .profile-img {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #D4AF37;
        margin-bottom: 10px;
    }
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(135deg, #065f46 0%, #047857 100%) !important;
        color: white !important;
        border: 1px solid rgba(212, 175, 55, 0.5) !important;
        transition: 0.3s;
    }
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
        # Photo dans la sidebar
        img_url = st.session_state.user_info.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f"<div style='text-align:center;'><img src='{img_url}' style='width:70px;height:70px;border-radius:50%;border:2px solid #D4AF37;'></div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:white;'><b>{st.session_state.user_info.get('prenom')}</b></p>", unsafe_allow_html=True)
        
        options = ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"]
        if st.session_state.user_info.get('email') == "nernonedouard99@gmail.com":
            options.insert(4, "🛠️ Admin")
        menu = st.radio("Menu Principal", options)

# --- PAGES ---

if menu == "📝 Inscription":
    st.markdown("<h1 class='gold-text'>✨ Inscription AEEMG</h1>", unsafe_allow_html=True)
    with st.form("reg_form"):
        c1, c2 = st.columns(2)
        nom, prenom = c1.text_input("Nom"), c2.text_input("Prénom")
        email, pwd = c1.text_input("Email"), c2.text_input("Mot de passe", type="password")
        ville, organe = c1.text_input("Ville"), c2.selectbox("Organe", ["Bureau National", "Section Universitaire", "Antenne Régionale"])
        motivation = st.text_area("Motivation")
        if st.form_submit_button("Envoyer ma demande"):
            if email and pwd:
                data = {"nom": nom, "prenom": prenom, "email": email, "password": hasher_password(pwd), "ville": ville, "organe_base": organe, "motivation": motivation, "statut": "en_attente"}
                try:
                    supabase.table("membres").insert(data).execute()
                    st.success("Demande envoyée !")
                except: st.error("Email déjà utilisé.")

elif menu == "🔑 Connexion":
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
    
    col_p, col_i = st.columns([1, 2])
    
    with col_p:
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        img_url = u.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f"<img src='{img_url}' class='profile-img'>", unsafe_allow_html=True)
        st.write(f"**{u['prenom']} {u['nom']}**")
        
        # Modifier la photo
        with st.expander("Modifier ma photo"):
            new_url = st.text_input("Lien URL de l'image (JPG/PNG)", value=img_url)
            if st.button("Enregistrer la photo"):
                supabase.table("membres").update({"photo_url": new_url}).eq("id", u['id']).execute()
                st.session_state.user_info['photo_url'] = new_url
                st.success("Photo mise à jour !")
                time.sleep(1)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_i:
        st.markdown("### 📢 Fil d'Actualités")
        st.markdown(f"""<div class="glass-card" style="padding: 15px; border-left: 5px solid #D4AF37;">
            <small style="color: #888;">Mars 2026</small>
            <h4 style="margin: 5px 0;">🌙 Bienvenue sur votre portail</h4>
            <p style="font-size: 0.9em;">N'oubliez pas de mettre à jour votre profil !</p>
        </div>""", unsafe_allow_html=True)

    # Stats en bas
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="glass-card">Statut: ✨ Actif<br>ID: #00{u["id"]}</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="glass-card">Cotisation: {"✅ À jour" if u["cotisation"] else "⚠️ À régler"}</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="glass-card">Organe:<br>{u["organe_base"]}</div>', unsafe_allow_html=True)

# (Reste du code : Cotisations, Documents, Galerie, Admin, Déconnexion inchangés)
elif menu == "💳 Cotisations":
    st.markdown("<h1 class='gold-text'>💳 Ma Cotisation</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">Le montant est de 10.000 GNF.</div>', unsafe_allow_html=True)
elif menu == "📂 Documents":
    st.markdown("<h1 class='gold-text'>📂 Bibliothèque</h1>", unsafe_allow_html=True)
elif menu == "📸 Galerie":
    st.markdown("<h1 class='gold-text'>📸 Galerie Photos</h1>", unsafe_allow_html=True)
elif menu == "🛠️ Admin":
    if st.session_state.user_info.get('email') == "nernonedouard99@gmail.com":
        st.markdown("<h1 class='gold-text'>🛠️ Admin</h1>", unsafe_allow_html=True)
        res = supabase.table("membres").select("*").eq("statut", "en_attente").execute()
        for m in res.data:
            with st.expander(f"{m['prenom']} {m['nom']}"):
                if st.button("Approuver", key=m['id']):
                    supabase.table("membres").update({"statut": "approuve"}).eq("id", m['id']).execute()
                    st.rerun()
elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()
