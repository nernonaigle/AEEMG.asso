import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime

# 1. Configuration de la page
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

# 2. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- FONCTIONS DE SÉCURITÉ ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 🎨 DESIGN (Vert Émeraude & Or) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Poppins', sans-serif; }
    .stApp {
        background: linear-gradient(rgba(2, 44, 34, 0.9), rgba(2, 44, 34, 0.95)),
        url("https://images.unsplash.com/photo-1518005020250-6eb5f3f2754d?q=80&w=2000") no-repeat center center fixed;
        background-size: cover !important;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 12px !important;
        background-color: #065f46 !important;
        color: white !important;
        border: 1px solid #D4AF37 !important;
        height: 45px;
        width: 100%;
    }
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
        st.markdown(f"🟢 **{st.session_state.user_info.get('prenom')}**")
        options = ["🏠 Tableau de Bord", "🛠️ Admin", "🚪 Déconnexion"]
        # L'onglet Admin ne s'affiche que pour toi
        if st.session_state.user_info.get('email') != "nernonedouard99@gmail.com":
            options.remove("🛠️ Admin")
        menu = st.radio("Menu", options)

# --- PAGES ---

if menu == "📝 Inscription":
    st.markdown("<h1 style='color: white;'>📝 Formulaire d'Adhésion</h1>", unsafe_allow_html=True)
    with st.form("inscription_form"):
        col1, col2 = st.columns(2)
        nom = col1.text_input("Nom")
        prenom = col2.text_input("Prénom")
        email = col1.text_input("Email")
        pwd = col2.text_input("Mot de passe", type="password")
        ville = col1.text_input("Ville")
        organe = col2.selectbox("Organe de base", ["Bureau National", "Section Universitaire", "Antenne Régionale"])
        motivation = st.text_area("Motivation (Pourquoi rejoindre l'AEEMG ?)")
        
        if st.form_submit_button("Envoyer ma demande"):
            if email and pwd and len(motivation) > 10:
                data = {
                    "nom": nom, "prenom": prenom, "email": email, 
                    "password": hasher_password(pwd), "ville": ville, 
                    "organe_base": organe, "motivation": motivation,
                    "statut": "en_attente", "cotisation": False
                }
                try:
                    supabase.table("membres").insert(data).execute()
                    st.success("✅ Demande envoyée ! Un administrateur doit valider votre compte.")
                    st.balloons()
                except:
                    st.error("❌ Cet email est déjà utilisé.")
            else:
                st.warning("Veuillez remplir tous les champs correctement.")

elif menu == "🔑 Connexion":
    st.markdown("<h1 style='text-align: center; color: white;'>🔑 Connexion</h1>", unsafe_allow_html=True)
    with st.container():
        _, center, _ = st.columns([1, 2, 1])
        with center:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            e_log = st.text_input("Email")
            p_log = st.text_input("Mot de passe", type="password")
            if st.button("Se connecter"):
                res = supabase.table("membres").select("*").eq("email", e_log).eq("password", hasher_password(p_log)).execute()
                if res.data:
                    user = res.data[0]
                    if user.get('statut') == "approuve":
                        st.session_state.connecte, st.session_state.user_info = True, user
                        st.rerun()
                    else:
                        st.warning("⏳ Votre compte est en attente de validation par l'administration.")
                else:
                    st.error("❌ Identifiants incorrects.")
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏠 Tableau de Bord":
    if st.session_state.connecte:
        u = st.session_state.user_info
        st.markdown(f"## Bienvenue, {u['prenom']} {u['nom']} 👋")
        st.markdown(f"""<div class="glass-card">
            <h4>Informations Membre</h4>
            <p><b>ID :</b> #00{u['id']}</p>
            <p><b>Statut :</b> ✅ Approuvé</p>
            <p><b>Organe :</b> {u['organe_base']}</p>
            <p><b>Cotisation :</b> {"💰 À jour" if u['cotisation'] else "⚠️ Non payée"}</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.warning("Veuillez vous connecter.")

elif menu == "🛠️ Admin":
    if st.session_state.connecte and st.session_state.user_info['email'] == "nernonedouard99@gmail.com":
        st.title("🛠️ Interface Administrateur")
        res = supabase.table("membres").select("*").eq("statut", "en_attente").execute()
        if not res.data:
            st.info("Aucune demande en attente.")
        else:
            for m in res.data:
                with st.expander(f"Demande de {m['prenom']} {m['nom']}"):
                    st.write(f"**Email :** {m['email']}")
                    st.write(f"**Motivation :** {m['motivation']}")
                    if st.button("Approuver", key=f"btn_{m['id']}"):
                        supabase.table("membres").update({"statut": "approuve"}).eq("id", m['id']).execute()
                        st.success(f"Compte de {m['prenom']} activé !")
                        st.rerun()

elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()
