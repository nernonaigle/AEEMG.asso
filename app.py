import streamlit as st
from supabase import create_client

# 1. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- 🎨 DESIGN "ÉMERAUDE & SÉRÉNITÉ" ---
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
        
        # On définit les options de base
        options = ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "🚪 Déconnexion"]
        
        # --- PARTIE À PERSONNALISER ---
        # Remplace l'email ci-dessous par ton email exact
        if st.session_state.user_info['email'] == "nernonedouard99@gmail.com":
            options.insert(3, "🛠️ Admin") # Ceci ajoute 'Admin' avant 'Déconnexion'
        
        menu = st.radio("Espace Privé", options)
# --- CONTENU DES PAGES ---

if menu == "📝 Inscription":
    st.markdown("<h1>✨ Rejoindre la communauté</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.form("inscription"):
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
            pwd = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Créer mon compte"):
                supabase.table("membres").insert({"nom":nom,"prenom":prenom,"email":email,"password":pwd,"cotisation":False}).execute()
                st.success("Compte créé avec succès !")
    with col2:
        st.markdown("""
        ### Pourquoi adhérer ?
        - Accès aux ressources éducatives
        - Participation aux événements fraternels
        - Soutien à la vie étudiante
        """)

elif menu == "🛠️ Admin":
    st.markdown("<h1>🛠️ Validation des Cotisations</h1>", unsafe_allow_html=True)
    
    # On va chercher les paiements qui sont 'en attente' dans Supabase
    try:
        res = supabase.table("paiements").select("*").eq("statut", "en attente").execute()
        attentes = res.data

        if not attentes:
            st.info("Aucun paiement en attente pour le moment. ✅")
        else:
            st.write(f"Il y a {len(attentes)} demande(s) à vérifier :")
            for p in attentes:
                with st.expander(f"Paiement de {p['email']}"):
                    st.write(f"**ID Transaction :** {p['transaction_id']}")
                    st.write(f"**Méthode :** {p['mode']}")
                    
                    if st.button(f"Valider le membre {p['email']}", key=p['id']):
                        # 1. On change le statut du paiement en 'validé'
                        supabase.table("paiements").update({"statut": "validé"}).eq("id", p['id']).execute()
                        
                        # 2. On met à jour le profil du membre (cotisation = True)
                        supabase.table("membres").update({"cotisation": True}).eq("email", p['email']).execute()
                        
                        st.success(f"Le profil de {p['email']} a été mis à jour !")
                        st.rerun()
    except Exception as e:
        st.error(f"Erreur : {e}")
elif menu == "🏠 Tableau de Bord":
    if st.session_state.connecte:
        u = st.session_state.user_info
        st.markdown(f"""
            <div style='text-align: center; padding: 20px;'>
                <img src='' style='border-radius: 50%; width: 120px; height: 120px; border: 3px solid #2D6A4F; background-color: white;'>
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
                        st.success("Enregistré ! Reconnectez-vous pour voir les changements.")
        
        with col2:
            st.markdown("### 💎 Mon Statut")
            if u.get('cotisation'):
                st.success("Membre à jour ✅")
            else:
                st.warning("Cotisation à régler ❌")
                st.button("Payer ma cotisation")
        
        st.write("---")
        st.markdown("### 📢 Fil d'actualité")
        st.info("💡 Annonce : La réunion mensuelle aura lieu dimanche à 10h.")
    else:
        st.warning("Veuillez vous connecter.")
elif menu == "💳 Cotisations":
    if st.session_state.connecte:
        st.markdown("<h1>💳 Ma Cotisation</h1>", unsafe_allow_html=True)
        u = st.session_state.user_info
elif menu == "🚪 Déconnexion":
    st.session_state.connecte = False
    st.rerun()
