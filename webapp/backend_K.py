import streamlit as st
from supabase import create_client, Client
from typing import Any, cast, Optional

@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()
_auth = cast(Any, supabase.auth)

