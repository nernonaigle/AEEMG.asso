import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime, date
import calendar
import time
import base64
from io import BytesIO
from PIL import Image

# 1. Configuration de la page avec ton logo personnalisé
# Nous utilisons ton code Base64 ici pour l'icône du navigateur
LOGO_BASE64 = "données:image/jpeg;base64,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 f9UZ2eob
# 2. Connexion Supabase
v_url = "https://ryfrekltrgaqyryzozhc.supabase.co"
v_key = "sb_publishable_iYEJIAz8ZK-fls3KMXI-pw_gcyinvF0"
supabase = create_client(v_url, v_key)

# --- FONCTIONS LOGIQUES ---
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

# --- 🎨 DESIGN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp {
        background: linear-gradient(135deg, rgba(2, 44, 34, 0.95) 0%, rgba(1, 20, 15, 0.98) 100%),
        url("https://images.unsplash.com/photo-1564115484-a4aaa88d5449?q=80&w=2000") no-repeat center center fixed;
        background-size: cover !important;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        margin-bottom: 15px;
    }
    .profile-img { width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 3px solid #D4AF37; margin-bottom: 10px; }
    .gold-text { color: #D4AF37; font-weight: 800; }
    .badge-paye { background: #10b981; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em; }
    .badge-impaye { background: #ef4444; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em; }
    
    .member-card {
        background: linear-gradient(145deg, #022c22 0%, #059669 100%);
        border: 2px solid #D4AF37;
        border-radius: 20px;
        padding: 25px;
        max-width: 350px;
        margin: 20px auto;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .card-photo { width: 120px; height: 120px; border-radius: 50%; border: 3px solid #D4AF37; object-fit: cover; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# 3. Session
if "connecte" not in st.session_state:
    st.session_state.connecte, st.session_state.user_info = False, None

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🌙 AEEMG</h1>", unsafe_allow_html=True)
    if st.session_state.connecte:
        u = st.session_state.user_info
        est_a_jour = check_cotisation_du_mois(u['id'])
        img_p = u.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
        st.markdown(f"<div style='text-align:center;'><img src='{img_p}' style='width:70px;height:70px;border-radius:50%;border:2px solid #D4AF37; object-fit: cover;'></div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:white; margin-bottom:0;'><b>{u['prenom']}</b></p>", unsafe_allow_html=True)
        status_html = "<span class='badge-paye'>✅ À JOUR</span>" if est_a_jour else "<span class='badge-impaye'>⚠️ À RÉGLER</span>"
        st.markdown(f"<div style='text-align:center;'>{status_html}</div>", unsafe_allow_html=True)
        menu = st.radio("Menu", ["🏠 Tableau de Bord", "💳 Cotisations", "🪪 Carte de Membre", "📂 Documents", "📸 Galerie", "🚪 Déconnexion"])
    else:
        menu = st.radio("Accès", ["🔑 Connexion", "📝 Inscription"])

# --- PAGES ---

if menu == "🔑 Connexion":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>Connexion</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
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

elif menu == "📝 Inscription":
    st.markdown("<h2 class='gold-text' style='text-align:center;'>Créer un compte</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("inscription_form"):
            nom = st.text_input("Nom")
            prenom = st.text_input("Prénom")
            email = st.text_input("Email")
            password = st.text_input("Mot de passe", type="password")
            organe = st.selectbox("Organe de base", ["Bureau National", "Section Universitaire", "Antenne Régionale"])
            if st.form_submit_button("Envoyer ma demande"):
                if nom and prenom and email and password:
                    data = {"nom": nom, "prenom": prenom, "email": email, "password": hasher_password(password), "organe_base": organe, "statut": "en_attente"}
                    supabase.table("membres").insert(data).execute()
                    st.success("✅ Demande envoyée ! Attendez la validation d'un administrateur.")
                else:
                    st.error("Veuillez remplir tous les champs.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🏠 Tableau de Bord" and st.session_state.connecte:
    u = st.session_state.user_info
    est_a_jour = check_cotisation_du_mois(u['id'])
    st.markdown(f"<h1 class='gold-text'>👋 Salam, {u['prenom']} !</h1>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 2.2])
    
    with col_left:
        st.markdown('<div class="glass-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown(f"<img src='{u.get('photo_url') or 'https://www.w3schools.com/howto/img_avatar.png'}' class='profile-img'>", unsafe_allow_html=True)
        st.write(f"**{u['prenom']} {u['nom']}**")
        st.markdown(f"Statut {datetime.now().strftime('%B')}: {'<b style=\"color:#10b981\">Payé</b>' if est_a_jour else '<b style=\"color:#ef4444\">Non payé</b>'}", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="glass-card"><small style="color:#D4AF37;">Organe de base</small><br><b>{u['organe_base']}</b><hr style="opacity:0.1"><small style="color:#D4AF37;">ID Membre</small><br><b>#AE-{u['id']}</b></div>""", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        txt = st.text_area("Quoi de neuf ?", placeholder="Partagez une info...", label_visibility="collapsed")
        media = st.file_uploader("Image/Vidéo", type=['jpg','png','mp4'], key="post_file")
        if st.button("🚀 Publier"):
            if txt or media:
                m_url, m_type = process_media(media)
                supabase.table("publications").insert({"auteur_nom": f"{u['prenom']} {u['nom']}", "auteur_photo": u.get('photo_url'), "contenu_texte": txt, "media_url": m_url, "media_type": m_type}).execute()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        posts = supabase.table("publications").select("*").order("created_at", desc=True).limit(10).execute()
        for p in posts.data:
            with st.container():
                st.markdown(f"""<div class="glass-card"><img src="{p['auteur_photo'] or 'https://www.w3schools.com/howto/img_avatar.png'}" style="width:35px;height:35px;border-radius:50%; vertical-align:middle; margin-right:10px;"><b>{p['auteur_nom']}</b> <small style="color:#888;">• {p['created_at'][:10]}</small><br><br>{p['contenu_texte']}</div>""", unsafe_allow_html=True)
                if p['media_url']:
                    if p['media_type']=="image": st.image(p['media_url'])
                    else: st.video(p['media_url'])
                
                # --- SYSTÈME DE LIKES CORRIGÉ ---
                likes_res = supabase.table("likes").select("id").eq("post_id", p['id']).execute()
                nb_likes = len(likes_res.data) if likes_res.data else 0
                
                c_lk, c_cm = st.columns([1, 5])
                with c_lk:
                    if st.button(f"❤️ {nb_likes}", key=f"lk_{p['id']}"):
                        check = supabase.table("likes").select("*").eq("post_id", p['id']).eq("user_id", u['id']).execute()
                        if check.data:
                            supabase.table("likes").delete().eq("post_id", p['id']).eq("user_id", u['id']).execute()
                        else:
                            supabase.table("likes").insert({"post_id": p['id'], "user_id": u['id']}).execute()
                        st.rerun()
                
                with c_cm:
                    with st.expander("💬 Commentaires"):
                        with st.form(key=f"f_cm_{p['id']}", clear_on_submit=True):
                            c_in = st.text_input("Ajouter un commentaire...", label_visibility="collapsed")
                            if st.form_submit_button("Envoyer"):
                                if c_in:
                                    supabase.table("commentaires").insert({"post_id": p['id'], "auteur_nom": f"{u['prenom']} {u['nom']}", "contenu": c_in}).execute()
                                    st.rerun()
                        comms = supabase.table("commentaires").select("*").eq("post_id", p['id']).order("created_at", desc=True).execute()
                        for c in comms.data:
                            st.markdown(f"<small><b>{c['auteur_nom']}</b>: {c['contenu']}</small>", unsafe_allow_html=True)
                st.markdown("---")

elif menu == "💳 Cotisations" and st.session_state.connecte:
    u = st.session_state.user_info
    st.markdown(f"<h1 class='gold-text'>💳 Cotisation de {datetime.now().strftime('%B %Y')}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("Montant : **10.000 GNF**")
        with st.form("pay"):
            tid = st.text_input("ID Transaction")
            file = st.file_uploader("Capture reçu", type=['jpg','png'])
            if st.form_submit_button("Déclarer le paiement"):
                if tid and file:
                    b64, _ = process_media(file, True)
                    supabase.table("cotisations").insert({"user_id": u['id'], "user_nom": u['prenom'], "transaction_id": tid, "preuve_image": b64, "statut": "en_attente"}).execute()
                    st.success("Reçu envoyé !")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("### Historique")
        hist = supabase.table("cotisations").select("*").eq("user_id", u['id']).order("date_paiement", desc=True).execute()
        for h in hist.data:
            st.write(f"📅 {h['date_paiement'][:10]} - {h['statut'].upper()}")

elif menu == "🪪 Carte de Membre" and st.session_state.connecte:
    u = st.session_state.user_info
    est_a_jour = check_cotisation_du_mois(u['id'])
    st.markdown("<h1 class='gold-text'>🪪 Carte de Membre Digitale</h1>", unsafe_allow_html=True)
    status_label = "MEMBRE ACTIF" if est_a_jour else "NON À JOUR"
    status_color = "#10b981" if est_a_jour else "#ef4444"
    photo = u.get('photo_url') or "https://www.w3schools.com/howto/img_avatar.png"
    st.markdown(f"""
    <div class="member-card">
        <div style="color: #D4AF37; font-weight: 800; margin-bottom: 15px;">AEEMG GUINÉE</div>
        <img src="{photo}" class="card-photo">
        <div style="font-size: 1.4em; font-weight: 700; color: white;">{u['prenom'].upper()} {u['nom'].upper()}</div>
        <div style="color: #D4AF37; font-size: 0.8em; margin-bottom: 15px;">ID: #AE-{u['id']} | {u['organe_base']}</div>
        <div style="background: {status_color}; color: white; padding: 5px 15px; border-radius: 20px; display: inline-block; font-size: 0.8em; font-weight: bold;">
            {status_label}
        </div>
    </div>
    """, unsafe_allow_html=True)

elif menu == "📂 Documents" and st.session_state.connecte:
    u = st.session_state.user_info
    st.markdown("<h1 class='gold-text'>📂 Bibliothèque Numérique</h1>", unsafe_allow_html=True)
    if u['email'] == "nernonaigle99@gmail.com":
        with st.expander("🛠️ Admin : Ajouter un document (PDF)"):
            with st.form("add_doc"):
                titre = st.text_input("Titre du document")
                cat = st.selectbox("Catégorie", ["Statuts", "Règlement", "PV de Réunion", "Formation"])
                f_doc = st.file_uploader("Fichier PDF", type=['pdf'])
                if st.form_submit_button("Mettre en ligne"):
                    if titre and f_doc:
                        b64_pdf = base64.b64encode(f_doc.read()).decode()
                        supabase.table("documents").insert({"titre": titre, "categorie": cat, "pdf_base64": b64_pdf}).execute()
                        st.success("Document ajouté !") ; st.rerun()
    docs = supabase.table("documents").select("*").order("created_at", desc=True).execute()
    for d in docs.data:
        st.markdown(f"""<div class="glass-card"><b>📄 {d['titre']}</b> ({d['categorie']})</div>""", unsafe_allow_html=True)
        st.download_button(label=f"📥 Télécharger", data=base64.b64decode(d['pdf_base64']), file_name=f"{d['titre']}.pdf", mime="application/pdf", key=d['id'])

elif menu == "📸 Galerie" and st.session_state.connecte:
    u = st.session_state.user_info
    st.markdown("<h1 class='gold-text'>📸 Médiathèque</h1>", unsafe_allow_html=True)
    if u['email'] == "nernonaigle99@gmail.com":
        with st.expander("🛠️ Admin : Ajouter des souvenirs"):
            with st.form("form_galerie"):
                nom_album = st.text_input("Nom de l'album")
                fichiers = st.file_uploader("Photos/Vidéos", type=['png','jpg','mp4'], accept_multiple_files=True)
                if st.form_submit_button("🚀 Publier"):
                    for f in fichiers:
                        b64, m_type = process_media(f)
                        supabase.table("galerie").insert({"titre_album": nom_album, "media_url": b64, "media_type": m_type, "auteur_nom": u['prenom']}).execute()
                    st.success("Ajouté !") ; st.rerun()
    res_gal = supabase.table("galerie").select("*").order("created_at", desc=True).execute()
    cols = st.columns(3)
    for idx, item in enumerate(res_gal.data):
        with cols[idx % 3]:
            if item['media_type'] == "video": st.video(item['media_url'])
            else: st.image(item['media_url'])
            st.caption(item['titre_album'])

elif menu == "🚪 Déconnexion":
    st.session_state.clear()
    st.rerun()
