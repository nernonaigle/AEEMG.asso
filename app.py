import streamlit as st
from supabase import create_client

url = ""
key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"

supabase = create_client(url, key)

st.title("🤝 AEEMG Association")

st.write("Bienvenue sur notre application !")

nom = st.text_input("Quel est ton nom ?")

if st.button("Dire bonjour"):
st.write(f"Bonjour {nom} ! Ton application fonctionne enfin.")
st.balloons()