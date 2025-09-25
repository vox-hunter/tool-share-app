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

# --- User Authentication ---


# --- Tool CRUD ---
def add_tool(user_id: str, name: str, desc: str):
    data = {"user_id": user_id, "name": name, "desc": desc}
    response = supabase.table("tools").insert(data).execute()
    return response

def get_user_tools(user_id: str):
    response = supabase.table("tools").select("id, name, desc").eq("user_id", user_id).execute()
    return response.data if hasattr(response, 'data') else response

def delete_tool(tool_id: int, user_id: str):
    response = supabase.table("tools").delete().eq("id", tool_id).eq("user_id", user_id).execute()
    return response

# --- Browse Tools ---
def get_all_tools():
    response = supabase.table("tools").select("id, name, desc, user_id").execute()
    return response.data if hasattr(response, 'data') else response

# --- Advanced Tool Search ---
def search_tools(name: str = None, tool_type: str = None):
    query = supabase.table("tools").select("id, name, desc, user_id, type")
    if name:
        query = query.ilike("name", f"%{name}%")
    if tool_type:
        query = query.eq("type", tool_type)
    response = query.execute()
    return response.data if hasattr(response, 'data') else response

# --- Reservation System ---
def create_reservation(user_id: str, tool_id: int, start_date: str, end_date: str):
    data = {"user_id": user_id, "tool_id": tool_id, "start_date": start_date, "end_date": end_date}
    response = supabase.table("reservations").insert(data).execute()
    return response

def get_user_reservations(user_id: str):
    response = supabase.table("reservations").select("id, tool_id, start_date, end_date").eq("user_id", user_id).execute()
    return response.data if hasattr(response, 'data') else response

def delete_reservation(reservation_id: int, user_id: str):
    response = supabase.table("reservations").delete().eq("id", reservation_id).eq("user_id", user_id).execute()
    return response

