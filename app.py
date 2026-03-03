import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime, date
import calendar
import base64
from io import BytesIO
from PIL import Image

# =========================================================
# CONFIGURATION PAGE
# =========================================================
st.set_page_config(
    page_title="AEEMG - Espace Membre",
    page_icon="🌙",
    layout="wide"
)

# =========================================================
# CONNEXION SUPABASE
# =========================================================
# Conseil : Utilisez st.secrets pour vos clés en production
SUPABASE_URL = "https://ryfrekltrgaqyryzozhc.supabase.co"
SUPABASE_KEY = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# FONCTIONS UTILES
# =========================================================
def hasher_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_cotisation_du_mois(user_id) -> bool:
    if not user_id: return False
    today = date.today()
    first_day = today.replace(day=1).isoformat()
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1]).isoformat()
    try:
        res = supabase.table("cotisations").select("*").eq("user_id", user_id).eq("statut", "valide").gte("date_paiement", first_day).lte("date_paiement", last_day).execute()
        return len(res.data) > 0
    except Exception:
        return False

def process_media(file, is_profile=False):
    if file is None: return None, None
    try:
        file_type = file.type.split("/")[0]
        if file_type == "image":
            img = Image.open(file)
            size = (300, 300) if is_profile else (800, 800)
            img.thumbnail(size)
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            encoded = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{encoded}", "image"
        else:
            encoded = base64.b64encode(file.read()).decode()
            return f"data:{file.type};base64,{encoded}", "video"
    except Exception as e:
        st.error(f"Erreur média : {e}")
        return None, None

# =========================================================
# DESIGN / CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp {
    background: linear-gradient(135deg, rgba(2,44,34,0.95), rgba(1,20,15,0.98)),
    url("https://images.unsplash.com/photo-1564115484-a4aaa88d5449?q=80&w=2000") no-repeat center center fixed;
    background-size: cover !important;
}
.glass-card {
    background: rgba(255,255,255,0.06); backdrop-filter: blur(15px);
    border-radius: 16px; padding: 25px; border: 1px solid rgba(255,255,255,0.12);
    color: white; margin-bottom: 20px;
}
.gold-text { color: #D4AF37; font-weight: 800; }
.badge-paye { background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8em; display: inline-block;}
.badge-impaye { background: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.8em; display: inline-block;}

.member-card {
    background: linear-gradient(135deg, #022c22 0%, #064e3b 100%);
    border: 2px solid #D4AF37; border-radius: 15px; padding: 20px;
    max-width: 350px; color: white; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# INITIALISATION SESSION
# =========================================================
if "connecte" not in st.session_state:
    st.session_state.connecte = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("<h1 style='text-align:center;color:#D4AF37;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    
    if st.session_state.connecte:
        u = st.session_state.user_info
        est_a_jour = check_cotisation_du_mois(u.get("id"))
        
        # Photo de profil
        avatar = u.get("photo_url") if u.get("photo_url") else "https://www.w3schools.com/howto/img_avatar.png"
        st.image(avatar, width=100)
        
        st.markdown(f"**{u.get('prenom', '')} {u.get('nom', '')}**")
        
        badge = f"<div class='badge-paye'>✅ À JOUR</div>" if est_a_jour else f"<div class='badge-impaye'>⚠️ À RÉGLER</div>"
        st.markdown(badge, unsafe_allow_html=True)
        st.write("---")
        
        menu = st.radio("Navigation", ["🏠 Tableau de Bord", "💳 Cotisations", "🪪 Carte de Membre", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# =========================================================
# ROUTAGE DES PAGES
# =========================================================

if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text'>Connexion</h2>", unsafe_allow_html=True)
    with st.container():
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            try:
                res = supabase.table("membres").select("*").eq("email", email).eq("password", hasher_password(password)).execute()
                if res.data:
                    user = res.data[0]
                    if user.get("statut") == "approuve":
                        st.session_state.connecte = True
                        st.session_state.user_info = user
                        st.success("Connexion réussie !")
                        st.rerun()
                    else:
                        st.warning("⏳ Votre compte est en attente de validation par l'administration.")
                else:
                    st.error("Email ou mot de passe incorrect.")
            except Exception as e:
                st.error(f"Erreur de connexion : {e}")

elif menu == "📝 Inscription":
    st.markdown("<h2 class='gold-text'>Demande d'adhésion</h2>", unsafe_allow_html=True)
    with st.form("inscription"):
        col1, col2 = st.columns(2)
        nom = col1.text_input("Nom")
        prenom = col2.text_input("Prénom")
        email = col1.text_input("Email")
        password = col2.text_input("Mot de passe", type="password")
        ville = col1.text_input("Ville")
        organe = col2.selectbox("Organe de base", ["Bureau National", "Section Universitaire", "Section Scolaire", "Section Communale"])
        photo = st.file_uploader("Photo de profil", type=['jpg', 'png', 'jpeg'])
        motivation = st.text_area("Motivation")
        
        if st.form_submit_button("Envoyer le dossier"):
            if nom and prenom and email and password:
                p_url, _ = process_media(photo, is_profile=True)
                data = {
                    "nom": nom, "prenom": prenom, "email": email,
                    "password": hasher_password(password), "ville": ville,
                    "motivation": motivation, "organe_base": organe,
                    "statut": "en_attente", "photo_url": p_url
                }
                supabase.table("membres").insert(data).execute()
                st.success("Dossier envoyé avec succès !")
            else:
                st.error("Veuillez remplir les champs obligatoires.")

elif st.session_state.connecte:
    u = st.session_state.user_info
    
    if menu == "🏠 Tableau de Bord":
        st.markdown(f"<h1 class='gold-text'>Salam, {u.get('prenom')}</h1>", unsafe_allow_html=True)

        # --- 1. ZONE DE PUBLICATION ---
        with st.container():
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### ✍️ Quoi de neuf dans la communauté ?")
            
            with st.form("form_post", clear_on_submit=True):
                contenu = st.text_area("Exprimez-vous...", placeholder=f"Partagez quelque chose, {u.get('prenom')}...")
                media_post = st.file_uploader("Ajouter une image ou vidéo", type=['jpg', 'png', 'mp4'])
                
                if st.form_submit_button("Publier"):
                    if contenu or media_post:
                        m_url, m_type = process_media(media_post)
                        new_post = {
                            "user_id": u['id'],
                            "auteur_nom": f"{u.get('prenom')} {u.get('nom')}",
                            "auteur_photo": u.get("photo_url"),
                            "contenu": contenu,
                            "media_url": m_url,
                            "media_type": m_type,
                            "date_pub": datetime.now().isoformat(),
                            "likes": 0
                        }
                        try:
                            supabase.table("posts").insert(new_post).execute()
                            st.success("Publication partagée !")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erreur : Vérifiez la table 'posts' sur Supabase. {e}")
                    else:
                        st.warning("Le message est vide !")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # --- 2. FIL D'ACTUALITÉ ---
        st.markdown("### 📰 Fil d'actualité")
        try:
            res_posts = supabase.table("posts").select("*").order("date_pub", desc=True).limit(10).execute()
            if res_posts.data:
                for post in res_posts.data:
                    with st.container():
                        avatar_p = post.get("auteur_photo") or "https://www.w3schools.com/howto/img_avatar.png"
                        st.markdown(f"""
                        <div class="glass-card" style="border-left: 4px solid #D4AF37;">
                            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                <img src="{avatar_p}" style="width:45px; height:45px; border-radius:50%; margin-right:12px; object-fit:cover; border:1px solid #D4AF37;">
                                <div>
                                    <b style="color:#D4AF37;">{post.get('auteur_nom', 'Membre')}</b><br>
                                    <small style="color:#888;">{post.get('date_pub', '')[:10]}</small>
                                </div>
                            </div>
                            <p style="font-size:1.1em;">{post.get('contenu', '')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if post.get("media_url"):
                            if post.get("media_type") == "image":
                                st.image(post["media_url"], use_container_width=True)
                            elif post.get("media_type") == "video":
                                st.video(post["media_url"])
                        st.write("") 
            else:
                st.info("Aucun message pour le moment.")
        except Exception:
            st.info("Le fil d'actualité sera activé après création de la table 'posts'.")

    elif menu == "💳 Cotisations":
        st.markdown("<h2 class='gold-text'>Cotisations</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Payer", "Historique"])
        with t1:
            with st.form("pay"):
                m = st.number_input("Montant GNF", value=5000)
                f = st.file_uploader("Preuve (Image)", type=['jpg', 'png'])
                if st.form_submit_button("Valider"):
                    img_url, _ = process_media(f)
                    supabase.table("cotisations").insert({
                        "user_id": u['id'], 
                        "montant": m, 
                        "preuve_url": img_url, 
                        "statut": "en_attente", 
                        "date_paiement": date.today().isoformat()
                    }).execute()
                    st.success("Soumission enregistrée.")
        with t2:
            hist = supabase.table("cotisations").select("*").eq("user_id", u['id']).execute()
            if hist.data: st.dataframe(hist.data)

    elif menu == "🪪 Carte de Membre":
        st.markdown("<h2 class='gold-text'>Ma Carte AEEMG</h2>", unsafe_allow_html=True)
        img_c = u.get("photo_url") or "https://www.w3schools.com/howto/img_avatar.png"
        card = f"""
        <div class="member-card">
            <div style="text-align:center">
                <img src="{img_c}" style="width:100px; height:100px; border-radius:50%; border:2px solid #D4AF37; object-fit: cover;">
                <h3 style="margin:10px 0;">{u.get('prenom')} {u.get('nom')}</h3>
                <span style="color:#D4AF37; letter-spacing:2px; font-size:12px;">MEMBRE OFFICIEL</span>
            </div>
            <div style="margin-top:20px; font-size:14px; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                <p><b>ID :</b> #AE-{u.get('id')}</p>
                <p><b>Organe :</b> {u.get('organe_base')}</p>
                <p><b>Ville :</b> {u.get('ville')}</p>
            </div>
        </div>
        """
        st.markdown(card, unsafe_allow_html=True)

    elif menu == "🚪 Déconnexion":
        st.session_state.clear()
        st.rerun()

else:
    st.warning("Veuillez vous connecter pour accéder à cette page.")
