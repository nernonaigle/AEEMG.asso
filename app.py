import streamlit as st
from supabase import create_client

url = "https://ryfrekltrgaqyryzozhc.supabase.co"
key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"

supabase = create_client(url, key)

st.title("🤝 AEEMG Association")
st.write("Félicitations ! L'application est en ligne.")
st.write("Ceci est la version de test sans erreurs d'espaces.")

nom_utilisateur = st.text_input("Entre ton nom pour tester :")
st.write("Utilisateur détecté :")
st.success(nom_utilisateur)