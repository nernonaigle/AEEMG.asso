import streamlit as st
from supabase import create_client

# 1. Connexion
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- DESIGN ---
st.set_page_config(page_title="AEEMG", page_icon="🎓")
st.markdown("<style>.stButton>button {width:100%; border-radius:20px; background:#1E3A8A; color:white;}</style>", unsafe_allow_html=True)

if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- MENU ---
st.sidebar.title("AEEMG")
if not st.session_state.connecte:
    menu = st.sidebar.radio("Menu", ["Connexion", "S'inscrire"])
else:
    options = ["🏠 Tableau de Bord", "💳 Cotisations"]
    
    # VERIFICATION ADMIN : Remplace par ton vrai email
    if st.session_state.user_info['email'] == "ton-email@gmail.com":
        options.append("👑 Administration")
        
    options.append("🚪 Déconnexion")
    menu = st.sidebar.radio("Menu", options)
# --- LOGIQUE ---
if menu == "🚪 Déconnexion":
    st.session_state.connecte = False
    st.rerun()

if menu == "S'inscrire":
    st.title("📝 Inscription")
    with st.form("ins"):
        n, p, e, pwd = st.text_input("Nom"), st.text_input("Prénom"), st.text_input("Email"), st.text_input("Pass", type="password")
        if st.form_submit_button("Valider"):
            supabase.table("membres").insert({"nom":n,"prenom":p,"email":e,"password":pwd,"cotisation":False}).execute()
            st.success("Compte créé !")

elif menu == "Connexion":
    st.title("🔑 Connexion")
    e_l, p_l = st.text_input("Email"), st.text_input("Pass", type="password")
    if st.button("Se connecter"):
        res = supabase.table("membres").select("*").eq("email", e_l).eq("password", p_l).execute()
        if res.data:
            st.session_state.connecte, st.session_state.user_info = True, res.data[0]
            st.rerun()
        else: st.error("Erreur d'identifiants")

elif st.session_state.connecte:
    user = st.session_state.user_info
    if menu == "🏠 Tableau de Bord":
        st.title(f"Salut {user['prenom']} !")
        st.info("Bienvenue sur ton espace membre AEEMG.")
    elif menu == "💳 Cotisations":
        st.title("💳 Cotisation")
        # On recharge la donnée en direct
        check = supabase.table("membres").select("cotisation").eq("id", user['id']).execute()
        paye = check.data[0]['cotisation'] if check.data else False
        if paye: st.success("✅ Cotisation à jour")
        else:
            st.warning("⚠️ Non payée")
            if st.button("Payer (Simulation)"):
                supabase.table("membres").update({"cotisation":True}).eq("id", user['id']).execute()
                st.success("Payé ! Reconnecte-toi.")
