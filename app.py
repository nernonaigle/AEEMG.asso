import streamlit as st
from supabase import create_client
import hashlib

# 1. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- FONCTION DE SÉCURITÉ ---
def hasher_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- 🎨 DESIGN MODERNE (CSS) ---
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

st.markdown("""
<style>
    /* Chargement d'une police moderne */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Fond d'écran avec overlay sombre */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
        url("https://images.unsplash.com/photo-1518005020250-6eb5f3f2754d?q=80&w=2000") no-repeat center center fixed;
        background-size: cover !important;
    }

    /* Effet de verre (Glassmorphism) pour les cartes */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
        color: white;
    }

    /* Style des boutons */
    .stButton>button {
        border-radius: 12px !important;
        background-color: #2D6A4F !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #40916C !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }

    /* Cacher le menu Streamlit pour faire plus "App" */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 2. Gestion de Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    st.write("---")
    if not st.session_state.connecte:
        menu = st.radio("Navigation", ["🔑 Connexion", "📝 Inscription"])
    else:
        st.markdown(f"🟢 **{st.session_state.user_info['prenom']}** (Membre)")
        options = ["🏠 Tableau de Bord", "💳 Cotisations", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"]
        if st.session_state.user_info['email'] == "nernonedouard99@gmail.com":
            options.insert(4, "🛠️ Admin") 
        menu = st.radio("Menu Principal", options)

# --- CONTENU DES PAGES ---

if menu == "📝 Inscription":
    st.markdown("<h1 style='color: white;'>✨ Créer un compte</h1>", unsafe_allow_html=True)
    with st.container():
        col1, _ = st.columns([1.5, 2])
        with col1:
            with st.form("inscription"):
                nom = st.text_input("Nom")
                prenom = st.text_input("Prénom")
                email = st.text_input("Email")
                pwd = st.text_input("Mot de passe", type="password")
                if st.form_submit_button("S'inscrire maintenant"):
                    supabase.table("membres").insert({
                        "nom": nom, "prenom": prenom, "email": email, 
                        "password": hasher_password(pwd), "cotisation": False
                    }).execute()
                    st.success("Bienvenue ! Connectez-vous maintenant.")

elif menu == "🔑 Connexion":
    st.markdown("<h1 style='text-align: center; color: white;'>🔑 Connexion</h1>", unsafe_allow_html=True)
    _, cent, _ = st.columns([1, 1.2, 1])
    with cent:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        e_l = st.text_input("Email")
        p_l = st.text_input("Mot de passe", type="password")
        if st.button("Entrer dans l'espace membre"):
            res = supabase.table("membres").select("*").eq("email", e_l).eq("password", hasher_password(p_l)).execute()
            if res.data:
                st.session_state.connecte, st.session_state.user_info = True, res.data[0]
                st.rerun()
            else:
                st.error("Identifiants incorrects")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏠 Tableau de Bord":
    if st.session_state.connecte:
        u = st.session_state.user_info
        
        # Header Profil
        st.markdown(f"""
            <div style='text-align: center; padding: 30px;'>
                <img src='https://api.dicebear.com/7.x/avataaars/svg?seed={u['nom']}' style='border-radius: 50%; width: 150px; background: white; padding: 5px; border: 4px solid #D4AF37;'>
                <h1 style='color: white; margin-bottom: 0;'>{u['prenom']} {u['nom']}</h1>
                <p style='color: #D4AF37; font-size: 1.2em;'>{u.get('bio', 'Membre Officiel AEEMG')}</p>
            </div>
        """, unsafe_allow_html=True)

        # Grille d'informations
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown(f"""<div class="glass-card">
                <h3 style='margin-top:0'>📍 Localisation</h3>
                <p>{u.get('ville', 'Non définie')}</p>
                <h3 style='margin-top:10px'>📧 Contact</h3>
                <p>{u['email']}</p>
            </div>""", unsafe_allow_html=True)

        with c2:
            status_color = "#2D6A4F" if u.get('cotisation') else "#941B0C"
            status_text = "À JOUR" if u.get('cotisation') else "NON RÉGLÉE"
            st.markdown(f"""<div class="glass-card" style="text-align:center;">
                <h3>💎 Statut Cotisation</h3>
                <div style="background:{status_color}; padding: 10px; border-radius: 10px; font-weight: bold;">
                    {status_text}
                </div>
                <p style="margin-top:15px; font-size: 0.8em;">ID Membre: #00{u.get('id', '0')}</p>
            </div>""", unsafe_allow_html=True)

        with c3:
            st.markdown("""<div class="glass-card">
                <h3 style='margin-top:0'>📢 Dernière Annonce</h3>
            """, unsafe_allow_html=True)
            try:
                res_ann = supabase.table("annonces").select("*").order("date", desc=True).limit(1).execute()
                if res_ann.data:
                    ann = res_ann.data[0]
                    st.write(ann['message'])
                else:
                    st.write("Aucune annonce pour le moment.")
            except:
                st.write("Annonces en cours...")
            st.markdown("</div>", unsafe_allow_html=True)

        # Formulaire de mise à jour caché dans un expander stylisé
        with st.expander("👤 Modifier mon profil"):
            with st.form("update_profil"):
                col_a, col_b = st.columns(2)
                new_tel = col_a.text_input("Téléphone", value=u.get('telephone', ''))
                new_ville = col_b.text_input("Ville", value=u.get('ville', ''))
                new_bio = st.text_area("Ma Bio", value=u.get('bio', ''))
                if st.form_submit_button("Mettre à jour mon profil"):
                    supabase.table("membres").update({"telephone": new_tel, "ville": new_ville, "bio": new_bio}).eq("email", u['email']).execute()
                    st.success("Profil actualisé ! Reconnectez-vous.")
    else:
        st.warning("Veuillez vous connecter.")

elif menu == "💳 Cotisations":
    if st.session_state.connecte:
        st.markdown("<h1 style='color: white;'>💳 Paiement de la Cotisation</h1>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""<div class="glass-card">
                <h3>Détails du paiement</h3>
                <p>Montant annuel : <b>50 000 GNF</b></p>
                <p>Votre contribution aide l'AEEMG à organiser des événements et soutenir les étudiants.</p>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            mode = st.selectbox("Méthode", ["Orange Money", "Moov Money"])
            trans_id = st.text_input("ID de la Transaction")
            if st.button("Envoyer la preuve de paiement"):
                if trans_id:
                    supabase.table("paiements").insert({"email": st.session_state.user_info['email'], "transaction_id": trans_id, "mode": mode, "statut": "en attente"}).execute()
                    st.success("Reçu envoyé ! Un admin va valider cela sous peu.")
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📸 Galerie":
    st.markdown("<h1 style='color: white;'>📸 Galerie Photo</h1>", unsafe_allow_html=True)
    # Simulation d'une galerie moderne
    photos = [
        "https://images.unsplash.com/photo-1523240715632-d984bb4b9749",
        "https://images.unsplash.com/photo-1542810634-71277d95dcbb",
        "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846",
        "https://images.unsplash.com/photo-1519074069444-1ba4fff66d16"
    ]
    cols = st.columns(2)
    for i, url in enumerate(photos):
        with cols[i % 2]:
            st.markdown(f'<div class="glass-card"><img src="{url}" style="width:100%; border-radius:10px;"></div>', unsafe_allow_html=True)

elif menu == "🛠️ Admin":
    if st.session_state.connecte and st.session_state.user_info['email'] == "nernonedouard99@gmail.com":
        st.title("🛠️ Administration")
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        tab_p, tab_m, tab_a = st.tabs(["💰 Paiements", "👥 Membres", "📢 Annonces"])
        
        with tab_p:
            res = supabase.table("paiements").select("*").eq("statut", "en attente").execute()
            if not res.data: st.info("Tout est à jour !")
            for p in res.data:
                col_p1, col_p2 = st.columns([3,1])
                col_p1.write(f"Paiement de : {p['email']} (ID: {p['transaction_id']})")
                if col_p2.button("Valider", key=f"val_{p['id']}"):
                    supabase.table("paiements").update({"statut": "validé"}).eq("id", p['id']).execute()
                    supabase.table("membres").update({"cotisation": True}).eq("email", p['email']).execute()
                    st.rerun()

        with tab_m:
            sq = st.text_input("Rechercher un membre").lower()
            m_res = supabase.table("membres").select("*").execute()
            for m in m_res.data:
                if sq in m['nom'].lower() or sq in m['email'].lower():
                    st.write(f"👤 {m['prenom']} {m['nom']} - {m['email']} - {'✅' if m['cotisation'] else '❌'}")

        with tab_a:
            with st.form("ann"):
                msg = st.text_area("Nouveau message")
                if st.form_submit_button("Diffuser"):
                    supabase.table("annonces").insert({"message": msg, "important": False}).execute()
                    st.success("Diffusé !")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🚪 Déconnexion":
    st.session_state.connecte = False
    st.session_state.user_info = None
    st.rerun()
