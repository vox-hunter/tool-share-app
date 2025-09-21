import streamlit as st

st.set_page_config(
    page_title="GearGrid-Tool Share",
)

st.write("# GearGrid") #name of the app

st.sidebar.success("Home") #sidebar

import streamlit as st

# Sidebar input
tool_name = st.sidebar.text_input("Tool Name")
tool_type = st.sidebar.selectbox("Tool Type", ["Hand Tool", "Power Tool", "Pneumatic Tool"])
submit = st.sidebar.button("Submit")

#About Us section
st.markdown(
    """
This website is designed to help facilitate the sharing of tools amongst community members. 
\nOur mission is to connect the community through a platform where you can **share, borrow**, or **rent** equipment, reducing waste, cutting costs and supporting local livelihoods.
\nBy sharing resources, we can all contribute to a more sustainable community!
"""
)

st.write("__________________________________________________________________")

#Sidebar navigation
menu = ["Add Tool", "Reservations", "Login/Signup"]
choice = st.sidebar.radio("Navigate", menu)


#Supabase Auth Placeholder
def supabase_auth():
	st.info("Login/Signup via Supabase (placeholder)")
	# TODO: Integrate Supabase auth
	st.text_input("Email")
	st.text_input("Password", type="password")
	st.button("Login")
	st.markdown(
    """
    <style>
    .signup-button {
        background-color: #87CEEB; /* Sky Blue */
        border: none;
        color: black;
        padding: 5px 5px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    </style>
    <div class="signup-button">Sign Up</div>
    """,
    unsafe_allow_html=True
)

#Add Tool
def add_tool():
	st.header("Add a Tool")
	with st.form("add_tool_form"):
		name = st.text_input("Tool Name")
		desc = st.text_area("Description")
		submit = st.form_submit_button("Post Tool")
		if submit:
			# TODO: Add to Supabase
			st.success(f"'{name}' added to page!")

#Reservations
def reservations():
	st.header("Your Reservations")
	# TODO: Fetch user reservations from Supabase
	st.info("No reservations yet.")

# Main Routing
# Browse Tools
def browse_tools():
	st.header("Browse Tools")
	# TODO: Fetch and display tools from Supabase
	st.info("Tool browsing feature coming soon.")

if choice == "Browse Tools":
	browse_tools()
elif choice == "Add Tool":
	add_tool()
elif choice == "Reservations":
	reservations()
elif choice == "Login/Signup":
	supabase_auth()