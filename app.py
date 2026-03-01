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

def image_to_base64(uploaded_file):
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        img.thumbnail((600, 600))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"
    return None

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
    .gold-text { color: #D4AF37; font-weight: 800; }
    .badge { padding: 5px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
    .statut-en_attente { background: #f59e0b; color: white; }
    .statut-valide { background: #10b981; color: white; }
    .statut-rejete { background: #ef4444; color: white; }
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
        img_p = u.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f"<div style='text-align:center;'><img src='{img_p}' style='width:70px;height:70px;border-radius:50%;border:2px solid #D4AF37; object-fit: cover;'></div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:white;'><b>{u.get('prenom')}</b></p>", unsafe_allow_html=True)
        menu = st.radio("Menu", ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# --- PAGES ---

if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>Connexion</h2>", unsafe_allow_html=True)
    with st.container():
        _, c, _ = st.columns([1,1.5,1])
        with c:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            e = st.text_input("Email")
            p = st.text_input("Pass", type="password")
            if st.button("Entrer"):
                res = supabase.table("membres").select("*").eq("email", e).eq("password", hasher_password(p)).execute()
                if res.data:
                    st.session_state.connecte, st.session_state.user_info = True, res.data[0]
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "💳 Cotisations":
    u = st.session_state.user_info
    st.markdown("<h1 class='gold-text'>💳 Gestion des Cotisations</h1>", unsafe_allow_html=True)
    
    col_form, col_hist = st.columns([1, 1.2])
    
    with col_form:
        st.markdown("### 📤 Déclarer un paiement")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("Montant annuel : **10.000 GNF**")
        st.info("Paiement via Orange Money au : **+224 62X XX XX XX**")
        
        with st.form("form_cotis", clear_on_submit=True):
            tid = st.text_input("ID de transaction (ex: PP2403...)")
            preuve = st.file_uploader("Capture d'écran du reçu", type=['jpg', 'png'])
            submit = st.form_submit_button("Envoyer pour validation")
            
            if submit:
                if tid and preuve:
                    img_b64 = image_to_base64(preuve)
                    cotis_data = {
                        "user_id": u['id'],
                        "user_nom": f"{u['prenom']} {u['nom']}",
                        "transaction_id": tid,
                        "preuve_image": img_b64,
                        "statut": "en_attente"
                    }
                    supabase.table("cotisations").insert(cotis_data).execute()
                    st.success("Déclaration envoyée ! L'administrateur vérifiera sous peu.")
                else:
                    st.error("Veuillez remplir tous les champs.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_hist:
        st.markdown("### 📜 Mon historique")
        hist = supabase.table("cotisations").select("*").eq("user_id", u['id']).order("date_paiement", desc=True).execute()
        
        if not hist.data:
            st.info("Aucun paiement déclaré pour le moment.")
        else:
            for c in hist.data:
                st.markdown(f"""
                <div class="glass-card" style="padding:15px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span>🗓️ {c['date_paiement'][:10]}</span>
                        <span class="badge statut-{c['statut']}">{c['statut'].upper()}</span>
                    </div>
                    <p style="margin:5px 0; font-size:0.9em;">ID Transaction: <b>{c['transaction_id']}</b></p>
                </div>
                """, unsafe_allow_html=True)
                if c['statut'] == 'en_attente':
                    with st.expander("Voir ma preuve"):
                        st.image(c['preuve_image'])

elif menu == "🏠 Tableau de Bord":
    # (Garder le code du fil d'actualité que nous avons fait juste avant)
    st.write("Bienvenue sur le tableau de bord.")

elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()
