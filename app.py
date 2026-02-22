Oups ! Il est possible que le bloc de code précédent ne soit pas apparu correctement sur ton écran. Je vais te le redonner en texte brut, sans aucun bloc gris, pour être sûr que tu puisses tout copier facilement.

Voici le code à copier (de la première à la dernière ligne) :

import streamlit as st
from supabase import create_client

url = ""
key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"

try:
supabase = create_client(url, key)
except Exception as e:
st.error("Erreur de connexion")

st.set_page_config(page_title="Mon Association", page_icon="🤝", layout="wide")

st.sidebar.title("🌟 Espace Membres")
menu = ["Accueil / Mur", "Créer mon Profil", "Publier une Activité", "Annuaire des Membres"]
choix = st.sidebar.radio("Navigation", menu)

if choix == "Accueil / Mur":
st.title("📱 Fil d'actualité")
st.write("Bienvenue sur le réseau social de l'association !")
st.divider()
st.info("Ici s'afficheront bientôt les messages de la communauté.")

elif choix == "Créer mon Profil":
st.title("👤 Mon Profil")
st.write("Remplissez vos informations.")
nom = st.text_input("Nom complet")
if st.button("Enregistrer"):
st.success(f"Profil de {nom} créé !")

elif choix == "Publier une Activité":
st.title("✍️ Publier sur le mur")
msg = st.text_area("Votre message")
if st.button("Publier"):
st.balloons()
st.success("Publié !")

elif choix == "Annuaire des Membres":
st.title("👥 Annuaire de la communauté")
st.table({"Membres": ["Admin", "Président", "Secrétaire"], "Rôle": ["Fondateur", "Direction", "Gestion"]})