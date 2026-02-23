import streamlit as st
from supabase import create_client

url = ""
key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(url, key)

st.set_page_config(page_title="AEEMG Association", page_icon="🤝")

st.sidebar.title("🌟 Menu")
menu = ["Accueil / Mur", "Créer mon Profil", "Publier une Activité", "Annuaire"]
choix = st.sidebar.radio("Navigation", menu)

if choix == "Accueil / Mur":
st.button("📱 Fil d'actualité")  
st.write("Bienvenue sur l'espace de l'AEEMG !")
st.info("Les publications des membres s'afficheront ici.")
t.title("📱 Fil d'actualité")  
elif choix == "Créer mon Profil":
st.title("👤 Mon Profil")
nom = st.text_input("Nom complet")
bio = st.text_area("Ma présentation (bio)")
if st.button("Enregistrer"):
st.success(f"Bravo {nom} ! Ton profil est prêt.")

elif choix == "Publier une Activité":
st.title("✍️ Publier")
titre = st.text_input("Titre de l'activité")
contenu = st.text_area("Détails")
if st.button("Publier sur le mur"):
st.balloons()
st.success("C'est publié !")

elif choix == "Annuaire":
st.title("👥 Annuaire")
st.write("Liste des membres de l'association :")
membres = {"Membres": ["Admin", "Président"], "Rôle": ["Gestion", "Direction"]}
st.table(membres)
