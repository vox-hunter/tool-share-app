import streamlit as st

st.set_page_config(
    page_title="GearGrid-Tool Share",
)

st.write("# GearGrid") #name of the app

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Home", "Dashboard", "Login/Sign Up", "Add Tool", "Reservations"])

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
    st.header("My Tools Dashboard")
    st.write("See all tools posted by you.")
    
with tab3:
	st.header("Login/Sign Up")
	#Supabase Auth Placeholder
	def supabase_auth():
		st.info("Login/Signup via Supabase (placeholder)")
    	# TODO: Integrate Supabase auth
		st.text_input("Email")
		st.text_input("Password", type="password")
		st.button("Login")
		st.button("Sign Up", key="signup_button", help="Click to sign up", on_click=None, args=None, kwargs=None)
			
	supabase_auth()

with tab4:
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

with tab5:
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
