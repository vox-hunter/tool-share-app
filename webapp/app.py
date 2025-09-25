import streamlit as st
from supabase import create_client, Client
from typing import Any, cast, Optional

# --- Backend Functions (from backend_K.py) ---
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()
_auth = cast(Any, supabase.auth)

# --- Tool CRUD ---
def add_tool(user_id: str, name: str, desc: str, tool_type: str = "Hand Tool"):
    data = {"owner_id": user_id, "name": name, "description": desc}
    response = supabase.table("tools").insert(data).execute()
    return response

def get_user_tools(user_id: str):
    response = supabase.table("tools").select("id, name, description").eq("owner_id", user_id).execute()
    return response.data if hasattr(response, 'data') else response

def delete_tool(tool_id: int, user_id: str):
    response = supabase.table("tools").delete().eq("id", tool_id).eq("owner_id", user_id).execute()
    return response

# --- Browse Tools ---
def get_all_tools():
    response = supabase.table("tools").select("id, name, description, owner_id").execute()
    return response.data if hasattr(response, 'data') else response

# --- Advanced Tool Search ---
def search_tools(name: str = None, tool_type: str = None):
    query = supabase.table("tools").select("id, name, description, owner_id")
    if name:
        query = query.ilike("name", f"%{name}%")
    response = query.execute()
    return response.data if hasattr(response, 'data') else response

# --- Reservation System ---
def create_reservation(user_id: str, tool_id: int, start_date: str, end_date: str):
    data = {"borrower_id": user_id, "tool_id": tool_id, "start_date": start_date, "end_date": end_date}
    response = supabase.table("reservations").insert(data).execute()
    return response

def get_user_reservations(user_id: str):
    response = supabase.table("reservations").select("id, tool_id, start_date, end_date").eq("borrower_id", user_id).execute()
    return response.data if hasattr(response, 'data') else response

# Helper to get tool name by id
def get_tool_name(tool_id):
    response = supabase.table("tools").select("name").eq("id", tool_id).single().execute()
    if hasattr(response, 'data') and response.data:
        return response.data.get('name', str(tool_id))
    return str(tool_id)

def delete_reservation(reservation_id: int, user_id: str):
    response = supabase.table("reservations").delete().eq("id", reservation_id).eq("borrower_id", user_id).execute()
    return response

# --- Streamlit UI (from frontend.py, now using backend) ---
st.set_page_config(page_title="GearGrid-Tool Share")
st.write("# GearGrid")

tab1, tab2, tab3, tab4 = st.tabs(["Home", "Account", "Reservations", "My Page"])

with tab1:
    st.header("About Us.")
    st.write("""
    This website is designed to help facilitate the sharing of tools amongst community members.
    \nOur mission is to connect the community through a platform where you can **share, borrow**, or **rent** equipment,
    reducing waste, cutting costs and supporting local livelihoods.
    \nBy sharing resources, we can all contribute to a more sustainable community!
    """)

# --- Authentication State ---
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

with tab2:
    col1, col2 = st.columns(2)
    # Login (Left Column)
    with col1:
        st.subheader("Login")
        st.info("Login/Signup via Supabase (placeholder)")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                user = _auth.sign_in_with_password({"email": login_email, "password": login_password})
                if user.user:
                    st.session_state.user_id = user.user.id
                    st.session_state.user_email = login_email
                    st.success("Logged in successfully!")
                else:
                    st.error("Login failed: No user returned.")
            except Exception as e:
                st.error(f"Login failed: {e}")
    # Sign Up (Right Column)
    with col2:
        st.subheader("Sign Up")
        if hasattr(st, "dialog"):
            @st.dialog("Sign Up")
            def show_signup_dialog():
                st.write("Please enter your details to sign up:")
                name = st.text_input("Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                phone = st.text_input("Phone Number")
                age = st.number_input("Age", min_value=13)
                if st.button("Submit"):
                    try:
                        signup_response = _auth.sign_up({"email": email, "password": password})
                        if signup_response.user:
                            st.success(f"Thanks for signing up, {name}!")
                        else:
                            st.error("Signup failed: No user returned.")
                    except Exception as e:
                        st.error(f"Signup failed: {e}")
            if st.button("Sign Up Form"):
                show_signup_dialog()

with tab3:
    st.header("Your Reservations")
    if st.session_state.user_id:
        reservations = get_user_reservations(st.session_state.user_id)
        if reservations:
            for r in reservations:
                tool_name = get_tool_name(r['tool_id'])
                st.write(f"Tool: {tool_name}, Start: {r['start_date']}, End: {r['end_date']}")
                if st.button("Delete Reservation", key=f"delres_{r['id']}"):
                    delete_reservation(r['id'], st.session_state.user_id)
                    st.success("Reservation deleted.")
        else:
            st.info("No reservations yet.")
    else:
        st.info("Please log in to view reservations.")

with tab4:
    st.subheader("Post a New Tool")
    tool_name = st.text_input("Name", key="new_tool_name")
    tool_desc = st.text_area("Description", key="new_tool_desc")
    if st.button("Add Tool to Profile"):
        if tool_name and st.session_state.user_id:
            add_tool(st.session_state.user_id, tool_name, tool_desc)
            st.success(f"'{tool_name}' posted successfully!")
        elif not st.session_state.user_id:
            st.warning("Please log in to post a tool!")
        else:
            st.warning("Please enter a tool name!")
    st.markdown("---")
    st.subheader("Your Profile")
    if st.session_state.user_id:
        tools = get_user_tools(st.session_state.user_id)
        if tools:
            cols = st.columns(2)
            for idx, tool in enumerate(tools):
                col = cols[idx % 2]
                with col:
                    st.markdown(
                        f"""
                        <div style='background-color:#f9f9f9;padding:15px;margin-bottom:10px;border-radius:10px;box-shadow: 0 2px 5px rgba(0,0,0,0.1);'>
                            <h4 style='margin:0'>{tool['name']}</h4>
                            <p>{tool.get('description', '')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button("Delete", key=f"del_{tool['id']}"):
                        delete_tool(tool['id'], st.session_state.user_id)
                        st.success("Tool deleted.")
        else:
            st.info("You haven't posted any tools yet!")
    else:
        st.info("Please log in to view your profile.")

# --- Tool Search Sidebar ---
st.sidebar.header("Tool Search")
tool_name = st.sidebar.text_input("Name")
if st.sidebar.button("Submit"):
    results = search_tools(tool_name)
    if results:
        for tool in results:
            st.sidebar.write(f"{tool['name']}: {tool.get('description', '')}")
    else:
        st.sidebar.info("No tools found.")

# --- Browse Tools Sidebar ---
def browse_tools():
    st.sidebar.header("Browse Available Tools")
    tools = get_all_tools()
    if tools:
        for tool in tools:
            st.sidebar.write(f"{tool['name']}: {tool.get('description', '')}")
            if st.session_state.get('user_id'):
                with st.sidebar.form(key=f'reserve_form_{tool["id"]}'):
                    st.write("")  # For spacing
                    start_date = st.date_input("Start Date", key=f'start_{tool["id"]}')
                    end_date = st.date_input("End Date", key=f'end_{tool["id"]}')
                    reserve_btn = st.form_submit_button("Reserve")
                    if reserve_btn:
                        create_reservation(
                            st.session_state.user_id,
                            tool['id'],
                            str(start_date),
                            str(end_date)
                        )
                        st.success(f"Reserved '{tool['name']}' from {start_date} to {end_date}.")
            else:
                st.sidebar.info("Log in to reserve tools.")
    else:
        st.sidebar.info("No tools available.")
browse_tools()
