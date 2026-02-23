import streamlit as st
from supabase import create_client

# Connexion
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

st.title("🤝 AEEMG Association")

# Formulaire
nom = st.text_input("Nom")
prenom = st.text_input("Prénom")
email = st.text_input("Email")

if st.button("S'inscrire"):
    # Attention : les 2 lignes suivantes ont 4 espaces au début
    data = {"nom": nom, "prenom": prenom, "email": email}
    supabase.table("membres").insert(data).execute()
    st.success("C'est bon, tu es inscrit !")

st.divider()
st.subheader("Liste des membres")

# Affichage des membres
res = supabase.table("membres").select("*").execute()
for m in res.data:
    # Attention : la ligne suivante a 4 espaces au début
    st.write(f"👤 {m.get('prenom')} {m.get('nom')}")
