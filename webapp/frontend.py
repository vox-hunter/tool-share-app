import streamlit as st

import backend_K
import backend_V as auth_backend


def _run_supabase_health_check():
    try:
        res = auth_backend.get_user()
        if res.get("error"):
            return {"ok": False, "message": res["error"]["message"]}
        return {"ok": True, "message": "Supabase reachable" if res.get("data") else "Connected (no active session)"}
    except Exception as exc:  # pragma: no cover - defensive guard for network errors
        return {"ok": False, "message": str(exc)}


if "supabase_health" not in st.session_state:
    st.session_state["supabase_health"] = _run_supabase_health_check()

if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

st.set_page_config(
    page_title="GearGrid-Tool Share",
)

st.write("# GearGrid") #name of the app

tab1, tab2, tab3, tab4 = st.tabs(["Home", "Account", "Reservations", "My Page"])

with tab1:
    st.header("About Us.")
    #About Us section
    st.write("""
    This website is designed to help facilitate the sharing of tools amongst community members.
    \nOur mission is to connect the community through a platform where you can **share, borrow**, or **rent** equipment,
    reducing waste, cutting costs and supporting local livelihoods.
    \nBy sharing resources, we can all contribute to a more sustainable community!
    """)
    
with tab2:

    col1, col2 = st.columns(2)

    # Login (Left Column)
    with col1:
        st.subheader("Login")
        st.info("Supabase email/password auth")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if not login_email or not login_password:
                st.warning("Please enter both email and password.")
            else:
                try:
                    response = backend_K.supabase.auth.sign_in_with_password({
                        "email": login_email,
                        "password": login_password,
                    })
                    user = getattr(response, "user", None)
                    session = getattr(response, "session", None)
                    if not user:
                        st.error("Login failed. Check credentials or verify your account.")
                    else:
                        user_email = getattr(user, "email", None) or (
                            user.get("email") if isinstance(user, dict) else None
                        )
                        st.session_state["current_user"] = {
                            "email": user_email,
                            "session": session,
                        }
                        st.session_state["supabase_health"] = _run_supabase_health_check()
                        st.success(f"Logged in as {user_email or 'current user'}")
                except Exception as exc:  # pragma: no cover - network/auth failure guard
                    st.error(f"Auth error: {exc}")

        if st.session_state.get("current_user"):
            st.caption(f"Current session: {st.session_state['current_user'].get('email', 'unknown')}")
            if st.button("Sign Out"):
                res = auth_backend.sign_out()
                if res.get("error"):
                    st.error(res["error"]["message"])
                else:
                    st.session_state["current_user"] = None
                    st.session_state["supabase_health"] = _run_supabase_health_check()
                    st.success("Signed out successfully.")

    # Sign Up (Right Column)
    with col2:
        st.subheader("Sign Up")
        if hasattr(st, "dialog"): #Check if dialog is supported
            @st.dialog("Sign Up")
            def show_signup_dialog():
                st.write("Please enter your details to sign up:")
                name = st.text_input("Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                phone = st.text_input("Phone Number")
                age = st.number_input("Age", min_value=13)
                if st.button("Submit", key="signup_submit"):
                    first_name, last_name = ("", "")
                    name_parts = name.strip().split(" ", 1)
                    if name_parts:
                        first_name = name_parts[0]
                        last_name = name_parts[1] if len(name_parts) > 1 else name_parts[0]
                    if not all([first_name, email, password, phone]):
                        st.warning("Please complete all fields before submitting.")
                    else:
                        result = auth_backend.sign_up_traditional(
                            email=email,
                            phone=phone,
                            password=password,
                            first_name=first_name,
                            last_name=last_name,
                            age=int(age),
                        )
                        if result.get("error"):
                            st.error(result["error"]["message"])
                        else:
                            st.success("Account created. Please verify your email and phone.")
                            st.session_state["supabase_health"] = _run_supabase_health_check()

            if st.button("Sign Up Form"):
                show_signup_dialog()

with tab3:
    def reservations():
        st.header("Your Reservations")
        # Placeholder: Fetch user reservations from Supabase
        st.info("No reservations yet.")
    reservations()

if "user_tools" not in st.session_state:
    st.session_state.user_tools = []

with tab4:

    # Post a New Tool
    st.subheader("Post a New Tool")
    tool_name = st.text_input("Name", key="new_tool_name")
    tool_desc = st.text_area("Description", key="new_tool_desc")

    if st.button("Add Tool to Profile"):
        if tool_name:
            st.session_state.user_tools.append({
                "name": tool_name,
                "desc": tool_desc
            })
            # TODO: Add to Supabase
            st.success(f"'{tool_name}' posted successfully!")
        else:
            st.warning("Please enter a tool name!")

    st.markdown("---")

    # --- Display Tools in Grid Cards ---
    st.subheader("Your Profile")

    tools = st.session_state.user_tools

    if tools:
        # Display 2 tools per row
        cols = st.columns(2)
        for idx, tool in enumerate(tools):
            col = cols[idx % 2] #Ensures two columns displayed
            with col:
                st.markdown(
                    f"""
                    <div style='
                        background-color:#f9f9f9;
                        padding:15px;
                        margin-bottom:10px;
                        border-radius:10px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    '>
                        <h4 style='margin:0'>{tool['name']}</h4>
                        <p>{tool['desc']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # Delete button
                if st.button("Delete", key=f"del_{idx}"):
                    st.session_state.user_tools.pop(idx)
    else:
        st.info("You haven't posted any tools yet!")

# Supabase health + Tool Search Sidebar
sidebar_status = st.session_state.get("supabase_health", {"ok": False, "message": "Unknown"})
if st.sidebar.button("Refresh Supabase Status"):
    st.session_state["supabase_health"] = _run_supabase_health_check()
    sidebar_status = st.session_state["supabase_health"]

if sidebar_status.get("ok"):
    st.sidebar.success(sidebar_status.get("message", "Supabase reachable"))
else:
    st.sidebar.error(sidebar_status.get("message", "Supabase not reachable"))

if st.session_state.get("current_user"):
    st.sidebar.caption(f"Authenticated as {st.session_state['current_user'].get('email', 'unknown')}")
else:
    st.sidebar.caption("Not signed in")

st.sidebar.header("Tool Search")
tool_name = st.sidebar.text_input("Name")
tool_type = st.sidebar.selectbox("Tool Type", ["Hand Tool", "Power Tool", "Pneumatic Tool"])
submit = st.sidebar.button("Submit")

# Browse Tools Sidebar
def browse_tools():
    st.sidebar.header("Browse Available Tools")
    # Placeholder: Fetch and display tools from Supabase
    st.sidebar.info("Tool browsing feature coming soon.")
browse_tools()

