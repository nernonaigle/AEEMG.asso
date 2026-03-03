import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime

# ... (Garder tes fonctions de connexion et process_media habituelles) ...

# =========================================================
# LOGIQUE DU FIL D'ACTUALITÉ (DANS LA PAGE CONNECTÉE)
# =========================================================
if menu == "🏠 Fil d'actualité":
    u = st.session_state.user_info
    st.markdown(f"<h2 class='gold-text'>Bienvenue, {u['prenom']} !</h2>", unsafe_allow_html=True)
    
    # 1. ZONE DE PUBLICATION (Simplifiée)
    with st.expander("📝 Publier quelque chose sur le mur"):
        with st.form("post_form", clear_on_submit=True):
            txt = st.text_area("Quoi de neuf ?", placeholder="Exprimez-vous...")
            if st.form_submit_button("PUBLIER"):
                new_post = {
                    "user_id": u['id'], 
                    "auteur_nom": f"{u['prenom']} {u['nom']}", 
                    "contenu": txt, 
                    "likes": 0, # Initialisation à 0
                    "date_pub": datetime.now().isoformat()
                }
                supabase.table("posts").insert(new_post).execute()
                st.rerun()

    # 2. RÉCUPÉRATION DES POSTS
    res_posts = supabase.table("posts").select("*").order("date_pub", desc=True).limit(10).execute()
    
    for post in res_posts.data:
        # Récupérer les commentaires liés
        res_c = supabase.table("commentaires").select("*").eq("post_id", post['id']).execute()
        nb_comms = len(res_c.data)
        nb_likes = post.get('likes', 0) # On récupère le nombre actuel de likes

        st.markdown(f"""
        <div class="post-card" style="background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <img src="https://www.w3schools.com/howto/img_avatar.png" style="width:40px; height:40px; border-radius:50%;">
                <b style="color: #064e3b;">{post['auteur_nom']}</b>
            </div>
            <p style="font-size: 1.1rem; font-weight: 700; color: #000000;">{post['contenu']}</p>
            
            <div style="display: flex; justify-content: space-between; color: #65676b; font-weight: 800; font-size: 0.9rem; margin-top: 15px; padding: 5px 0; border-top: 1px solid #f0f2f5;">
                <span>❤️ {nb_likes} J'aime</span>
                <span>💬 {nb_comms} commentaires</span>
            </div>
        """, unsafe_allow_html=True)

        # 3. BOUTONS D'ACTION
        col_like, col_comm = st.columns([1, 1])
        
        with col_like:
            # FONCTION LIKE : Incrémente en base de données
            if st.button(f"👍 J'aime", key=f"btn_lk_{post['id']}", use_container_width=True):
                new_count = nb_likes + 1
                try:
                    # Mise à jour dans Supabase
                    supabase.table("posts").update({"likes": new_count}).eq("id", post['id']).execute()
                    st.toast(f"Vous avez aimé le post de {post['auteur_nom']} !")
                    st.rerun() # Recharge pour voir le nouveau chiffre
                except Exception as e:
                    st.error("Erreur lors du Like")

        with col_comm:
            show_comment_area = st.toggle("💬 Commenter", key=f"tog_c_{post['id']}")

        # 4. ZONE COMMENTAIRES (Si toggle actif)
        if show_comment_area:
            with st.form(f"form_c_{post['id']}", clear_on_submit=True):
                c_input = st.text_input("Écrire un commentaire...", key=f"in_c_{post['id']}")
                if st.form_submit_button("Envoyer"):
                    if c_input:
                        supabase.table("commentaires").insert({
                            "post_id": post['id'], 
                            "auteur_nom": u['prenom'], 
                            "contenu": c_input
                        }).execute()
                        st.rerun()

            # Affichage des bulles de commentaires
            for c in res_c.data:
                st.markdown(f"""
                <div style="background-color: #f0f2f5; border-radius: 15px; padding: 10px; margin: 5px 0 5px 40px;">
                    <b style="font-size: 0.85rem; color: #000;">{c['auteur_nom']}</b><br>
                    <span style="color: #050505;">{c['contenu']}</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True) # Fermeture de la carte
