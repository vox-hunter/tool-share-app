import streamlit as st

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
        st.info("Login/Signup via Supabase (placeholder)")
        # TODO: Integrate Supabase auth here
        st.text_input("Email", key="login_email")
        st.text_input("Password", type="password", key="login_password")

        #To show that button pressed successfully
        if st.button("Login"):
            st.success("Logged in successfully!")

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
                if st.button("Submit"):
                    st.success(f"Thanks for signing up, {name}!")

            if st.button("Sign Up Form"):
                show_signup_dialog()

with tab3:
    def reservations():
        st.header("Your Reservations")
        # TODO: Fetch user reservations from Supabase
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

# Tool Search Sidebar
st.sidebar.header("Tool Search")
tool_name = st.sidebar.text_input("Name")
tool_type = st.sidebar.selectbox("Tool Type", ["Hand Tool", "Power Tool", "Pneumatic Tool"])
submit = st.sidebar.button("Submit")

# Browse Tools Sidebar
def browse_tools():
    st.sidebar.header("Browse Available Tools")
    # TODO: Fetch and display tools from Supabase
    st.sidebar.info("Tool browsing feature coming soon.")
browse_tools()

