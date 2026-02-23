import streamlit as st
from supabase import create_client

# Connexion à ta base
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

st.set_page_config(page_title="AEEMG", page_icon="🤝")

# Titre centré
st.title("🤝 Inscription AEEMG")
st.write("Veuillez remplir vos informations pour rejoindre l'association.")

# Formulaire ordonné
with st.form("formulaire_inscription"):
    nom = st.text_input("Votre Nom")
    prenom = st.text_input("Votre Prénom")
    email = st.text_input("Votre adresse Email")
    password = st.text_input("Choisissez un Mot de Passe", type="password")
    
    # Bouton de validation
    submit = st.form_submit_button("Créer mon compte")

# Action après clic
if submit:
    if nom and prenom and email and password:
        # On prépare les données (vérifie que tes colonnes sur Supabase ont ces noms précis)
        data = {
            "nom": nom, 
            "prenom": prenom, 
            "email": email, 
            "password": password
        }
        
        try:
            supabase.table("membres").insert(data).execute()
            st.success(f"Félicitations {prenom} ! Tu es bien inscrit(e).")
            st.balloons() # Petite animation de fête
        except Exception as e:
            st.error("Erreur lors de l'inscription. Vérifie que la colonne 'password' existe sur Supabase.")
    else:
        st.warning("⚠️ Attention : Tous les champs doivent être remplis.")
