elif menu == "🛠️ Admin":
    if st.session_state.connecte and st.session_state.user_info.get('email') == "nernonedouard99@gmail.com":
        st.title("🛠️ Gestion AEEMG")
        t1, t2, t3 = st.tabs(["📢 Adhésions", "💰 Finances", "👥 Membres"])
        
        with t1:
            res = supabase.table("membres").select("*").eq("statut", "en_attente").execute()
            if not res.data: 
                st.info("Aucune demande d'adhésion en attente.")
            else:
                for m in res.data:
                    # On utilise un titre simple sans f-string complexe pour l'expander
                    titre_dossier = f"Dossier de {m['prenom']} {m['nom']}"
                    with st.expander(titre_dossier):
                        st.write(f"**Parents :** {m.get('nom_pere')} & {m.get('nom_mere')}")
                        st.write(f"**Lieu de Naissance :** {m.get('lieu_naissance')}")
                        st.write(f"**Motivation :**")
                        st.info(m.get('motivation'))
                        if st.button("Approuver l'adhésion", key=f"app_{m['id']}"):
                            supabase.table("membres").update({"statut": "approuve"}).eq("id", m['id']).execute()
                            st.success(f"Le membre {m['prenom']} a été approuvé !")
                            st.rerun()
        
        with t2:
            st.subheader("Paiements à valider")
            try:
                res_p = supabase.table("paiements").select("*").eq("statut", "en attente").execute()
                if not res_p.data:
                    st.info("Aucun paiement en attente.")
                else:
                    for p in res_p.data:
                        # Ici aussi, on simplifie l'affichage
                        with st.expander(f"Paiement de {p['email']}"):
                            st.write(f"ID Transaction : {p['transaction_id']}")
                            if st.button("Confirmer le reçu", key=f"p_{p['id']}"):
                                supabase.table("paiements").update({"statut": "validé"}).eq("id", p['id']).execute()
                                supabase.table("membres").update({"cotisation": True}).eq("email", p['email']).execute()
                                st.success("Paiement validé !")
                                st.rerun()
            except:
                st.error("Erreur d'accès à la table paiements.")

        with t3:
            st.subheader("Liste des membres")
            m_all = supabase.table("membres").select("*").execute()
            if m_all.data:
                st.dataframe(m_all.data)
