import streamlit as st
from supabase import create_client

# 1. Connexion (Inchangée)
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- 🎨 DESIGN & STYLE ---
st.set_page_config(page_title="AEEMG Espace Membre", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    /* Style global */
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1E3A8A; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #2563EB; border: none; color: white; }
    
    /* Cartes d'info */
    .card { padding: 20px; border-radius: 10px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    h1 { color: #1E3A8A; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# 2. Gestion Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- Sidebar Stylisée ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/100/education.png", width=100)
    st.title("AEEMG")
    st.write("Association des Étudiants")
    st.divider()
    
    if not st.session_state.connecte:
        menu = st.radio("Navigation", ["🔑 Connexion", "📝 S'inscrire"])
    else:
        st.success(f"Connecté : {st.session_state.user_info['prenom']}")
        options = ["🏠 Tableau de Bord", "💳 Cotisations"]
        if st.session_state.user_info['email'] == "tonemail@gmail.com": # Mets ton mail ici
            options.append("👑 Admin")
        options.append("🚪 Déconnexion")
        menu = st.radio("Navigation", options)

# --- PAGES ---

# 1. INSCRIPTION
if menu == "📝 S'inscrire":
    st.markdown("<h1>📝 Créer un compte membre</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        with st.form("ins"):
            n = st.text_input("Nom de famille")
            p = st.text_input("Prénom")
            e = st.text_input("Adresse Email")
            pwd = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Finaliser l'inscription"):
                if n and p and e and pwd:
                    supabase.table("membres").insert({"nom":n,"prenom":p,"email":e,"password":pwd,"cotisation":False}).execute()
                    st.success("Bienvenue ! Connectez-vous maintenant.")
    with col2:
        st.info("Rejoindre l'AEEMG vous permet d'accéder aux documents exclusifs et de gérer vos cotisations en ligne.")

# 2. CONNEXION
elif menu == "🔑 Connexion":
    st.markdown("<h1 style='text-align: center;'>🔑 Connexion</h1>", unsafe_allow_html=True)
    _, cent, _ = st.columns([1, 2, 1])
    with cent:
        e_l = st.text_input("Email")
        p_l = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", e_l).eq("password", p_l).execute()
            if res.data:
                st.session_state.connecte, st.session_state.user_info = True, res.data[0]
                st.rerun()
            else: st.error("Identifiants incorrects.")

# 3. DASHBOARD
elif menu == "🏠 Tableau de Bord":
    u = st.session_state.user_info
    st.markdown(f"<h1>👋 Bonjour, {u['prenom']} !</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Statut Membre", "Actif")
    col2.metric("Cotisation 2026", "Payée" if u.get('cotisation') else "À régler")
    col3.metric("Annonces", "2 Nouvelles")
    
    st.divider()
    st.subheader("📢 Actualités de l'association")
    st.info("La prochaine Assemblée Générale aura lieu le 15 mars à 18h.")

# 4. COTISATION (VISUEL)
elif menu == "💳 Cotisations":
    st.markdown("<h1>💳 Ma Cotisation</h1>", unsafe_allow_html=True)
    u = st.session_state.user_info
    res = supabase.table("membres").select("cotisation").eq("id", u['id']).execute()
    paye = res.data[0]['cotisation'] if res.data else False
    
    if paye:
        st.balloons()
        st.success("### ✅ Vous êtes en règle !\nMerci pour votre soutien à l'AEEMG.")
    else:
        st.warning("### ⚠️ Cotisation en attente\nPour accéder à tous les services, veuillez régler votre cotisation annuelle.")
        if st.button("Simuler le paiement par carte"):
            supabase.table("membres").update({"cotisation":True}).eq("id", u['id']).execute()
            st.success("Paiement validé ! Veuillez rafraîchir.")

# 5. ADMIN (PROPRE)
elif menu == "👑 Admin":
    st.markdown("<h1>👑 Administration</h1>", unsafe_allow_html=True)
    res = supabase.table("membres").select("*").execute()
    st.dataframe(res.data, use_container_width=True) # Affiche un tableau interactif pro

# LOGIQUE DECO
if menu == "🚪 Déconnexion":
    st.session_state.connecte = False
    st.rerun()
