import streamlit as st

st.set_page_config(
    page_title="GearGrid-Tool Share",
)

st.write("# GearGrid") #name of the app

tab1, tab2, tab3, tab4 = st.tabs(["Home", "Account", "Add Tool", "Reservations"])

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

    # --- LOGIN (Left Column) ---
    with col1:
        st.subheader("Login")
        st.info("Login/Signup via Supabase (placeholder)")
        # TODO: Integrate Supabase auth here
        st.text_input("Email", key="login_email")
        st.text_input("Password", type="password", key="login_password")

        #To show that button pressed successfully
        if st.button("Login"):
            st.success("Logged in successfully!")

    # --- SIGN UP (Right Column) ---
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
    st.header("Add a Tool")
    def add_tool():
        with st.form("add_tool_form"):
            name = st.text_input("Tool Name")
            desc = st.text_area("Description")
            submit = st.form_submit_button("Post Tool")
            if submit:
                # TODO: Add to Supabase
                st.success(f"'{name}' added to page!")
    add_tool()

with tab4:
    def reservations():
        st.header("Your Reservations")
        # TODO: Fetch user reservations from Supabase
        st.info("No reservations yet.")
    reservations()

# Sidebar input
st.sidebar.header("Tool Search")
tool_name = st.sidebar.text_input("Name")
tool_type = st.sidebar.selectbox("Tool Type", ["Hand Tool", "Power Tool", "Pneumatic Tool"])
submit = st.sidebar.button("Submit")

# Main Routing
# Browse Tools
def browse_tools():
    st.sidebar.header("Browse Available Tools")
    # TODO: Fetch and display tools from Supabase
    st.sidebar.info("Tool browsing feature coming soon.")
browse_tools()
