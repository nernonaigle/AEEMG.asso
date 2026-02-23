import streamlit as st
from supabase import create_client

# 1. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# 2. Gestion de la connexion (Session State)
if "connecte" not in st.session_state:
    st.session_state.connecte = False
    st.session_state.user_info = None

# --- BARRE LATÉRALE ---
st.sidebar.title("Menu AEEMG")
if not st.session_state.connecte:
    menu = st.sidebar.radio("Navigation", ["Connexion", "S'inscrire"])
else:
    menu = st.sidebar.radio("Navigation", ["Mon Profil", "Documents", "Déconnexion"])

# --- LOGIQUE DE DÉCONNEXION ---
if menu == "Déconnexion":
    st.session_state.connecte = False
    st.session_state.user_info = None
    st.rerun()

# --- PAGE D'INSCRIPTION ---
if menu == "S'inscrire":
    st.title("📝 Créer un compte")
    with st.form("inscription"):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        email = st.text_input("Email")
        pwd = st.text_input("Mot de passe", type="password")
        submit = st.form_submit_button("S'inscrire")
        
        if submit:
            if nom and prenom and email and pwd:
                data = {"nom": nom, "prenom": prenom, "email": email, "password": pwd}
                supabase.table("membres").insert(data).execute()
                st.success("Compte créé ! Tu peux maintenant te connecter.")
            else:
                st.error("Remplis tous les champs !")

# --- PAGE DE CONNEXION ---
elif menu == "Connexion":
    st.title("🔑 Connexion")
    email_login = st.text_input("Email")
    pwd_login = st.text_input("Mot de passe", type="password")
    
    if st.button("Se connecter"):
        # On cherche l'utilisateur avec cet email et ce mot de passe
        res = supabase.table("membres").select("*").eq("email", email_login).eq("password", pwd_login).execute()
        
        if len(res.data) > 0:
            st.session_state.connecte = True
            st.session_state.user_info = res.data[0]
            st.success(f"Bienvenue {res.data[0]['prenom']} !")
            st.rerun()
        else:
            st.error("Email ou mot de passe incorrect.")

# --- ESPACE MEMBRE PRIVÉ ---
elif st.session_state.connecte:
    user = st.session_state.user_info
    st.title(f"👋 Espace de {user['prenom']}")
    
    if menu == "Mon Profil":
        st.subheader("Tes informations")
        st.write(f"**Nom :** {user['nom']}")
        st.write(f"**Prénom :** {user['prenom']}")
        st.write(f"**Email :** {user['email']}")
        
    elif menu == "Documents":
        st.subheader("📂 Documents de l'association")
        st.write("Ici, tu trouveras les PV d'assemblée générale et les statuts.")
        # On pourra ajouter des liens de téléchargement plus tard
