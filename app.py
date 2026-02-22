import streamlit as st from supabase import create_client
1. Configuration de la connexion
Remplace les valeurs entre guillemets par tes propres clés Supabase
url = "https://ryfrekltrgaqyryzozhc.supabase.co" key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
Initialisation de la connexion
try: supabase = create_client(url, key) except Exception as e: st.error("Erreur de connexion : Vérifiez vos clés URL et API")
Configuration de la page
st.set_page_config(page_title="Mon Association", page_icon="🤝", layout="wide")
Barre latérale (Menu)
st.sidebar.title("🌟 Espace Membres") menu = ["Accueil / Mur", "Créer mon Profil", "Publier une Activité", "Annuaire des Membres"] choix = st.sidebar.radio("Navigation", menu)
--- PAGE ACCUEIL (LE MUR) ---
if choix == "Accueil / Mur": st.title("📱 Fil d'actualité") st.write("Bienvenue sur le réseau social de l'association !") st.divider()
--- PAGE PROFIL ---
elif choix == "Créer mon Profil": st.title("👤 Mon Profil") st.write("Remplissez vos informations pour que la communauté vous connaisse.")
--- PAGE PUBLIER ---
elif choix == "Publier une Activité": st.title("✍️ Publier sur le mur")
--- PAGE ANNUAIRE ---
elif choix == "Annuaire des Membres": st.title("👥 Annuaire de la communauté") st.write("Retrouvez ici tous les membres inscrits à l'association.") st.table({"Membres": ["Admin", "Président", "Secrétaire"], "Rôle": ["Fondateur", "Direction", "Gestion"]})
