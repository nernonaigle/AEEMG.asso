import streamlit as st
from supabase import create_client

v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

st.set_page_config(page_title="AEEMG")
st.title("🤝 AEEMG Association")

st.header("📝 Inscription")
nom = st.text_input("Nom")
prenom = st.text_input("Prénom")
email = st.text_input("Email")

if st.button("Envoyer"):
try:
data = {"nom": nom, "prenom": prenom, "email": email}
supabase.table("membres").insert(data).execute()
st.success(f"Inscrit : {prenom}")
except Exception as e:
st.error(f"Erreur : {e}")

st.divider()

st.subheader("📊 Liste des membres en base")
try:
reponse = supabase.table("membres").select("*").execute()
if reponse.data:
for membre in reponse.data:
st.write(f"✅ {membre.get('prenom')} {membre.get('nom')} ({membre.get('email')})")
else:
st.info("Aucun membre trouvé dans la base pour le moment.")
except Exception as e:
st.error("Impossible de lire la base.")
