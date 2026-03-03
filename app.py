import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime, date
import calendar
import base64
from io import BytesIO
from PIL import Image

# --- CONFIGURATION PAGE ---
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

# --- CONNEXION SUPABASE ---
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- FONCTIONS UTILES ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_cotisation_du_mois(user_id):
    today = date.today()
    first_day = today.replace(day=1).isoformat()
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1]).isoformat()
    try:
        res = supabase.table("cotisations").select("*").eq("user_id", user_id).eq("statut", "valide").gte("date_paiement", first_day).lte("date_paiement", last_day).execute()
        return len(res.data) > 0
    except:
        return False

def process_media(file, is_profile=False):
    if file is None: return None, None
    file_type = file.type.split('/')[0]
    if file_type == 'image':
        img = Image.open(file)
        size = (300, 300) if is_profile else (800, 800)
        img.thumbnail(size)
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}", "image"
    return f"data:{file.type};base64,{base64.b64encode(file.read()).decode()}", "video"

# --- DESIGN ---
VERT_FORET = "#0B3D0B"  # Couleur AEEMG vert forêt

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [class*="st-"] {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
.stApp {{ background: linear-gradient(135deg, rgba(2,44,34,0.95) 0%, rgba(1,20,15,0.98) 100%), url("https://images.unsplash.com/photo-1564115484-a4aaa88d5449?q=80&w=2000") no-repeat center center fixed; background-size: cover !important; }}
.glass-card {{ background: rgba(255,255,255,0.05); backdrop-filter: blur(15px); border-radius:15px; padding:20px; border:1px solid rgba(255,255,255,0.1); color:white; margin-bottom:15px; }}
.profile-img {{ width:110px; height:110px; border-radius:50%; object-fit:cover; border:3px solid {VERT_FORET}; margin-bottom:10px; }}
.vert-text {{ color:{VERT_FORET}; font-weight:800; }}
.badge-paye {{ background:#10b981; color:white; padding:3px 10px; border-radius:10px; font-size:0.8em; }}
.badge-impaye {{ background:#ef4444; color:white; padding:3px 10px; border-radius:10px; font-size:0.8em; }}
.member-card {{ background: linear-gradient(145deg, #022c22 0%, #059669 100%); border:2px solid {VERT_FORET}; border-radius:20px; padding:25px; max-width:350px; margin:20px auto; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.5); }}
.card-photo {{ width:120px; height:120px; border-radius:50%; border:3px solid {VERT_FORET}; object-fit:cover; margin-bottom:15px; }}
</style>
""", unsafe_allow_html=True)

# --- SESSION ---
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- SIDEBAR & NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h1 style='text-align:center; color:{VERT_FORET};'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        u = st.session_state.user_info
        est_a_jour = check_cotisation_du_mois(u['id'])
        img_p = u.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f"<div style='text-align:center;'><img src='{img_p}' style='width:70px;height:70px;border-radius:50%;border:2px solid {VERT_FORET}; object-fit: cover;'></div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:white; margin-bottom:0;'><b>{u['prenom']}</b></p>", unsafe_allow_html=True)
        status_html = "<span class='badge-paye'>✅ À JOUR</span>" if est_a_jour else "<span class='badge-impaye'>⚠️ À RÉGLER</span>"
        st.markdown(f"<div style='text-align:center;'>{status_html}</div>", unsafe_allow_html=True)
        menu_options = ["🏠 Tableau de Bord", "💳 Cotisations", "🪪 Carte de Membre", "📂 Documents", "📸 Galerie"]
        if u['email'] == "nernonaigle99@gmail.com":
            menu_options.append("🛡️ Admin Approbation")
        menu_options.append("🚪 Déconnexion")
        menu = st.radio("Menu", menu_options)
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# --- PAGES ---
# Connexion
if menu == "🔑 Connexion":
    st.markdown(f"<h2 class='vert-text' style='text-align:center;'>Connexion</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            res = supabase.table("membres").select("*").eq("email", email).eq("password", hasher_password(password)).execute()
            if res.data:
                user = res.data[0]
                if user.get('statut') == "approuve":
                    st.session_state.connecte = True
                    st.session_state.user_info = user
                    st.rerun()
                else:
                    st.warning("⏳ Votre compte est en attente de validation par un admin.")
            else:
                st.error("Identifiants incorrects.")
        st.markdown('</div>', unsafe_allow_html=True)

# Inscription
elif menu == "📝 Inscription":
    st.markdown(f"<h2 class='vert-text' style='text-align:center;'>Créer un compte</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("inscription_form"):
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            ville = st.text_input("Ville")
            motivation = st.text_area("Motivation (Pourquoi rejoindre l’AEEMG ?)")
            organe = st.selectbox("Organe", ["Bureau National","Section Universitaire","Antenne Régionale","Section Scolaire","Section Communale"])
            submitted = st.form_submit_button("Envoyer ma demande")
            if submitted:
                if nom and prenom and email and password and ville and motivation:
                    data = {
                        "nom": nom,
                        "prenom": prenom,
                        "email": email,
                        "password": hasher_password(password),
                        "ville": ville,
                        "motivation": motivation,
                        "organe_base": organe,
                        "statut": "en_attente"
                    }
                    try:
                        supabase.table("membres").insert(data).execute()
                        st.success("✅ Demande envoyée ! Attendez la validation d'un administrateur.")
                    except Exception as e:
                        st.error("Erreur lors de l'inscription.")
                        st.expander("Erreur technique").code(str(e))
                else:
                    st.error("⚠️ Tous les champs sont obligatoires.")
        st.markdown('</div>', unsafe_allow_html=True)

# Admin Approbation
elif menu == "🛡️ Admin Approbation" and st.session_state.connecte:
    st.markdown(f"<h1 class='vert-text'>🛡️ Validation des Membres</h1>", unsafe_allow_html=True)
    res = supabase.table("membres").select("*").eq("statut","en_attente").execute()
    if not res.data:
        st.info("Aucune demande en attente actuellement.")
    else:
        for m in res.data:
            with st.expander(f"Demande de : {m['prenom']} {m['nom']}"):
                st.write(f"📧 Email : {m['email']}")
                st.write(f"🏢 Organe : {m['organe_base']}")
                st.write(f"🏙️ Ville : {m.get('ville','Non renseignée')}")
                st.write(f"💡 Motivation : {m.get('motivation','Non renseignée')}")
                c1,c2 = st.columns(2)
                if c1.button("✅ Approuver", key=f"app_{m['id']}"):
                    supabase.table("membres").update({"statut":"approuve"}).eq("id",m['id']).execute()
                    st.success(f"Membre {m['prenom']} approuvé !")
                    st.rerun()
                if c2.button("❌ Rejeter", key=f"rej_{m['id']}"):
                    supabase.table("membres").delete().eq("id",m['id']).execute()
                    st.warning("Demande supprimée.")
                    st.rerun()

# Le code continue pour le tableau de bord, publications, cotisations, carte, documents, galerie, déconnexion
# ... (on remplace simplement toutes les couleurs dorées par VERT_FORET et toutes les sections restent identiques)
