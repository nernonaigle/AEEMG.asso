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
SUPABASE_URL = "https://ryfrekltrgaqyryzozhc.supabase.co"
SUPABASE_KEY = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# FONCTIONS UTILES
# =========================================================
def hasher_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_cotisation_du_mois(user_id: int) -> bool:
    today = date.today()
    first_day = today.replace(day=1).isoformat()
    last_day = today.replace(
        day=calendar.monthrange(today.year, today.month)[1]
    ).isoformat()
    try:
        res = (
            supabase.table("cotisations")
            .select("*")
            .eq("user_id", user_id)
            .eq("statut", "valide")
            .gte("date_paiement", first_day)
            .lte("date_paiement", last_day)
            .execute()
        )
        return bool(res.data)
    except Exception:
        return False


def process_media(file, is_profile=False):
    if file is None:
        return None, None

    file_type = file.type.split("/")[0]

    if file_type == "image":
        img = Image.open(file)
        size = (300, 300) if is_profile else (800, 800)
        img.thumbnail(size)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{encoded}", "image"

    encoded = base64.b64encode(file.read()).decode()
    return f"data:{file.type};base64,{encoded}", "video"

# =========================================================
# DESIGN / CSS
# =========================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

html, body, [class*="st-"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background:
    linear-gradient(135deg, rgba(2,44,34,0.95), rgba(1,20,15,0.98)),
    url("https://images.unsplash.com/photo-1564115484-a4aaa88d5449?q=80&w=2000")
    no-repeat center center fixed;
    background-size: cover !important;
}

.glass-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(15px);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.12);
    color: white;
    margin-bottom: 16px;
}

.gold-text {
    color: #D4AF37;
    font-weight: 800;
}

.profile-img {
    width: 110px;
    height: 110px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #D4AF37;
}

.badge-paye {
    background: #10b981;
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.8em;
}

.badge-impaye {
    background: #ef4444;
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.8em;
}
</style>
""",
    unsafe_allow_html=True
)

# =========================================================
# SESSION
# =========================================================
if "connecte" not in st.session_state:
    st.session_state.connecte = False
    st.session_state.user_info = None

# =========================================================
# SIDEBAR / NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown(
        "<h1 style='text-align:center;color:#D4AF37;'>🌙 AEEMG</h1>",
        unsafe_allow_html=True,
    )

    if st.session_state.connecte:
        u = st.session_state.user_info
        est_a_jour = check_cotisation_du_mois(u["id"])

        avatar = u.get("photo_url") or "https://www.w3schools.com/howto/img_avatar.png"
        st.image(avatar, width=80)
        st.markdown(f"<p style='text-align:center'><b>{u['prenom']}</b></p>", unsafe_allow_html=True)

        badge = "badge-paye" if est_a_jour else "badge-impaye"
        texte = "✅ À JOUR" if est_a_jour else "⚠️ À RÉGLER"
        st.markdown(f"<div class='{badge}' style='text-align:center'>{texte}</div>", unsafe_allow_html=True)

        menu = st.radio(
            "Menu",
            [
                "🏠 Tableau de Bord",
                "💳 Cotisations",
                "🪪 Carte de Membre",
                "📂 Documents",
                "📸 Galerie",
                "🚪 Déconnexion",
            ],
        )
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# =========================================================
# PAGE CONNEXION
# =========================================================
if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center'>Connexion</h2>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            res = (
                supabase.table("membres")
                .select("*")
                .eq("email", email)
                .eq("password", hasher_password(password))
                .execute()
            )

            if res.data:
                user = res.data[0]
                if user["statut"] == "approuve":
                    st.session_state.connecte = True
                    st.session_state.user_info = user
                    st.rerun()
                else:
                    st.warning("⏳ Compte en attente de validation")
            else:
                st.error("Identifiants incorrects")

        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# PAGE INSCRIPTION
# =========================================================
elif menu == "📝 Inscription":
    st.markdown("<h2 class='gold-text' style='text-align:center'>Créer un compte</h2>", unsafe_allow_html=True)

    with st.form("form_inscription"):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        email = st.text_input("Email")
        password = st.text_input("Mot de passe", type="password")
        ville = st.text_input("Ville")
        motivation = st.text_area("Pourquoi rejoindre l’AEEMG ?")
        organe = st.selectbox(
            "Organe de base",
            [
                "Bureau National",
                "Section Universitaire",
                "Section Scolaire",
                "Section Communale",
                "Antenne Régionale",
            ],
        )

        submit = st.form_submit_button("Envoyer ma demande")

        if submit:
            if not all([nom, prenom, email, password, ville, motivation]):
                st.error("⚠️ Tous les champs sont obligatoires")
            else:
                supabase.table("membres").insert(
                    {
                        "nom": nom,
                        "prenom": prenom,
                        "email": email,
                        "password": hasher_password(password),
                        "ville": ville,
                        "motivation": motivation,
                        "organe_base": organe,
                        "statut": "en_attente",
                    }
                ).execute()
                st.success("✅ Demande envoyée, en attente de validation")

# =========================================================
# TABLEAU DE BORD
# =========================================================
elif menu == "🏠 Tableau de Bord" and st.session_state.connecte:
    u = st.session_state.user_info
    st.markdown(f"<h1 class='gold-text'>👋 Salam {u['prenom']}</h1>", unsafe_allow_html=True)

# =========================================================
# DÉCONNEXION
# =========================================================
elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()
