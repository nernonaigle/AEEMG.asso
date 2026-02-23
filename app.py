import streamlit as st
from supabase import create_client

v_url = ""
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

st.set_page_config(page_title="AEEMG", page_icon="🌙", layout="wide")

st.markdown("""
<style>
.stApp {
background: linear-gradient(rgba(18, 54, 38, 0.9), rgba(18, 54, 38, 0.9)),
url("");
background-size: cover;
background-position: center;
background-attachment: fixed;
}
[data-testid="stForm"], [data-testid="stMetric"], .stChatMessage {
background: rgba(255, 255, 255, 0.1) !important;
backdrop-filter: blur(15px);
border-radius: 20px !important;
border: 1px solid rgba(255, 255, 255, 0.2) !important;
padding: 20px !important;
}
h1, h2, h3, label, p, span { color: white !important; }
.stButton>button {
background-color: #2D6A4F !important;
color: white !important;
border-radius: 12px;
border: 1px solid #40916C !important;
height: 3em;
font-weight: bold;
}
[data-testid="stSidebar"] { background-color: rgba(8, 28, 21, 0.95) !important; }
</style>
""", unsafe_allow_html=True)

if "connecte" not in st.session_state:
    st.session_state.connecte = False
    st.session_state.user_info = None

with st.sidebar:
st.markdown("<h1 style='text-align: center;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
if not st.session_state.connecte:
    menu = st.radio("Navigation", ["Connexion", "Inscription"])
else:
st.success(f"Bienvenue {st.session_state.user_info['prenom']}")
menu = st.radio("Espace Privé", ["Tableau de Bord", "Cotisations", "Déconnexion"])

if menu == "Inscription":
    st.title("✨ Rejoindre l'AEEMG")
    with st.form("inscription"):
    n = st.text_input("Nom")
    p = st.text_input("Prénom")
    e = st.text_input("Email")
    pwd = st.text_input("Mot de passe", type="password")
if st.form_submit_button("Créer mon compte"):
if n and p and e and pwd:
    supabase.table("membres").insert({"nom":n,"prenom":p,"email":e,"password":pwd,"cotisation":False}).execute()
    st.success("Compte créé ! Connectez-vous.")
else:
st.error("Champs vides")

elif menu == "Connexion":
st.title("🔑 Connexion")
e_l = st.text_input("Email")
p_l = st.text_input("Mot de passe", type="password")
if st.button("Se connecter"):
    res = supabase.table("membres").select("*").eq("email", e_l).eq("password", p_l).execute()
if res.data:
    st.session_state.connecte = True
    st.session_state.user_info = res.data[0]
    st.rerun()
else:
st.error("Identifiants incorrects")

elif menu == "Tableau de Bord":
if st.session_state.connecte:
    u = st.session_state.user_info
    st.title(f"👋 Paix sur toi, {u['prenom']}")
    c1, c2 = st.columns(2)
    c1.metric("Statut", "Membre Actif")
    c2.metric("Cotisation", "✅ Payée" if u.get('cotisation') else "❌ À régler")

elif menu == "Déconnexion":
st.session_state.connecte = False
st.session_state.user_info = None
st.rerun()
