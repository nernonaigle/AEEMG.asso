import streamlit as st
from supabase import create_client
import hashlib
from datetime import datetime, date
import calendar
import time
import base64
from io import BytesIO
from PIL import Image

# 1. Configuration de la page
st.set_page_config(page_title="AEEMG - Espace Membre", page_icon="🌙", layout="wide")

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
        
        # Liste du menu
        menu_options = ["🏠 Tableau de Bord", "💳 Cotisations", "🪪 Carte de Membre", "📂 Documents", "📸 Galerie"]
        if u['email'] == "nernonaigle99@gmail.com":
            menu_options.append("🛡️ Admin Approbation")
        menu_options.append("🚪 Déconnexion")
        
        menu = st.radio("Menu", menu_options)
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
                    try:
                        supabase.table("membres").insert(data).execute()
                        st.success("✅ Demande envoyée ! Attendez la validation d'un administrateur.")
                    except Exception as e:
                        st.error("Erreur d'inscription. Vérifiez les politiques RLS de Supabase.")
                        st.expander("Voir l'erreur technique").code(str(e))
                else:
                    st.error("Veuillez remplir tous les champs.")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🛡️ Admin Approbation" and st.session_state.connecte:
    st.markdown("<h1 class='gold-text'>🛡️ Validation des Membres</h1>", unsafe_allow_html=True)
    res = supabase.table("membres").select("*").eq("statut", "en_attente").execute()
    if not res.data:
        st.info("Aucune demande en attente actuellement.")
    else:
        for m in res.data:
            with st.expander(f"Demande de : {m['prenom']} {m['nom']}"):
                st.write(f"📧 Email : {m['email']}")
                st.write(f"🏢 Organe : {m['organe_base']}")
                c1, c2 = st.columns(2)
                if c1.button("✅ Approuver", key=f"app_{m['id']}"):
                    supabase.table("membres").update({"statut": "approuve"}).eq("id", m['id']).execute()
                    st.success(f"Membre {m['prenom']} approuvé !")
                    st.rerun()
                if c2.button("❌ Rejeter", key=f"rej_{m['id']}"):
                    supabase.table("membres").delete().eq("id", m['id']).execute()
                    st.warning("Demande supprimée.")
                    st.rerun()

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

# Les autres sections (Cotisations, Carte, etc.) restent identiques...
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
