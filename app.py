import streamlit as st
from supabase import create_client

v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

st.set_page_config(page_title="AEEMG", page_icon="🤝")
st.title("🤝 AEEMG Association")

menu = st.radio("Navigation", ["Accueil", "Inscription"], horizontal=True)

if menu == "Accueil":
st.header("Fil d'actualité")
st.write("Bienvenue sur l'espace officiel de l'AEEMG !")

if menu == "Inscription":
st.header("Devenir membre")
nom = st.text_input("Nom")
prenom = st.text_input("Prénom")
filiere = st.selectbox("Filière", ["Médecine", "Pharmacie", "Odontologie", "Autre"])
email = st.text_input("Email")
if st.button("S'inscrire"):
if nom and prenom and email:
st.success(f"Merci {prenom} ! Inscription reçue.")
else:
st.warning("Remplis tous les champs.")
