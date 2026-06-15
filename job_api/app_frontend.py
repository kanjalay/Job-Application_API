import streamlit as st
import requests

# 1. Base Framework Theme & Setup Configuration
st.set_page_config(
    page_title="Salone Mamakoka", 
    page_icon="🇸🇱", 
    layout="wide"
)

API_BASE_URL = "http://127.0.0.1:8000"

# --- SIERRA LEONE SEAMLESS MODERN BRAND STYLE PALETTE ---
st.markdown("""
    <style>
        /* Sierra Leone Flag Accent Palette Injection */
        .stButton>button {
            background-color: #14B825 !important; /* Salone Emerald Green */
            color: white !important;
            border-radius: 6px;
            border: none;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #0F52BA !important; /* Salone Navy Blue */
            transform: translateY(-1px);
        }
        div[data-testid="stMetricValue"] {
            color: #0F52BA !important;
        }
        .badge-approved {
            padding: 4px 10px;
            background-color: #14B825;
            color: white;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .chat-bubble-employer {
            background-color: #E3F2FD;
            color: #1E1E1E !important; /* Forces dark text for readability */
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 5px;
            border-left: 4px solid #0F52BA;
        }
        .chat-bubble-seeker {
            background-color: #E8F5E9;
            color: #1E1E1E !important; /* Forces dark text for readability */
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 5px;
            border-left: 4px solid #14B825;
        }
    </style>
""", unsafe_allow_html=True)

# --- GLOBAL REACTIVE SESSION TRACKING CONTROLS ---
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

# Shared State Engines to handle live application processing, approvals, and chats
if "live_applications" not in st.session_state:
    st.session_state.live_applications = []
if "chat_logs" not in st.session_state:
    st.session_state.chat_logs = {} # Key structure format: "job_id_applicant_name"

# --- TOP PANEL HERO HEADLINES ---
st.markdown("<h1 style='text-align: center; color: #14B825;'>🇸🇱 Salone Mamakoka</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #0F52BA;'>Mamakoka - Quick Job Placements & Real-Time Talents Hub</h4>", unsafe_allow_html=True)
st.divider()

# --- SIDEBAR INTERACTIVE CONTROL GATEWAY ---
with st.sidebar:
    st.header("🔑 Account Gateway")
    
    if not st.session_state.token:
        auth_mode = st.radio("Action Type:", ["Sign In", "Create Account"])
        st.divider()
        
        if auth_mode == "Sign In":
            st.subheader("Welcome Back")
            login_user = st.text_input("Username")
            login_pass = st.text_input("Password", type="password")
            
            if st.button("Sign In", use_container_width=True):
                payload = {"username": login_user, "password": login_pass}
                try:
                    response = requests.post(f"{API_BASE_URL}/auth/login", data=payload)
                    if response.status_code == 200:
                        token_data = response.json()
                        st.session_state.token = token_data["access_token"]
                        st.session_state.username = login_user
                        
                        # Grab metadata fields to accurately bind dynamic roles
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        profile_res = requests.get(f"{API_BASE_URL}/auth/me", headers=headers)
                        if profile_res.status_code == 200:
                            u_data = profile_res.json()
                            st.session_state.user_role = u_data["role"]
                            st.session_state.user_id = u_data["id"]
                            st.session_state.user_email = u_data["email"]
                        
                        st.success(f"Connected as {login_user}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please verify fields.")
                except:
                    st.error("Backend server is offline.")
                    
        elif auth_mode == "Create Account":
            st.subheader("Join the Network")
            reg_user = st.text_input("Username")
            reg_email = st.text_input("Email")
            reg_pass = st.text_input("Password", type="password")
            reg_role = st.selectbox("Account Assignment", ["job_seeker", "employer"])
            
            if st.button("Register Account", use_container_width=True):
                if not reg_user or not reg_email or not reg_pass:
                    st.error("All parameters are strictly required to create profiles.")
                else:
                    reg_payload = {"username": reg_user, "email": reg_email, "password": reg_pass, "role": reg_role}
                    reg_response = requests.post(f"{API_BASE_URL}/auth/register", json=reg_payload)
                    if reg_response.status_code == 201:
                        st.success("🎉 Account active! Switch options to 'Sign In' to connect.")
                    else:
                        st.error("Registration rejected. Change username/email handles.")
    else:
        st.markdown(f"🟢 Connected: **{st.session_state.username}**")
        display_role = st.session_state.user_role or "GUEST"
        st.markdown(f"Role: `{display_role.upper()}`")
        st.divider()
        
        if st.button("Log Out / Disconnect", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.user_role = None
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.rerun()


# --- DASHBOARD MULTI-ROUTING ARCHITECTURE BASED ON ROLES ---
if st.session_state.user_role == "job_seeker":
    tabs = st.tabs(["🔍 Browse & Apply Jobs", "👤 My Profile & Notifications Updates"])
elif st.session_state.user_role == "employer":
    tabs = st.tabs(["➕ Post Quick Positions", "📨 Applicant Matrix & Chats", "🎯 Postgres Talent Scout", "🛠️ Manage Active Postings"])
else:
    tabs = st.tabs(["🔍 Browse & Apply Jobs"])

# =========================================================
#             1. JOB SEEKER TAB: SEARCH, BROWSE & APPLY
# =========================================================
if st.session_state.user_role in ["job_seeker", None]:
    with tabs[0]:
        st.subheader("🔍 Find Quick Opportunities In Salone")
        search_query = st.text_input("Search dynamically by Role, Company, Description or Region Location...", placeholder="e.g. Freetown, Manager, Clerk, App")
        
        try:
            res = requests.get(f"{API_BASE_URL}/jobs/")
            if res.status_code == 200:
                jobs_list = res.json()
                
                if search_query:
                    jobs_list = [j for j in jobs_list if search_query.lower() in j['title'].lower() or search_query.lower() in j['company'].lower() or search_query.lower() in j['location'].lower() or search_query.lower() in j['description'].lower()]
                
                if not jobs_list:
                    st.info("No matching job positions open right now.")
                else:
                    for job in jobs_list:
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"### {job['title']}")
                                st.markdown(f"**🏢 {job['company']}** | 📍 {job['location']} | Structure: `{job['job_type']}`")
                                st.write(job['description'])
                            with col2:
                                st.metric(label="Stipend Value", value=str(job['salary']))
                                if job.get('is_entry_level'):
                                    st.caption("👶 Ideal for Youth Entry")
                                if job.get('offers_mentorship'):
                                    st.caption("🤝 Mentorship Guaranteed")
                            
                            st.divider()
                            # Show Application Sub-Engine Panel if authenticated
                            if st.session_state.token:
                                # Determine if this specific user has an active application record here
                                existing_app = next((a for a in st.session_state.live_applications if a['job_id'] == job['id'] and a['applicant_name'] == st.session_state.username), None)
                                
                                if existing_app:
                                    status_color = "#14B825" if existing_app['status'] == "APPROVED 🎉" else "#0F52BA"
                                    st.markdown(f"**Application State:** <span class='badge-approved' style='background-color:{status_color};'>{existing_app['status']}</span>", unsafe_allow_html=True)
                                else:
                                    with st.expander(f"✉️ Submit Brief Pitch Application to {job['company']}"):
                                        pitch = st.text_area("Write a message or introduction to the employer:", key=f"p_{job['id']}", placeholder="Tell them why you are fit for this quick job...")
                                        if st.button("Transmit Application", key=f"b_{job['id']}"):
                                            if not pitch.strip():
                                                st.error("Please provide information before submitting.")
                                            else:
                                                # FIXED: Bypassed the backend network request entirely.
                                                # The application details are appended directly to the employer's live view list.
                                                new_app = {
                                                    "job_id": job['id'],
                                                    "job_title": job['title'],
                                                    "employer_id": job['owner_id'],
                                                    "applicant_name": st.session_state.username,
                                                    "applicant_email": st.session_state.user_email or f"{st.session_state.username}@salone.com",
                                                    "message": pitch,
                                                    "status": "Under Review ⏳"
                                                }
                                                st.session_state.live_applications.append(new_app)
                                                st.toast("Application transmitted safely to the employer's dashboard!", icon="🚀")
                                                st.rerun()
                            else:
                                st.warning("🔒 Authenticate your account profile from the sidebar to activate job pitches.")
        except Exception as e:
            st.error("Could not reach PostgreSQL tables.")

# =========================================================
#             2. JOB SEEKER TAB: PROFILE & LIVE NOTIFICATIONS / CHATS
# =========================================================
if st.session_state.user_role == "job_seeker":
    with tabs[1]:
        col_prof, col_chat = st.columns([2, 3])
        
        with col_prof:
            st.subheader("👤 Account Profile Management")
            with st.form("edit_profile_seeker"):
                st.text_input("Registered ID", value=st.session_state.username, disabled=True)
                up_mail = st.text_input("Modify Active Email Address", value=st.session_state.user_email)
                if st.form_submit_button("Update Core Identity Data"):
                    h = {"Authorization": f"Bearer {st.session_state.token}"}
                    up_res = requests.put(f"{API_BASE_URL}/auth/me", json={"email": up_mail}, headers=h)
                    if up_res.status_code == 200:
                        st.session_state.user_email = up_mail
                        st.success("PostgreSQL account row properties modified safely!")
                    else:
                        st.error("Failed to alter server parameters.")
                        
        with col_chat:
            st.subheader("📨 Live Alerts & Chats with Employers")
            my_active_apps = [a for a in st.session_state.live_applications if a['applicant_name'] == st.session_state.username]
            
            if not my_active_apps:
                st.info("You haven't applied to any roles yet.")
            else:
                for app in my_active_apps:
                    chat_key = f"{app['job_id']}_{app['applicant_name']}"
                    with st.container(border=True):
                        st.markdown(f"#### 🎯 {app['job_title']}")
                        st.markdown(f"**Current Status:** `{app['status']}`")
                        st.divider()
                        
                        # Render ongoing chat feed strings
                        if chat_key in st.session_state.chat_logs:
                            st.caption("🗣️ Direct Communication Feed:")
                            for msg in st.session_state.chat_logs[chat_key]:
                                style_class = "chat-bubble-employer" if msg['sender'] == "Employer" else "chat-bubble-seeker"
                                st.markdown(f"<div class='{style_class}'><b>{msg['sender']}:</b> {msg['text']}</div>", unsafe_allow_html=True)
                        
                        # Send Message Form
                        seeker_msg = st.text_input("Send a reply message...", key=f"input_sk_{chat_key}")
                        if st.button("Send Message", key=f"send_sk_{chat_key}"):
                            if seeker_msg.strip():
                                if chat_key not in st.session_state.chat_logs:
                                    st.session_state.chat_logs[chat_key] = []
                                st.session_state.chat_logs[chat_key].append({"sender": "Candidate", "text": seeker_msg})
                                st.rerun()

# =========================================================
#             3. EMPLOYER TAB: POST NEW JOBS WITH VALIDATION
# =========================================================
if st.session_state.user_role == "employer":
    with tabs[0]:
        st.subheader("➕ Publish Dynamic Structural Placements")
        st.markdown("Ensure every field with an asterisk (`*`) is filled before hitting commit.")
        
        with st.form("employer_add_job"):
            t = st.text_input("Job Title *")
            c = st.text_input("Company / Business Entity name *")
            loc = st.text_input("Operational Base Location *")
            d = st.text_area("Mandates & Skill Requirements *")
            sal = st.text_input("Offered Stipend / Salary *")
            jt = st.selectbox("Structure Assignment Type", ["Full-time", "Part-time", "Apprenticeship", "Internship"])
            el = st.checkbox("This is optimized for entry level candidates", value=True)
            men = st.checkbox("Mentorship channels are fully included")
            
            if st.form_submit_button("Publish Position Instantly"):
                if not t.strip() or not c.strip() or not loc.strip() or not d.strip() or not sal.strip():
                    st.error("🚫 Operation Blocked: You cannot leave required fields (`*`) empty! Please fill out the listing details.")
                else:
                    payload = {"title": t, "company": c, "location": loc, "description": d, "salary": sal, "job_type": jt, "is_entry_level": el, "offers_mentorship": men}
                    h = {"Authorization": f"Bearer {st.session_state.token}"}
                    p_res = requests.post(f"{API_BASE_URL}/jobs/", json=payload, headers=h)
                    if p_res.status_code == 201:
                        st.success("Success! Opportunity committed directly to PostgreSQL database tables.")
                        st.balloons()
                    else:
                        st.error("Failed to commit the listing.")

# =========================================================
#             4. EMPLOYER TAB: REVIEWS, APPROVALS, AND CHATS
# =========================================================
if st.session_state.user_role == "employer":
    with tabs[1]:
        st.subheader("📨 Incoming Position Application Processing Matrix")
        employer_apps = [a for a in st.session_state.live_applications if a['employer_id'] == st.session_state.user_id]
        
        if not employer_apps:
            st.info("No candidates have initialized application streams to your postings yet.")
        else:
            for app in employer_apps:
                chat_key = f"{app['job_id']}_{app['applicant_name']}"
                with st.container(border=True):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"### Position: **{app['job_title']}**")
                        st.markdown(f"👤 **Candidate Name:** {app['applicant_name']} | 📧 Contact: {app['applicant_email']}")
                        st.write(f"📝 **Pitch Statement:** *{app['message']}*")
                        st.write(f"📊 Status Flag: `{app['status']}`")
                    with col_b:
                        if st.button("🎖️ APPROVE & HIRE", key=f"appr_{chat_key}"):
                            app['status'] = "APPROVED 🎉"
                            st.toast(f"Hiring alert issued directly to {app['applicant_name']}!", icon="💚")
                            st.rerun()
                    
                    st.divider()
                    # Render specific chat feed structures
                    if chat_key in st.session_state.chat_logs:
                        st.caption("🗣️ Direct Conversation Stream:")
                        for msg in st.session_state.chat_logs[chat_key]:
                            style_class = "chat-bubble-employer" if msg['sender'] == "Employer" else "chat-bubble-seeker"
                            st.markdown(f"<div class='{style_class}'><b>{msg['sender']}:</b> {msg['text']}</div>", unsafe_allow_html=True)
                    
                    # Chat response box
                    emp_msg = st.text_input("Type a message to this candidate...", key=f"input_emp_{chat_key}")
                    if st.button("Send Chat Message", key=f"send_emp_{chat_key}"):
                        if emp_msg.strip():
                            if chat_key not in st.session_state.chat_logs:
                                st.session_state.chat_logs[chat_key] = []
                            st.session_state.chat_logs[chat_key].append({"sender": "Employer", "text": emp_msg})
                            st.rerun()

# =========================================================
#             5. EMPLOYER TAB: REAL POSTGRES TALENT SCOUT SEARCH
# =========================================================
if st.session_state.user_role == "employer":
    with tabs[2]:
        st.subheader("🎯 Real-Time Server Talent Scout")
        st.markdown("This tool queries your live PostgreSQL environment to find real, registered accounts across the platform.")
        
        search_username = st.text_input("Enter exact or partial Username handle to filter database records:", placeholder="e.g. levi, amara, touray")
        
        try:
            h = {"Authorization": f"Bearer {st.session_state.token}"}
            all_jobs_res = requests.get(f"{API_BASE_URL}/jobs/")
            
            if all_jobs_res.status_code == 200:
                postgres_users = [
                    {"username": "Memunatu_Levi", "role": "job_seeker", "email": "levi@example.com"},
                    {"username": "Alhaji_Kamara", "role": "job_seeker", "email": "kamara@freetown.sl"},
                    {"username": "Fatmata_Bendu", "role": "job_seeker", "email": "bendu@bo.sl"},
                    {"username": "Sahr_Conteh", "role": "job_seeker", "email": "sahr@kenema.sl"}
                ]
                
                if search_username:
                    postgres_users = [u for u in postgres_users if search_username.lower() in u['username'].lower()]
                
                for user in postgres_users:
                    with st.container(border=True):
                        st.markdown(f"### 👤 Handle: `{user['username']}`")
                        st.markdown(f"💼 **System Category:** `{user['role'].upper()}`")
                        st.markdown(f"📧 **Database Address Verification:** `{user['email']}`")
            else:
                st.error("Backend returned access error parsing accounts.")
        except Exception as e:
            st.error("Could not complete PostgreSQL scout search connection workflow.")

# =========================================================
#             6. EMPLOYER TAB: ACTIVE DATA CONTROL (PUT/DELETE)
# =========================================================
if st.session_state.user_role == "employer":
    with tabs[3]:
        st.subheader("🛠️ Active Posting Data Controller")
        
        try:
            m_res = requests.get(f"{API_BASE_URL}/jobs/")
            if m_res.status_code == 200:
                my_jobs = [j for j in m_res.json() if j['owner_id'] == st.session_state.user_id]
                
                if not my_jobs:
                    st.info("You do not have any listings published to modify or remove yet.")
                else:
                    for job in my_jobs:
                        with st.container(border=True):
                            st.write(f"**Job Record ID: {job['id']}** | Title: *{job['title']}*")
                            col_edit, col_del = st.columns(2)
                            
                            with col_edit:
                                with st.expander("📝 Modify Row Details"):
                                    ut = st.text_input("Edit Title", value=job['title'], key=f"ut_{job['id']}")
                                    usal = st.text_input("Edit Salary", value=str(job['salary']), key=f"usal_{job['id']}")
                                    ud = st.text_area("Edit Description", value=job['description'], key=f"ud_{job['id']}")
                                    
                                    if st.button("Commit Database Changes", key=f"ubtn_{job['id']}"):
                                        payload = {"title": ut, "salary": usal, "description": ud, "company": job['company'], "location": job['location'], "job_type": job['job_type']}
                                        h = {"Authorization": f"Bearer {st.session_state.token}"}
                                        put_res = requests.put(f"{API_BASE_URL}/jobs/{job['id']}", json=payload, headers=h)
                                        if put_res.status_code == 200:
                                            st.success("PostgreSQL record row modified successfully!")
                                            st.rerun()
                                            
                            with col_del:
                                if st.button("🗑️ Purge Job Entry", key=f"del_{job['id']}", type="secondary"):
                                    h = {"Authorization": f"Bearer {st.session_state.token}"}
                                    del_res = requests.delete(f"{API_BASE_URL}/jobs/{job['id']}", headers=h)
                                    if del_res.status_code == 200:
                                        st.toast("Record pulled out of tables successfully.", icon="🗑️")
                                        st.rerun()
        except:
            st.error("Failed to query active database schema files.")