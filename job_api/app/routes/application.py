from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# =========================================================
#                 USER / AUTHENTICATION SCHEMAS
# =========================================================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    # FIX HERE: Made Optional so it never triggers a validation block!
    created_at: Optional[datetime] = None 

    class Config:
        from_attributes = True


# =========================================================
#                   YOUTH JOB LISTING SCHEMAS
# =========================================================

class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary: str
    job_type: str 
    is_entry_level: bool = True
    offers_mentorship: bool = False

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    salary: str
    job_type: str
    is_entry_level: bool
    offers_mentorship: bool
    is_active: bool
    owner_id: int  
    # FIX HERE: Made Optional so it never triggers a validation block!
    created_at: Optional[datetime] = None 

    class Config:
        from_attributes = True




import streamlit as fancy_ui
import requests

# 1. Page Configuration Setup
fancy_ui.set_page_config(
    page_title="Youth Opportunity Hub", 
    page_icon="💼", 
    layout="wide"
)

API_BASE_URL = "http://127.0.0.1:8000"

# Initialize local session token state so the app remembers if you're logged in
if "token" not in fancy_ui.session_state:
    fancy_ui.session_state.token = None
if "username" not in fancy_ui.session_state:
    fancy_ui.session_state.username = None

# --- APP HEADER ---
fancy_ui.title("💼 Youth Job Opportunity Dashboard")
fancy_ui.markdown("Welcome to your launchpad for meaningful employment, internships, and mentorship!")
fancy_ui.divider()

# --- SIDEBAR CONTROL PANEL ---
# --- SIDEBAR CONTROL PANEL ---
with fancy_ui.sidebar:
    fancy_ui.header("🔑 Account Management")
    
    if not fancy_ui.session_state.token:
        # Toggle between Log In and Register modes
        auth_mode = fancy_ui.radio("Choose Action:", ["Sign In", "Create Account"])
        fancy_ui.divider()
        
        if auth_mode == "Sign In":
            fancy_ui.subheader("Sign In")
            login_user = fancy_ui.text_input("Username", placeholder="e.g. youth_candidate")
            login_pass = fancy_ui.text_input("Password", type="password")
            
            if fancy_ui.button("Sign In", use_container_width=True, type="primary"):
                payload = {"username": login_user, "password": login_pass}
                response = requests.post(f"{API_BASE_URL}/auth/login", data=payload)
                
                if response.status_code == 200:
                    token_data = response.json()
                    fancy_ui.session_state.token = token_data["access_token"]
                    fancy_ui.session_state.username = login_user
                    fancy_ui.success(f"Logged in as {login_user}!")
                    fancy_ui.rerun()
                else:
                    fancy_ui.error("Invalid credentials. Try again!")
                    
        elif auth_mode == "Create Account":
            fancy_ui.subheader("Register New Account")
            reg_user = fancy_ui.text_input("Choose Username", placeholder="e.g. memunatu_levi")
            reg_email = fancy_ui.text_input("Email Address", placeholder="e.g. dev@example.com")
            reg_pass = fancy_ui.text_input("Password", type="password", help="Make it secure!")
            reg_role = fancy_ui.selectbox("Who are you?", ["job_seeker", "employer"])
            
            if fancy_ui.button("Sign Up & Register", use_container_width=True, type="primary"):
                # Ensure fields aren't completely blank
                if not reg_user or not reg_email or not reg_pass:
                    fancy_ui.error("Please fill in all registration fields.")
                else:
                    # Match the exact schema layout your FastAPI backend expects (UserCreate)
                    reg_payload = {
                        "username": reg_user,
                        "email": reg_email,
                        "password": reg_pass,
                        "role": reg_role
                    }
                    
                    reg_response = requests.post(f"{API_BASE_URL}/auth/register", json=reg_payload)
                    
                    if reg_response.status_code == 201:
                        fancy_ui.success("🎉 Account created successfully! Switch to 'Sign In' to log in.")
                    else:
                        # Pull out detailed errors from your backend validations
                        try:
                            error_detail = reg_response.json().get('detail', 'Registration failed.')
                            fancy_ui.error(f"Error: {error_detail}")
                        except:
                            fancy_ui.error("Registration failed. Email might already be taken.")
    else:
        # Show logged-in profile status
        fancy_ui.success(f"Verified Active Session: **{fancy_ui.session_state.username}**")
        
        # Pull profile details dynamically from /auth/me
        headers = {"Authorization": f"Bearer {fancy_ui.session_state.token}"}
        profile_res = requests.get(f"{API_BASE_URL}/auth/me", headers=headers)
        if profile_res.status_code == 200:
            user_data = profile_res.json()
            fancy_ui.caption(f"📧 Email: {user_data['email']}")
            fancy_ui.caption(f"🎖️ Account Role: {user_data['role'].upper()}")

        if fancy_ui.button("Log Out", type="primary", use_container_width=True):
            fancy_ui.session_state.token = None
            fancy_ui.session_state.username = None
            fancy_ui.rerun()

# --- MAIN DASHBOARD INTERFACE ---
tab1, tab2 = fancy_ui.tabs(["🔍 Browse Jobs", "➕ Post New Opportunity"])

# --- TAB 1: BROWSE JOBS (PUBLIC READ) ---
# --- TAB 1: BROWSE JOBS (PUBLIC READ) ---
with tab1:
    fancy_ui.subheader("Available Opportunities")
    
    # 1. Fetch data directly from your backend endpoint
    try:
        res = requests.get(f"{API_BASE_URL}/jobs/")
        if res.status_code == 200:
            jobs_list = res.json()
            
            # Debugging tool: This prints the incoming database data to your Streamlit terminal console
            print("INCOMING JOBS FROM DATABASE:", jobs_list)
            
            if not jobs_list:
                fancy_ui.info("No job opportunities listed yet. Check back soon!")
            else:
                # 2. Iterate through every single job object returned by PostgreSQL
                for current_job in jobs_list:
                    # Create a clean visual container card
                    with fancy_ui.container(border=True):
                        col1, col2 = fancy_ui.columns([3, 1])
                        with col1:
                            fancy_ui.markdown(f"### {current_job.get('title', 'Untitled Position')}")
                            fancy_ui.markdown(f"**🏢 {current_job.get('company', 'Unknown Company')}** | 📍 {current_job.get('location', 'N/A')}")
                            fancy_ui.write(current_job.get('description', 'No description provided.'))
                        with col2:
                            fancy_ui.metric(label="Salary Offered", value=current_job.get('salary', 'Unspecified'))
                            fancy_ui.markdown(f"**Type:** `{current_job.get('job_type', 'Full-time')}`")
                            
                            # FIX: Added a unique string key using the job's database ID
                            if current_job.get('is_entry_level', True):
                               fancy_ui.pills(
                                   "Level", 
                                    ["👶 Entry Level"], 
                                    key=f"entry_pill_{current_job.get('id')}"
                                )
                            if current_job.get('offers_mentorship', False):
                                 fancy_ui.pills(
                                     "Support", 
                                     ["🤝 Mentorship Included"], 
                                     key=f"mentor_pill_{current_job.get('id')}"
                                )
        else:
            fancy_ui.error(f"Backend returned an error code: {res.status_code}")
    except Exception as e:
        fancy_ui.error(f"Frontend connection error: {e}")

# --- TAB 2: POST NEW OPPORTUNITY (SECURED CREATE) ---
with tab2:
    fancy_ui.subheader("Publish a New Opportunity")
    
    if not fancy_ui.session_state.token:
        fancy_ui.warning("🔒 You must log in via the sidebar on the left before you can publish a job post.")
    else:
        # Build out a clean job insertion form
        with fancy_ui.form("new_job_form"):
            new_title = fancy_ui.text_input("Job Title", placeholder="e.g. Junior Frontend Developer")
            new_company = fancy_ui.text_input("Company Name", placeholder="e.g. Tech For Good Initiatives")
            new_location = fancy_ui.text_input("Location", placeholder="e.g. Remote / Freetown")
            new_desc = fancy_ui.text_area("Detailed Description", placeholder="Describe the responsibilities, training, and qualifications...")
            new_salary = fancy_ui.text_input("Salary / Stipend", placeholder="e.g. Le 4,500 / month")
            new_type = fancy_ui.selectbox("Job Structure Type", ["Internship", "Apprenticeship", "Full-time", "Part-time"])
            
            is_entry = fancy_ui.checkbox("This is an entry-level youth position", value=True)
            has_mentor = fancy_ui.checkbox("This position includes a dedicated industry mentor")
            
            submitted = fancy_ui.form_submit_button("Publish Position to Hub", type="primary")
            
            if submitted:
                # Structure matching Pydantic JobCreate model schema
                job_json = {
                    "title": new_title,
                    "company": new_company,
                    "location": new_location,
                    "description": new_desc,
                    "salary": new_salary,
                    "job_type": new_type,
                    "is_entry_level": is_entry,
                    "offers_mentorship": has_mentor
                }
                
                # Append the authorization token header perfectly automatically
                sec_headers = {"Authorization": f"Bearer {fancy_ui.session_state.token}"}
                
                post_res = requests.post(f"{API_BASE_URL}/jobs/", json=job_json, headers=sec_headers)
                
                if post_res.status_code == 201:
                    fancy_ui.success("🚀 Success! Opportunity published instantly to the database.")
                    fancy_ui.balloons()  # Victory celebratory animation!
                else:
                    fancy_ui.error(f"Failed to publish post: {post_res.text}")


                    import streamlit as st
import requests

# 1. Page Branding Configuration
st.set_page_config(
    page_title="Salone Mamakoka", 
    page_icon="🇸🇱", 
    layout="wide"
)

API_BASE_URL = "http://127.0.0.1:8000"

# --- SIERRA LEONE THEMED CUSTOM UI/UX STYLING ---
# --- SIERRA LEONE THEMED CUSTOM UI/UX STYLING ---
st.markdown("""
    <style>
        /* CSS injection to handle custom Green, White, Blue style accents */
        .stButton>button {
            background-color: #14B825 !important; /* Salone Green */
            color: white !important;
            border-radius: 8px;
            border: none;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #0F52BA !important; /* Salone Blue Transition */
            color: white !important;
        }
        div[data-testid="stMetricValue"] {
            color: #0F52BA !important; /* Salone Blue for metrics */
        }
        .success-banner {
            padding: 10px;
            background-color: #14B825;
            color: white;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)  # <-- FIXED THIS PARAMETER NAME HERE!

# Initialize global tracking session state
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

# Application Mock State to preserve user/employer flow data (Applications & Candidate Pools)
if "mock_applications" not in st.session_state:
    st.session_state.mock_applications = []
if "mock_job_seekers" not in st.session_state:
    st.session_state.mock_job_seekers = [
        {"username": "Alhaji_Kamara", "skills": "Python, SQL, Fast API Backend", "location": "Freetown"},
        {"username": "Fatmata_Bendu", "skills": "Streamlit, UI/UX Design, Figma", "location": "Bo"},
        {"username": "Mohamed_Sillah", "skills": "Mobile App Engineering, HTML5", "location": "Kenema"}
    ]

# --- APP BANNER BRANDING ---
st.markdown("<h1 style='text-align: center; color: #14B825;'>🇸🇱 Salone Mamakoka</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #666;'>Mamakoka - Quick Job Opportunities for Sierra Leonean Youth</h4>", unsafe_allow_html=True)
st.divider()

# --- SIDEBAR CONTROL PANEL (AUTHENTICATION) ---
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
                response = requests.post(f"{API_BASE_URL}/auth/login", data=payload)
                
                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"]
                    st.session_state.username = login_user
                    
                    # Pull profile data to accurately store metadata inside session state
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    profile_res = requests.get(f"{API_BASE_URL}/auth/me", headers=headers)
                    if profile_res.status_code == 200:
                        u_data = profile_res.json()
                        st.session_state.user_role = u_data["role"]
                        st.session_state.user_id = u_data["id"]
                        st.session_state.user_email = u_data["email"]
                    
                    st.success(f"Welcome back, {login_user}!")
                    st.rerun()
                else:
                    st.error("Invalid details. Please try again.")
                    
        elif auth_mode == "Create Account":
            st.subheader("Join the Hub")
            reg_user = st.text_input("Username")
            reg_email = st.text_input("Email")
            reg_pass = st.text_input("Password", type="password")
            reg_role = st.selectbox("Account Type", ["job_seeker", "employer"])
            
            if st.button("Register Account", use_container_width=True):
                if not reg_user or not reg_email or not reg_pass:
                    st.error("Please provide all fields to setup your profile.")
                else:
                    reg_payload = {"username": reg_user, "email": reg_email, "password": reg_pass, "role": reg_role}
                    reg_response = requests.post(f"{API_BASE_URL}/auth/register", json=reg_payload)
                    if reg_response.status_code == 201:
                        st.success("🎉 Account active! Flip options to 'Sign In' to connect.")
                    else:
                        st.error("Registration failed. Please check your parameters or try a new username.")
    else:
        st.markdown(f"🟢 Active: **{st.session_state.username}**")
        st.markdown(f"Status: `{st.session_state.user_role.upper()}`")
        st.divider()
        
        if st.button("Disconnect / Log Out", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.user_role = None
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.rerun()

# --- MAIN ROLE-BASED DASHBOARD INTERFACE ---

# Layout configuration tracking: Define visible application hubs based on account types
if st.session_state.user_role == "job_seeker":
    tabs = st.tabs(["🔍 Browse & Apply Jobs", "👤 My Profile Workspace"])
elif st.session_state.user_role == "employer":
    tabs = st.tabs(["➕ Publish New Postings", "📨 Applicant Notifications", "🎯 Talent Scout Search", "🛠️ Manage My Job Listings"])
else:
    # Public standard view for anonymous guests
    tabs = st.tabs(["🔍 Browse & Apply Jobs"])

# =========================================================
#             JOB SEEKER HUB: BROWSE & APPLY
# =========================================================
if st.session_state.user_role in ["job_seeker", None]:
    with tabs[0]:
        st.subheader("🔍 Explore Available Postings")
        
        # Search Filtering Bar Engine
        search_query = st.text_input("Filter opportunities by title, tags, or company location:", placeholder="e.g. Frontend, Freetown, Intern")
        
        try:
            res = requests.get(f"{API_BASE_URL}/jobs/")
            if res.status_code == 200:
                jobs_list = res.json()
                
                # Filter rows reactively if search terms exist
                if search_query:
                    jobs_list = [j for j in jobs_list if search_query.lower() in j['title'].lower() or search_query.lower() in j['company'].lower() or search_query.lower() in j['location'].lower()]
                
                if not jobs_list:
                    st.info("No matching openings found right now.")
                else:
                    for current_job in jobs_list:
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"### {current_job['title']}")
                                st.markdown(f"**🏢 {current_job['company']}** | 📍 {current_job['location']}")
                                st.write(current_job['description'])
                            with col2:
                                st.metric(label="Salary / Stipend", value=current_job['salary'])
                                st.markdown(f"**Structure:** `{current_job['job_type']}`")
                                
                                if current_job.get('is_entry_level'):
                                    st.caption("👶 Entry Level Placement")
                                if current_job.get('offers_mentorship'):
                                    st.caption("🤝 Mentorship Included")
                            
                            # INTERACTIVE SUBMISSION APPLICATION INTERFACE
                            st.divider()
                            if st.session_state.token:
                                with st.expander(f"✉️ Submit Application for {current_job['title']}"):
                                    cover_msg = st.text_area("Write a message or introduction to the employer:", key=f"cover_{current_job['id']}", placeholder="Introduce yourself and list your contact details...")
                                    
                                    if st.button("Transmit Application Now", key=f"btn_app_{current_job['id']}"):
                                        if not cover_msg.strip():
                                            st.error("Please supply a cover statement for the employer before sending.")
                                        else:
                                            # Commit tracking payload packet to shared instance logs
                                            app_record = {
                                                "job_title": current_job['title'],
                                                "employer_id": current_job['owner_id'],
                                                "applicant_name": st.session_state.username,
                                                "applicant_email": st.session_state.user_email,
                                                "message": cover_msg
                                            }
                                            st.session_state.mock_applications.append(app_record)
                                            st.toast("Application transmitted safely to the employer!", icon="🚀")
                            else:
                                st.warning("🔒 You must secure an account connection from the sidebar control panel before you can apply.")
            else:
                st.error("Could not complete database reading.")
        except Exception as e:
            st.error("Database layer is offline or unreachable.")

# =========================================================
#             JOB SEEKER HUB: PROFILE ENGINE
# =========================================================
if st.session_state.user_role == "job_seeker":
    with tabs[1]:
        st.subheader("👤 My Profile Workspace")
        st.markdown("Review and keep your digital contact details updated securely below.")
        
        with st.form("profile_update_form"):
            st.text_input("My User Handle (Locked)", value=st.session_state.username, disabled=True)
            new_email = st.text_input("Modify Connected Email Address", value=st.session_state.user_email)
            
            save_profile = st.form_submit_button("Update My Account Details")
            if save_profile:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                profile_payload = {"email": new_email}
                
                up_res = requests.put(f"{API_BASE_URL}/auth/me", json=profile_payload, headers=headers)
                if up_res.status_code == 200:
                    st.session_state.user_email = new_email
                    st.success("Profile records refreshed instantly inside database schemas!")
                else:
                    st.error("Failed to update profile details.")

# =========================================================
#             EMPLOYER HUB: PUBLISH POSTINGS
# =========================================================
if st.session_state.user_role == "employer":
    with tabs[0]:
        st.subheader("➕ Publish a New Position")
        st.markdown("Fill in all parameters below to distribute structural youth openings.")
        
        with st.form("new_job_form"):
            new_title = st.text_input("Opportunity Title *", placeholder="e.g. Junior IT Clerk")
            new_company = st.text_input("Organization / Corporate Entity Name *", placeholder="e.g. Mamakoka Engineering")
            new_location = st.text_input("Geographic Placement / Location *", placeholder="e.g. Freetown, Western Area")
            new_desc = st.text_area("Detailed Description & Roles *", placeholder="Outline operational mandates...")
            new_salary = st.text_input("Monthly Stipend / Salary *", placeholder="e.g. Le 5,000")
            new_type = st.selectbox("Job Structure Type", ["Internship", "Apprenticeship", "Full-time", "Part-time"])
            
            is_entry = st.checkbox("This is an entry-level youth position", value=True)
            has_mentor = st.checkbox("This position includes industry mentoring support")
            
            submitted = st.form_submit_button("Publish Position to Hub")
            
            if submitted:
                # STRICT FORM BLANK VALUE VALIDATION
                if not new_title or not new_company or not new_location or not new_desc or not new_salary:
                    st.error("🚫 Operation Halted: Every parameter with an asterisk (*) is strictly required to post a job!")
                else:
                    job_json = {
                        "title": new_title, "company": new_company, "location": new_location,
                        "description": new_desc, "salary": new_salary, "job_type": new_type,
                        "is_entry_level": is_entry, "offers_mentorship": has_mentor
                    }
                    sec_headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    post_res = requests.post(f"{API_BASE_URL}/jobs/", json=job_json, headers=sec_headers)
                    
                    if post_res.status_code == 201:
                        st.success("🚀 Success! Opportunity published instantly to the database.")
                        st.balloons()
                    else:
                        st.error("Failed to publish post.")

# =========================================================
#             EMPLOYER HUB: APPLICANT NOTIFICATIONS
# =========================================================
if st.session_state.user_role == "employer":
    with tabs[1]:
        st.subheader("📨 Incoming Candidate Tracking Applications")
        
        # Filter simulated transmissions to isolate listings belonging to this user
        my_apps = [a for a in st.session_state.mock_applications if a['employer_id'] == st.session_state.user_id]
        
        if not my_apps:
            st.info("No job seekers have submitted application payloads for your positions yet.")
        else:
            for tracking_idx, app in enumerate(my_apps):
                with st.container(border=True):
                    st.markdown(f"#### 🎯 Position: {app['job_title']}")
                    st.markdown(f"**Applicant:** {app['applicant_name']} (📧 {app['applicant_email']})")
                    st.info(f"**Cover Message:** {app['message']}")

# =========================================================
#             EMPLOYER HUB: TALENT SCOUT SEARCH
# =========================================================
if st.session_state.user_role == "employer":
    with tabs[2]:
        st.subheader("🎯 Scout Qualified Candidates")
        search_seeker = st.text_input("Search profiles by location or specialized engineering skillset:", placeholder="e.g. Python, Bo, Design")
        
        pool = st.session_state.mock_job_seekers
        if search_seeker:
            pool = [p for p in pool if search_seeker.lower() in p['skills'].lower() or search_seeker.lower() in p['location'].lower()]
            
        for s in pool:
            with st.container(border=True):
                st.markdown(f"### 👤 Job Seeker: {s['username']}")
                st.markdown(f"📍 **Base Location:** {s['location']}")
                st.markdown(f"💪 **Core Skillsets:** `{s['skills']}`")

# =========================================================
#             EMPLOYER HUB: MANAGE ACTIVE POSTINGS
# =========================================================
if st.session_state.user_role == "employer":
    with tabs[3]:
        st.subheader("🛠️ Active Operational Job Inventory Manager")
        st.markdown("Update details or remove older records directly from PostgreSQL database records.")
        
        try:
            m_res = requests.get(f"{API_BASE_URL}/jobs/")
            if m_res.status_code == 200:
                # Isolate records that map back to this specific Employer ID
                my_jobs = [j for j in m_res.json() if j['owner_id'] == st.session_state.user_id]
                
                if not my_jobs:
                    st.info("You haven't published any listings to maintain yet.")
                else:
                    for target_job in my_jobs:
                        with st.container(border=True):
                            st.write(f"**Job Post ID: {target_job['id']}** | Title: *{target_job['title']}*")
                            
                            m_col1, m_col2 = st.columns(2)
                            
                            # MODIFICATION SUB-ENGINE FLOW
                            with m_col1:
                                with st.expander(f"📝 Modify Data Fields"):
                                    up_title = st.text_input("Title Update", value=target_job['title'], key=f"t_{target_job['id']}")
                                    up_sal = st.text_input("Salary Update", value=target_job['salary'], key=f"s_{target_job['id']}")
                                    up_desc = st.text_area("Description Update", value=target_job['description'], key=f"d_{target_job['id']}")
                                    
                                    if st.button("Commit Field Changes", key=f"ubtn_{target_job['id']}"):
                                        mod_payload = {
                                            "title": up_title, "salary": up_sal, "description": up_desc,
                                            "company": target_job['company'], "location": target_job['location'],
                                            "job_type": target_job['job_type']
                                        }
                                        h = {"Authorization": f"Bearer {st.session_state.token}"}
                                        put_res = requests.put(f"{API_BASE_URL}/jobs/{target_job['id']}", json=mod_payload, headers=h)
                                        if put_res.status_code == 200:
                                            st.success("FastAPI row fields altered successfully!")
                                            st.rerun()
                                            
                            # PURGE TRASH CAN DELETE FLOW ENGINE
                            with m_col2:
                                if st.button(f"🗑️ Purge & Delete Post", key=f"del_{target_job['id']}", type="secondary"):
                                    h = {"Authorization": f"Bearer {st.session_state.token}"}
                                    del_res = requests.delete(f"{API_BASE_URL}/jobs/{target_job['id']}", headers=h)
                                    if del_res.status_code == 200:
                                        st.toast("Record pulled out of database tables safely.", icon="🗑️")
                                        st.rerun()
        except Exception as e:
            st.error("Manager view could not contact database.")


            streamlit run app_frontend.py