import streamlit as st
from supabase import create_client

# 1. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- 🎨 DESIGN ---
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

st.markdown("""
<style>
.stApp {
background: linear-gradient(rgba(18, 54, 38, 0.7), rgba(18, 54, 38, 0.7)),
url("WhatsApp Image 2026-02-14 at 18.08.42.jpeg") no-repeat center center fixed;
background-size: cover !important;
}
</style>
""", unsafe_allow_html=True)

# 2. Gestion de Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    st.write("---")
    if not st.session_state.connecte:
        menu = st.radio("Navigation", ["🔑 Connexion", "📝 Inscription"])
    else:
        st.success(f"Bienvenue {st.session_state.user_info['prenom']}")
        # AJOUT DE LA GALERIE DANS LES OPTIONS
        options = ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"]
        
        # Accès Admin pour ton email
        if st.session_state.user_info['email'] == "nernonedouard99@gmail.com":
            options.insert(4, "🛠️ Admin") # Placé avant Déconnexion
        
        menu = st.radio("Espace Privé", options)

# --- CONTENU DES PAGES ---

if menu == "📝 Inscription":
    st.markdown("<h1>✨ Rejoindre la communauté</h1>", unsafe_allow_html=True)
    col1, _ = st.columns([1, 1])
    with col1:
        with st.form("inscription"):
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
            pwd = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer mon compte"):
                supabase.table("membres").insert({"nom":nom,"prenom":prenom,"email":email,"password":pwd,"cotisation":False}).execute()
                st.success("Compte créé avec succès ! Connectez-vous.")

elif menu == "🔑 Connexion":
    st.markdown("<h1 style='text-align: center;'>🔑 Accès Membre</h1>", unsafe_allow_html=True)
    _, cent, _ = st.columns([1, 1, 1])
    with cent:
        e_l = st.text_input("Email")
        p_l = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", e_l).eq("password", p_l).execute()
            if res.data:
                st.session_state.connecte, st.session_state.user_info = True, res.data[0]
                st.rerun()
            else:
                st.error("Identifiants incorrects")

elif menu == "🏠 Tableau de Bord":
    if st.session_state.connecte:
        u = st.session_state.user_info
        st.markdown(f"""
            <div style='text-align: center; padding: 20px;'>
                <img src='https://www.w3schools.com/howto/img_avatar.png' style='border-radius: 50%; width: 120px; height: 120px; border: 3px solid #2D6A4F; background-color: white;'>
                <h1 style='margin-top: 10px;'>{u['prenom']} {u['nom']}</h1>
                <p style='color: #ccc; font-style: italic;'>{u.get('bio', 'Membre de la communauté AEEMG')}</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📋 Mes Infos")
            st.write(f"📧 Email : {u['email']}")
            st.write(f"📞 Tel : {u.get('telephone', 'Non renseigné')}")
            st.write(f"📍 Ville : {u.get('ville', 'Non renseignée')}")
            with st.expander("⚙️ Modifier mes infos"):
                with st.form("update_profil"):
                    new_tel = st.text_input("Téléphone", value=u.get('telephone', ''))
                    new_ville = st.text_input("Ville", value=u.get('ville', ''))
                    new_bio = st.text_area("Bio", value=u.get('bio', ''))
                    if st.form_submit_button("Enregistrer"):
                        supabase.table("membres").update({"telephone": new_tel, "ville": new_ville, "bio": new_bio}).eq("email", u['email']).execute()
                        st.success("Enregistré ! Reconnectez-vous pour actualiser.")
        
        with col2:
            st.markdown("### 💎 Mon Statut")
            if u.get('cotisation'):
                st.success("Membre à jour ✅")
            else:
                st.warning("Cotisation à régler ❌")
        
        st.write("---")
        st.markdown("### 📢 Fil d'actualité")
        try:
            res_ann = supabase.table("annonces").select("*").order("date", desc=True).limit(1).execute()
            if res_ann.data:
                ann = res_ann.data[0]
                if ann['important']:
                    st.error(f"🚨 **IMPORTANT :** {ann['message']}")
                else:
                    st.info(f"💡 {ann['message']}")
            else:
                st.info("💡 Bienvenue sur votre nouvel espace membre AEEMG !")
        except:
            st.info("💡 Fil d'actualité en attente de configuration.")
    else:
        st.warning("Veuillez vous connecter.")

elif menu == "💳 Cotisations":
    if st.session_state.connecte:
        st.markdown("<h1>💳 Ma Cotisation</h1>", unsafe_allow_html=True)
        u = st.session_state.user_info
        st.write("Montant : **50 000 GNF / an**")
        mode = st.selectbox("Mode de paiement", ["Orange Money", "Moov Money"])
        trans_id = st.text_input("ID de transaction")
        if st.button("Valider le paiement"):
            if trans_id:
                supabase.table("paiements").insert({"email": u['email'], "transaction_id": trans_id, "mode": mode, "statut": "en attente"}).execute()
                st.success("Demande envoyée à l'admin !")
            else:
                st.error("Entrez l'ID de transaction")
    else:
        st.warning("Veuillez vous connecter.")

elif menu == "📂 Documents":
    st.markdown("<h1>📂 Bibliothèque de l'AEEMG</h1>", unsafe_allow_html=True)
    st.write("Retrouvez ici tous les documents officiels et ressources utiles.")
    cat = st.tabs(["📜 Administratif", "📚 Études", "🌙 Religieux"])

    with cat[0]:
        st.subheader("Documents de l'Association")
        c1, c2 = st.columns(2)
        with c1:
            st.info("📄 Statuts de l'AEEMG")
            st.download_button("Télécharger", "Contenu PDF", file_name="statuts_aeemg.pdf")
        with c2:
            st.info("📄 Règlement Intérieur")
            st.download_button("Télécharger", "Contenu PDF", file_name="reglement_aeemg.pdf")

    with cat[1]:
        st.subheader("Ressources Académiques")
        st.warning("⚠️ Section en cours de mise à jour.")

    with cat[2]:
        st.subheader("Ressources Islamiques")
        st.success("📖 Calendrier des prières - Conakry")
        st.download_button("Télécharger le Calendrier", "Contenu PDF", file_name="calendrier_priere.pdf")

# --- NOUVELLE SECTION : GALERIE ---
elif menu == "📸 Galerie":
    st.markdown("<h1>📸 Vie de l'Association</h1>", unsafe_allow
