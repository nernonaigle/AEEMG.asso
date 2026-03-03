import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime, date
import calendar
import base64
from io import BytesIO
from PIL import Image

# ==============================
# CONFIGURATION DE LA PAGE
# ==============================
st.set_page_config(
    page_title="AEEMG - Espace Membre",
    page_icon="🌙",
    layout="wide"
)

# ==============================
# CONNEXION SUPABASE
# ==============================
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# ==============================
# FONCTIONS
# ==============================
def hasher_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def check_cotisation_du_mois(user_id):
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
        return len(res.data) > 0
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

        return (
            f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}",
            "image",
        )

    return (
        f"data:{file.type};base64,{base64.b64encode(file.read()).decode()}",
        "video",
    )

# ==============================
# DESIGN
# ==============================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
html, body, [class*="st-"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, rgba(2,44,34,0.95), rgba(1,20,15,0.98)),
    url("https://images.unsplash.com/photo-1564115484-a4aaa88d5449?q=80&w=2000")
    no-repeat center center fixed;
    background-size: cover;
}
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(15px);
    border-radius: 15px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.1);
    color: white;
    margin-bottom: 15px;
}
.profile-img {
    width:110px;
    height:110px;
    border-radius:50%;
    object-fit:cover;
    border:3px solid #D4AF37;
}
.gold-text {
    color:#D4AF37;
    font-weight:800;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==============================
# SESSION
# ==============================
if "connecte" not in st.session_state:
    st.session_state.connecte = False
    st.session_state.user_info = None

# ==============================
# MENU SIDEBAR
# ==============================
with st.sidebar:
    st.markdown(
        "<h1 style='text-align:center;color:#D4AF37;'>🌙 AEEMG</h1>",
        unsafe_allow_html=True,
    )

    if st.session_state.connecte:
        u = st.session_state.user_info
        est_a_jour = check_cotisation_du_mois(u["id"])

        img = u.get("photo_url") or "https://www.w3schools.com/howto/img_avatar.png"
        st.image(img, width=70)
        st.markdown(f"**{u['prenom']}**")

        st.markdown("✅ À JOUR" if est_a_jour else "⚠️ À RÉGLER")

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

# ==============================
# CONNEXION
# ==============================
if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text'>Connexion</h2>", unsafe_allow_html=True)

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

        if res.data and res.data[0]["statut"] == "approuve":
            st.session_state.connecte = True
            st.session_state.user_info = res.data[0]
            st.rerun()
        else:
            st.error("Connexion impossible")

# ==============================
# DÉCONNEXION
# ==============================
elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()
