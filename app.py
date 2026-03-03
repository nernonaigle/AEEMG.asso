import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime, date
import calendar

# ... (Garder tes fonctions de connexion et hashage identiques au début) ...

# =========================================================
# DESIGN / CSS AVANCÉ (STYLE FACEBOOK FEED)
# =========================================================
st.markdown("""
<style>
/* --- STYLE DES COMMENTAIRES --- */
.comment-bubble {
    background-color: #f0f2f5;
    border-radius: 18px;
    padding: 10px 15px;
    margin-top: 8px;
    margin-left: 50px;
    border: none;
    max-width: 85%;
}

.comment-author {
    font-weight: 800;
    color: #050505;
    font-size: 0.9rem;
    margin-bottom: 2px;
}

.comment-text {
    color: #050505;
    font-size: 0.95rem;
    line-height: 1.3;
}

.social-counts {
    display: flex;
    justify-content: space-between;
    padding: 10px 5px;
    color: #65676b;
    font-size: 0.9rem;
    font-weight: 600;
}

/* --- BOUTONS ACTIONS LÉGERS --- */
.stButton > button {
    background: transparent !important;
    color: #65676b !important;
    border: none !important;
    font-weight: 700 !important;
    transition: 0.2s;
}
.stButton > button:hover {
    background: #f2f2f2 !important;
    color: #064e3b !important;
}
</style>
""", unsafe_allow_html=True)

# ... (Logique de navigation inchangée) ...

elif st.session_state.connecte:
    u = st.session_state.user_info
    
    if menu == "🏠 Tableau de Bord":
        # ... (Garder le Header et le formulaire de publication identiques) ...

        # FLUX DE PUBLICATIONS
        res_posts = supabase.table("posts").select("*").order("date_pub", desc=True).limit(10).execute()
        
        for post in res_posts.data:
            # Récupérer les commentaires pour ce post spécifique
            res_comm = supabase.table("commentaires").select("*").eq("post_id", post['id']).order("created_at", desc=True).execute()
            nb_comm = len(res_comm.data)
            
            with st.container():
                st.markdown(f"""
                <div class="post-card">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <img src="{post.get('auteur_photo') or 'https://www.w3schools.com/howto/img_avatar.png'}" style="width:45px; height:45px; border-radius:50%; object-fit: cover;">
                        <div>
                            <b style="color: #064e3b;">{post.get('auteur_nom')}</b><br>
                            <small>{post.get('date_pub')[:10]}</small>
                        </div>
                    </div>
                    <div class="post-text">{post.get('contenu')}</div>
                """, unsafe_allow_html=True)

                if post.get("media_url"):
                    if post.get("media_type") == "image": st.image(post["media_url"], use_container_width=True)
                    else: st.video(post["media_url"])

                # --- COMPTEURS ---
                st.markdown(f"""
                <div class="social-counts">
                    <span>❤️ {post.get('likes', 0)} J'aime</span>
                    <span>{nb_comm} commentaires</span>
                </div>
                <hr style="margin: 0; opacity: 0.1;">
                """, unsafe_allow_html=True)

                # --- BOUTONS ACTIONS ---
                c_lk, c_cm, _ = st.columns([1, 1, 1.5])
                with c_lk:
                    if st.button(f"👍 J'aime", key=f"lk_{post['id']}"):
                        # Ici tu pourrais ajouter une logique d'update de la table posts
                        st.toast("Vous aimez ce post !")
                
                with c_cm:
                    show_comm = st.toggle("Commenter", key=f"tog_{post['id']}")

                # --- ZONE DE COMMENTAIRES (Style Facebook) ---
                if show_comm:
                    with st.form(f"f_comm_{post['id']}", clear_on_submit=True):
                        c_txt = st.text_input("Écrivez un commentaire...", key=f"in_{post['id']}")
                        if st.form_submit_button("Envoyer"):
                            new_c = {
                                "post_id": post['id'],
                                "auteur_nom": f"{u['prenom']} {u['nom']}",
                                "contenu": c_txt,
                                "user_id": u['id']
                            }
                            supabase.table("commentaires").insert(new_c).execute()
                            st.rerun()

                # --- AFFICHAGE DES DERNIERS COMMENTAIRES ---
                for comm in res_comm.data[:3]: # Affiche les 3 plus récents
                    st.markdown(f"""
                    <div class="comment-bubble">
                        <div class="comment-author">{comm['auteur_nom']}</div>
                        <div class="comment-text">{comm['contenu']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div><br>", unsafe_allow_html=True)
