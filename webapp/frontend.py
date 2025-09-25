from datetime import date, timedelta

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


TOOL_TYPE_OPTIONS = ["Hand Tool", "Power Tool", "Pneumatic Tool", "Other"]


def _execute_supabase(builder, default=None):
    """Execute a Supabase query builder, returning (data, error_message)."""

    try:
        response = builder().execute()
    except Exception as exc:  # pragma: no cover - defensive guard for network errors
        return default, str(exc)
    data = getattr(response, "data", None)
    error = getattr(response, "error", None)
    if error:
        message = getattr(error, "message", None) if hasattr(error, "message") else None
        code = getattr(error, "code", None) if hasattr(error, "code") else None
        if isinstance(error, dict):
            message = error.get("message") or message
            code = error.get("code") or code
        if code == "PGRST205":
            message = "Supabase table not found. Ensure the required tables (e.g., 'tools', 'reservations') exist."  # noqa: E501
        if not message:
            message = str(error)
        return default, message
    if isinstance(data, list):
        return data, None
    return data if data is not None else default, None


def _refresh_user_tools(user_id: str | None):
    if not user_id:
        st.session_state["user_tools"] = []
        return None
    data, error = _execute_supabase(
        lambda: backend_K.supabase.table("tools").select("*").eq("owner_id", user_id).order("created_at", desc=True),
        default=[],
    )
    st.session_state["user_tools"] = data or []
    return error


def _add_tool(owner_id: str | None, name: str, desc: str, tool_type: str):
    if not owner_id:
        return "Please sign in before posting a tool."
    payload = {
        "owner_id": owner_id,
        "name": name,
        "description": desc,
        "tool_type": tool_type,
    }
    _, error = _execute_supabase(lambda: backend_K.supabase.table("tools").insert(payload), default=[])
    return error


def _delete_tool(owner_id: str | None, tool_id):
    if not owner_id:
        return "Please sign in before deleting a tool."
    reservations, res_error = _execute_supabase(
        lambda: backend_K.supabase.table("reservations").select("id").eq("tool_id", tool_id).limit(1),
        default=[],
    )
    if res_error:
        return f"Unable to verify reservations for this tool: {res_error}"
    if reservations:
        return "This tool still has reservation records. Please cancel them before deleting the tool."
    _, error = _execute_supabase(
        lambda: backend_K.supabase.table("tools").delete().eq("id", tool_id).eq("owner_id", owner_id),
        default=[],
    )
    return error


def _search_tools(name: str | None, tool_type: str | None):
    def builder():
        query = backend_K.supabase.table("tools").select("*").order("created_at", desc=True)
        if name:
            query = query.ilike("name", f"%{name}%")
        if tool_type and tool_type != "All":
            query = query.eq("tool_type", tool_type)
        return query

    return _execute_supabase(builder, default=[])


def _fetch_available_tools(limit: int = 20):
    return _execute_supabase(
        lambda: backend_K.supabase.table("tools").select("*").order("created_at", desc=True).limit(limit),
        default=[],
    )


def _fetch_user_reservations(user_id: str | None):
    if not user_id:
        return [], "Please sign in to view reservations."
    return _execute_supabase(
        lambda: backend_K.supabase.table("reservations").select("*").eq("borrower_id", user_id).order("start_date", desc=True),
        default=[],
    )


def _fetch_owner_reservations(owner_id: str | None):
    if not owner_id:
        return [], "Please sign in to view requests."
    tools = st.session_state.get("user_tools", [])
    tool_ids = [tool.get("id") for tool in tools if tool.get("id")]
    if not tool_ids:
        return [], None
    return _execute_supabase(
        lambda: backend_K.supabase.table("reservations").select("*").in_("tool_id", tool_ids).order("start_date", desc=True),
        default=[],
    )


def _cancel_reservation(reservation_id: str | None, borrower_id: str | None):
    if not reservation_id or not borrower_id:
        return "Missing reservation or borrower information."
    _, error = _execute_supabase(
        lambda: backend_K.supabase.table("reservations").update({"status": "cancelled_by_borrower"}).eq("id", reservation_id).eq("borrower_id", borrower_id),
        default=[],
    )
    return error


def _owner_update_reservation(reservation_id: str | None, tool_id: str | None, status: str):
    if not reservation_id or not tool_id:
        return "Missing reservation or tool information."
    owned_ids = {tool.get("id") for tool in st.session_state.get("user_tools", []) if tool.get("id")}
    if tool_id not in owned_ids:
        return "You can only update reservations for your own tools."
    _, error = _execute_supabase(
        lambda: backend_K.supabase.table("reservations").update({"status": status}).eq("id", reservation_id).eq("tool_id", tool_id),
        default=[],
    )
    return error


def _create_reservation(tool_id: str, borrower_id: str, tool_name: str, start_date: date, end_date: date, notes: str | None = None):
    payload = {
        "tool_id": tool_id,
        "borrower_id": borrower_id,
        "tool_name": tool_name,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "status": "requested",
    }
    if notes:
        payload["notes"] = notes
    _, error = _execute_supabase(lambda: backend_K.supabase.table("reservations").insert(payload), default=[])
    return error


if "supabase_health" not in st.session_state:
    st.session_state["supabase_health"] = _run_supabase_health_check()

if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

if "user_tools" not in st.session_state:
    st.session_state["user_tools"] = []

st.session_state.setdefault("reservations_cache", None)
st.session_state.setdefault("owner_reservations_cache", None)
st.session_state.setdefault("search_results", [])
st.session_state.setdefault("search_error", None)
st.session_state.setdefault("search_submitted", False)
st.session_state.setdefault("new_tool_name", "")
st.session_state.setdefault("new_tool_desc", "")
st.session_state.setdefault("new_tool_type", TOOL_TYPE_OPTIONS[0])
st.session_state.setdefault("selected_tool", None)
today = date.today()
st.session_state.setdefault("reservation_start_date", today)
st.session_state.setdefault("reservation_end_date", today + timedelta(days=3))
st.session_state.setdefault("reservation_notes", "")
st.session_state.setdefault("reset_tool_form", False)
st.session_state.setdefault("reset_reservation_form", False)
st.session_state.setdefault("reservation_flash", None)

if st.session_state.get("reset_tool_form"):
    st.session_state["new_tool_name"] = ""
    st.session_state["new_tool_desc"] = ""
    st.session_state["new_tool_type"] = TOOL_TYPE_OPTIONS[0]
    st.session_state["reset_tool_form"] = False

if st.session_state.get("reset_reservation_form"):
    st.session_state["reservation_start_date"] = date.today()
    st.session_state["reservation_end_date"] = date.today() + timedelta(days=3)
    st.session_state["reservation_notes"] = ""
    st.session_state["reset_reservation_form"] = False

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
                        user_id = getattr(user, "id", None) or (
                            user.get("id") if isinstance(user, dict) else None
                        )
                        st.session_state["current_user"] = {
                            "email": user_email,
                            "id": user_id,
                            "session": session,
                        }
                        st.session_state["user_tools"] = []
                        st.session_state["reservations_cache"] = None
                        st.session_state["owner_reservations_cache"] = None
                        st.session_state["search_results"] = []
                        st.session_state["search_error"] = None
                        st.session_state["search_submitted"] = False
                        st.session_state["selected_tool"] = None
                        st.session_state["reservation_flash"] = None
                        st.session_state["reset_reservation_form"] = True
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
                    st.session_state["user_tools"] = []
                    st.session_state["reservations_cache"] = None
                    st.session_state["owner_reservations_cache"] = None
                    st.session_state["search_results"] = []
                    st.session_state["search_error"] = None
                    st.session_state["search_submitted"] = False
                    st.session_state["selected_tool"] = None
                    st.session_state["reservation_flash"] = None
                    st.session_state["reset_reservation_form"] = True
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
        current_user = st.session_state.get("current_user") or {}
        user_id = current_user.get("id")
        if not user_id:
            st.info("Sign in to view and manage reservations.")
            return

        owned_tools_error = _refresh_user_tools(user_id)
        if owned_tools_error:
            st.warning(f"Unable to sync your tools: {owned_tools_error}")

        flash = st.session_state.get("reservation_flash")
        if isinstance(flash, dict) and flash.get("message" ):
            level = flash.get("type", "info")
            message = flash.get("message")
            if level == "success":
                st.success(message)
            elif level == "warning":
                st.warning(message)
            elif level == "error":
                st.error(message)
            else:
                st.info(message)
            st.session_state["reservation_flash"] = None

        st.subheader("Reserve a Tool")
        available_tools, avail_error = _fetch_available_tools(limit=25)
        if avail_error:
            st.warning(f"Unable to load tools for reservation: {avail_error}")
        else:
            tool_choices = [tool for tool in (available_tools or []) if tool.get("owner_id") != user_id]
            if not tool_choices:
                st.info("No tools available to reserve right now. Check back soon!")
            else:
                selected_tool = st.session_state.get("selected_tool")
                default_index = 0
                for idx, tool in enumerate(tool_choices):
                    if selected_tool and tool.get("id") == selected_tool.get("id"):
                        default_index = idx
                        break

                tool_index = st.selectbox(
                    "Choose a tool",
                    options=list(range(len(tool_choices))),
                    index=default_index,
                    format_func=lambda idx: f"{tool_choices[idx].get('name', 'Unnamed Tool')} ({tool_choices[idx].get('tool_type', 'Unknown')})",
                )
                chosen_tool = tool_choices[tool_index]
                st.session_state["selected_tool"] = chosen_tool

                start_date = st.date_input(
                    "Start date",
                    key="reservation_start_date",
                    value=st.session_state.get("reservation_start_date", date.today()),
                )
                end_date = st.date_input(
                    "End date",
                    key="reservation_end_date",
                    value=st.session_state.get("reservation_end_date", date.today() + timedelta(days=3)),
                )
                notes = st.text_area("Notes (optional)", key="reservation_notes")

                if st.button("Reserve Tool", key="reserve_tool_button"):
                    if start_date > end_date:
                        st.warning("End date must be on or after the start date.")
                    else:
                        tool_id = chosen_tool.get("id")
                        tool_name = chosen_tool.get("name", "Unnamed Tool")
                        error = _create_reservation(
                            tool_id=tool_id,
                            borrower_id=user_id,
                            tool_name=tool_name,
                            start_date=start_date,
                            end_date=end_date,
                            notes=notes.strip() or None,
                        )
                        if error:
                            st.error(f"Unable to create reservation: {error}")
                        else:
                            st.session_state["reservations_cache"] = None
                            st.session_state["owner_reservations_cache"] = None
                            st.session_state["selected_tool"] = None
                            st.session_state["reservation_flash"] = {
                                "type": "success",
                                "message": f"Reservation requested for {tool_name}.",
                            }
                            st.session_state["reset_reservation_form"] = True
                            st.rerun()

        st.divider()

        if st.button("Refresh Reservations", key="refresh_reservations"):
            st.session_state["reservations_cache"] = None

        cached = st.session_state.get("reservations_cache")
        if cached is None:
            data, error = _fetch_user_reservations(user_id)
            st.session_state["reservations_cache"] = {
                "data": data or [],
                "error": error,
            }
            cached = st.session_state["reservations_cache"]

        if cached.get("error"):
            st.warning(f"Unable to load reservations: {cached['error']}")
            return

        st.subheader("Your Reservation Requests")
        reservations_data = cached.get("data", [])
        if not reservations_data:
            st.info("No reservations yet.")
        else:
            for idx, reservation in enumerate(reservations_data, start=1):
                with st.expander(f"Reservation {idx}", expanded=False):
                    tool_name = reservation.get("tool_name") or reservation.get("tool_id") or "Unknown tool"
                    st.markdown(f"**Tool:** {tool_name}")
                    st.markdown(f"**Borrower:** {current_user.get('email', 'You')}")
                    start_date_val = reservation.get("start_date") or "Unknown"
                    end_date_val = reservation.get("end_date") or "Unknown"
                    st.markdown(f"**Start:** {start_date_val}")
                    st.markdown(f"**End:** {end_date_val}")
                    status_raw = reservation.get("status") or "Pending"
                    status_lower = status_raw.lower()
                    st.markdown(f"**Status:** {status_raw.title()}")
                    st.caption("Reservation metadata")
                    st.json(reservation)

                    res_id = reservation.get("id")
                    if res_id and status_lower not in {"cancelled", "cancelled_by_borrower", "declined"}:
                        if st.button("Cancel Reservation", key=f"cancel_res_{res_id}"):
                            error = _cancel_reservation(res_id, user_id)
                            if error:
                                st.error(f"Unable to cancel: {error}")
                            else:
                                st.session_state["reservation_flash"] = {
                                    "type": "info",
                                    "message": "Reservation cancelled.",
                                }
                                st.session_state["reservations_cache"] = None
                                st.session_state["owner_reservations_cache"] = None
                                st.rerun()

        st.subheader("Requests for Your Tools")
        owned_tools = st.session_state.get("user_tools", [])
        owned_tool_ids = [tool.get("id") for tool in owned_tools if tool.get("id")]
        if not owned_tool_ids:
            st.info("You haven't posted any tools yet, so there are no incoming requests.")
        else:
            if st.button("Refresh Incoming Requests", key="refresh_owner_requests"):
                st.session_state["owner_reservations_cache"] = None

            owner_cache = st.session_state.get("owner_reservations_cache")
            if owner_cache is None:
                data, error = _fetch_owner_reservations(user_id)
                st.session_state["owner_reservations_cache"] = {
                    "data": data or [],
                    "error": error,
                }
                owner_cache = st.session_state["owner_reservations_cache"]

            if owner_cache.get("error"):
                st.warning(f"Unable to load requests: {owner_cache['error']}")
            else:
                requests_data = owner_cache.get("data", [])
                if not requests_data:
                    st.info("No reservation requests for your tools yet.")
                else:
                    for idx, reservation in enumerate(requests_data, start=1):
                        tool_name = reservation.get("tool_name") or reservation.get("tool_id") or "Unknown tool"
                        borrower_label = reservation.get("borrower_email") or reservation.get("borrower_id") or "Unknown borrower"
                        with st.expander(f"Request {idx}: {tool_name}", expanded=False):
                            st.markdown(f"**Borrower:** {borrower_label}")
                            start_date_val = reservation.get("start_date") or "Unknown"
                            end_date_val = reservation.get("end_date") or "Unknown"
                            st.markdown(f"**Start:** {start_date_val}")
                            st.markdown(f"**End:** {end_date_val}")
                            status_raw = reservation.get("status") or "Pending"
                            status_lower = status_raw.lower()
                            st.markdown(f"**Status:** {status_raw.title()}")
                            st.caption("Reservation metadata")
                            st.json(reservation)
                            res_id = reservation.get("id")
                            tool_id = reservation.get("tool_id")
                            if res_id and status_lower in {"requested", "pending"}:
                                action_cols = st.columns(2)
                                with action_cols[0]:
                                    if st.button("Accept", key=f"accept_res_{res_id}"):
                                        error = _owner_update_reservation(res_id, tool_id, "accepted")
                                        if error:
                                            st.error(f"Unable to accept: {error}")
                                        else:
                                            st.session_state["reservation_flash"] = {
                                                "type": "success",
                                                "message": "Reservation accepted.",
                                            }
                                            st.session_state["owner_reservations_cache"] = None
                                            st.session_state["reservations_cache"] = None
                                            st.rerun()
                                with action_cols[1]:
                                    if st.button("Decline", key=f"decline_res_{res_id}"):
                                        error = _owner_update_reservation(res_id, tool_id, "declined")
                                        if error:
                                            st.error(f"Unable to decline: {error}")
                                        else:
                                            st.session_state["reservation_flash"] = {
                                                "type": "warning",
                                                "message": "Reservation declined.",
                                            }
                                            st.session_state["owner_reservations_cache"] = None
                                            st.session_state["reservations_cache"] = None
                                            st.rerun()
    reservations()

with tab4:

    # Post a New Tool
    st.subheader("Post a New Tool")
    current_user = st.session_state.get("current_user") or {}
    owner_id = current_user.get("id")
    if not owner_id:
        st.info("Sign in to add and manage your tools.")

    tool_name = st.text_input("Name", key="new_tool_name")
    tool_desc = st.text_area("Description", key="new_tool_desc")
    tool_type_choice = st.selectbox("Tool Type", TOOL_TYPE_OPTIONS, key="new_tool_type")

    if st.button("Add Tool to Profile"):
        if not owner_id:
            st.warning("Please sign in before posting a tool.")
        elif not tool_name.strip():
            st.warning("Please enter a tool name!")
        else:
            error = _add_tool(owner_id, tool_name.strip(), tool_desc.strip(), tool_type_choice)
            if error:
                st.error(f"Unable to add tool: {error}")
            else:
                st.success(f"'{tool_name}' posted successfully!")
                st.session_state["reset_tool_form"] = True
                st.session_state["owner_reservations_cache"] = None
                _refresh_user_tools(owner_id)
                st.rerun()

    st.markdown("---")

    # --- Display Tools in Grid Cards ---
    st.subheader("Your Profile")

    refresh_error = None
    if owner_id:
        refresh_error = _refresh_user_tools(owner_id)
    else:
        st.session_state["user_tools"] = []

    if refresh_error:
        st.warning(f"Unable to load your tools: {refresh_error}")

    tools = st.session_state.get("user_tools", [])

    if tools:
        cols = st.columns(2)
        for idx, tool in enumerate(tools):
            col = cols[idx % 2]
            with col:
                tool_name_display = tool.get("name", "Unnamed Tool")
                tool_desc_display = tool.get("description") or tool.get("desc") or "No description provided."
                tool_type_display = tool.get("tool_type", "Unknown")
                st.markdown(
                    f"""
                    <div style='
                        background-color:#f9f9f9;
                        padding:15px;
                        margin-bottom:10px;
                        border-radius:10px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    '>
                        <h4 style='margin:0'>{tool_name_display}</h4>
                        <p style='margin:0 0 8px 0;'>{tool_desc_display}</p>
                        <span style='font-size:12px;color:#555;'>Type: {tool_type_display}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                tool_id = tool.get("id", idx)
                if st.button("Delete", key=f"del_{tool_id}"):
                    error = _delete_tool(owner_id, tool_id)
                    if error:
                        st.error(f"Unable to delete tool: {error}")
                    else:
                        st.success("Tool removed from profile.")
                        _refresh_user_tools(owner_id)
                        st.session_state["owner_reservations_cache"] = None
    else:
        if owner_id:
            st.info("You haven't posted any tools yet!")
        else:
            st.info("Sign in to view stored tools.")

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
search_name = st.sidebar.text_input("Name", key="search_name")
search_type = st.sidebar.selectbox("Tool Type", ["All"] + TOOL_TYPE_OPTIONS, index=0, key="search_type")
if st.sidebar.button("Submit", key="search_submit"):
    filters_name = search_name.strip() or None
    selected_type = search_type if search_type != "All" else None
    results, error = _search_tools(filters_name, selected_type)
    st.session_state["search_results"] = results or []
    st.session_state["search_error"] = error
    st.session_state["search_submitted"] = True

search_error = st.session_state.get("search_error")
search_results = st.session_state.get("search_results", [])
search_submitted = st.session_state.get("search_submitted", False)

if search_error:
    st.sidebar.error(f"Search failed: {search_error}")
elif search_submitted:
    if search_results:
        st.sidebar.success(f"Found {len(search_results)} matching tool(s).")
        for tool in search_results[:10]:
            name = tool.get("name", "Unnamed Tool")
            tool_type_label = tool.get("tool_type", "Unknown")
            st.sidebar.markdown(f"**{name}** — {tool_type_label}")
            description = tool.get("description") or tool.get("desc")
            if description:
                preview = (description[:80] + "…") if len(description) > 80 else description
                st.sidebar.caption(preview)
    else:
        st.sidebar.info("No tools match the current filters.")


# Browse Tools Sidebar
def browse_tools():
    st.sidebar.header("Browse Available Tools")
    tools, error = _fetch_available_tools(limit=10)
    if error:
        st.sidebar.error(f"Unable to load tools: {error}")
        return
    if not tools:
        st.sidebar.info("No tools available right now. Check back soon!")
        return
    for tool in tools:
        name = tool.get("name", "Unnamed Tool")
        tool_type_label = tool.get("tool_type", "Unknown")
        st.sidebar.markdown(f"**{name}** — {tool_type_label}")
        description = tool.get("description") or tool.get("desc")
        if description:
            preview = (description[:75] + "…") if len(description) > 75 else description
            st.sidebar.caption(preview)
        tool_id = tool.get("id") or name
        if st.sidebar.button("Reserve", key=f"sidebar_reserve_{tool_id}"):
            st.session_state["selected_tool"] = tool
            st.session_state["reservation_flash"] = {
                "type": "info",
                "message": f"'{name}' selected. Complete the request on the Reservations tab.",
            }
            st.session_state["reset_reservation_form"] = True
            st.rerun()


browse_tools()

