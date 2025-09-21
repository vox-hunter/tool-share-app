import streamlit as st
# Random Change
# --- Sidebar Navigation ---
menu = ["Browse Tools", "Add Tool", "Reservations", "Login/Signup"]
choice = st.sidebar.radio("Navigate", menu)

st.title("🛠️ ToolShare")
st.caption("Connected Worlds Hackathon 2025 — Team Project")

# --- Supabase Auth Placeholder ---
def supabase_auth():
	st.info("Login/Signup via Supabase (placeholder)")
	# TODO: Integrate Supabase auth
	st.text_input("Email")
	st.text_input("Password", type="password")
	st.button("Login")
	st.button("Sign Up")

# --- Browse Tools ---
def browse_tools():
	st.header("🔎 Browse Tools")
	# TODO: Fetch from Supabase
	sample_tools = [
		{"name": "Cordless Drill", "owner": "Alice", "available": True},
		{"name": "Lawn Mower", "owner": "Bob", "available": False},
		{"name": "Hammer", "owner": "Charlie", "available": True},
	]
	for tool in sample_tools:
		st.subheader(tool["name"])
		st.write(f"Owner: {tool['owner']}")
		status = "Available" if tool["available"] else "Reserved"
		st.write(f"Status: {status}")
		if tool["available"]:
			st.button(f"Reserve {tool['name']}")
		st.markdown("---")

# --- Add Tool ---
def add_tool():
	st.header("➕ Add a Tool")
	with st.form("add_tool_form"):
		name = st.text_input("Tool Name")
		desc = st.text_area("Description")
		submit = st.form_submit_button("Add Tool")
		if submit:
			# TODO: Add to Supabase
			st.success(f"Tool '{name}' added!")

# --- Reservations ---
def reservations():
	st.header("📅 Your Reservations")
	# TODO: Fetch user reservations from Supabase
	st.info("No reservations yet.")

# --- Main Routing ---
if choice == "Browse Tools":
	browse_tools()
elif choice == "Add Tool":
	add_tool()
elif choice == "Reservations":
	reservations()
elif choice == "Login/Signup":
	supabase_auth()
import streamlit as st
st.write("Automatic Refresh Test")