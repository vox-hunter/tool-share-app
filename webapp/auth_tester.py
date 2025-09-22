import os
import sys
import streamlit as st

# Ensure we can import sibling backend file when running directly via Streamlit
CURRENT_DIR = os.path.dirname(__file__)
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

import backend_V as auth  # noqa: E402

st.set_page_config(page_title="Auth Tester", page_icon="🔐", layout="centered")

st.title("🔐 Supabase Auth Tester")
st.caption("Manual harness to exercise backend auth helpers")

# Display quick session status
col_a, col_b = st.columns(2)
with col_a:
    if st.button("Get Current User", use_container_width=True):
        res = auth.get_user()
        if res.get("error"):
            st.error(res["error"]["message"]) 
        else:
            st.success("Got user")
            st.json(res["data"])  # may be None when signed out
with col_b:
    if st.button("Sign Out", use_container_width=True):
        res = auth.sign_out()
        if res.get("error"):
            st.error(res["error"]["message"]) 
        else:
            st.success("Signed out")

st.divider()

# Tabs for flows
signup_tab, oauth_tab, completion_tab, phone_tab = st.tabs([
    "Traditional Signup",
    "OAuth",
    "Completion/Missing Fields",
    "Phone Verification",
])

# --- Traditional signup ---
with signup_tab:
    st.subheader("Create account (all fields required)")
    with st.form("signup_form"):
        c1, c2 = st.columns(2)
        with c1:
            first_name = st.text_input("First name", key="su_first")
            age = st.number_input("Age", min_value=0, step=1, key="su_age")
        with c2:
            last_name = st.text_input("Last name", key="su_last")
            phone = st.text_input("Phone (E.164)", placeholder="+15551234567", key="su_phone")
        email = st.text_input("Email", key="su_email")
        password = st.text_input("Password", type="password", key="su_pass")
        submitted = st.form_submit_button("Create Account")
    if submitted:
        res = auth.sign_up_traditional(
            email=email,
            phone=phone,
            password=password,
            first_name=first_name,
            last_name=last_name,
            age=int(age),
        )
        if res.get("error"):
            st.error(res["error"]["message"]) 
        else:
            st.success("Account created. Verify email and phone.")
            st.json(res["data"]) 

# --- OAuth ---
with oauth_tab:
    st.subheader("Start OAuth flow")
    provider = st.selectbox("Provider", ["google", "github", "discord", "facebook"], index=0)
    default_redirect = "http://localhost:8501"
    redirect_to = st.text_input("Redirect URL", value=default_redirect)
    if st.button("Get OAuth URL"):
        res = auth.sign_in_with_oauth(provider, redirect_to=redirect_to)
        if res.get("error"):
            st.error(res["error"]["message"]) 
        else:
            url = res["data"]["url"]
            if url:
                st.link_button("Open Provider Login", url)
            else:
                st.warning("No URL returned. Check provider settings and redirect URL.")

    st.markdown("---")
    st.subheader("Exchange code for session (PKCE)")
    qp = st.experimental_get_query_params()
    code_default = qp.get("code", [""])[0]
    code = st.text_input("Auth code (from redirect)", value=code_default)
    code_verifier = st.text_input("Code verifier (optional)", value="")
    redir_again = st.text_input("Redirect URL (optional)", value="")
    if st.button("Exchange Code"):
        res = auth.exchange_code_for_session(code, code_verifier or None, redir_again or None)
        if res.get("error"):
            st.error(res["error"]["message"]) 
        else:
            st.success("Exchanged code for session")
            st.json(res["data"]) 

# --- Completion / Missing Fields ---
with completion_tab:
    st.subheader("Check completion status")
    if st.button("Get Completion Status"):
        res = auth.get_completion_status()
        if res.get("error"):
            st.error(res["error"]["message"]) 
        else:
            st.json(res["data"]) 

    st.markdown("---")
    st.subheader("Update missing fields")
    with st.form("update_missing"):
        uf_first = st.text_input("First name")
        uf_last = st.text_input("Last name")
        uf_age_str = st.text_input("Age (integer)")
        save = st.form_submit_button("Save Profile")
    if save:
        uf_age = None
        if uf_age_str.strip():
            try:
                uf_age = int(uf_age_str)
            except ValueError:
                st.error("Age must be an integer")
                st.stop()
        res = auth.update_missing_fields(first_name=uf_first or None, last_name=uf_last or None, age=uf_age)
        if res.get("error"):
            st.error(res["error"]["message"]) 
        else:
            st.success("Profile updated")
            st.json(res["data"]) 

# --- Phone verification ---
with phone_tab:
    st.subheader("Request phone verification (send SMS)")
    rp_phone = st.text_input("Phone (E.164)", key="rp_phone")
    if st.button("Send SMS Code"):
        res = auth.request_phone_verification(rp_phone)
        if res.get("error"):
            st.error(res["error"]["message"]) 
        else:
            st.success("SMS sent (if provider configured)")
            st.json(res["data"]) 

    st.markdown("---")
    st.subheader("Verify SMS code")
    v_phone = st.text_input("Phone (E.164)", key="v_phone")
    v_code = st.text_input("SMS Code", key="v_code")
    if st.button("Verify Code"):
        res = auth.verify_phone_sms(v_phone, v_code)
        if res.get("error"):
            st.error(res["error"]["message"]) 
        else:
            st.success("Phone verified (session may refresh)")
            st.json(res["data"]) 
