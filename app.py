import streamlit as st
from supabase import create_client

1. Configuration de la connexion
url = ""
key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"

Initialisation de la connexion
try:
supabase = create_client(url, key)
except Exception as e:
st.error("Erreur de connexion : Vérifiez vos clés URL et API")

Configuration de la page
st.set_page_config(page_title="Mon Association", page_icon="🤝", layout="wide")

Barre latérale (Menu)
st.sidebar.title("🌟 Espace Membres")
menu = ["Accueil / Mur", "Créer mon Profil", "Publier une Activité", "Annuaire des Membres"]
choix = st.sidebar.radio("Navigation", menu)

--- PAGE ACCUEIL (LE MUR) ---
if choix == "Accueil / Mur":
st.title("📱 Fil d'actualité")
st.write("Bienvenue sur le réseau social de l'association !")
st.divider()
st.info("Ici s'afficheront bientôt les messages de la communauté.")

--- PAGE PROFIL ---
elif choix == "Créer mon Profil":
st.title("👤 Mon Profil")
st.write("Remplissez vos informations pour que la communauté vous connaisse.")
nom = st.text_input("Nom complet")
if st.button("Enregistrer"):
st.success(f"Profil de {nom} créé !")

--- PAGE PUBLIER ---
elif choix == "Publier une Activité":
st.title("✍️ Publier sur le mur")
msg = st.text_area("Votre message")
if st.button("Publier"):
st.balloons()
st.success("Publié !")

--- PAGE ANNUAIRE ---
elif choix == "Annuaire des Membres":
st.title("👥 Annuaire de la communauté")
st.write("Retrouvez ici tous les membres inscrits à l'association.")
st.table({"Membres": ["Admin", "Président", "Secrétaire"], "Rôle": ["Fondateur", "Direction", "Gestion"]})