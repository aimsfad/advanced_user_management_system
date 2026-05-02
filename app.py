from datetime import datetime, timezone
from typing import Dict, List

import pandas as pd
import streamlit as st

from database import SEARCHABLE_FIELDS, add_user, delete_user, get_all_users, search_users, update_user
from validation import validate_user

st.set_page_config(
    page_title="Advanced User Management System",
    page_icon="👤",
    layout="wide",
)

DISPLAY_COLUMNS = {
    "first_name": "First Name",
    "last_name": "Last Name",
    "birth_date": "Birth Date",
    "birth_place": "Birth Place",
    "phone_number": "Phone Number",
}


def normalize_user_input(data: Dict[str, str]) -> Dict[str, str]:
    return {
        "first_name": data["first_name"].strip(),
        "last_name": data["last_name"].strip(),
        "birth_date": data["birth_date"].strip(),
        "birth_place": data["birth_place"].strip(),
        "phone_number": data["phone_number"].strip(),
    }


def users_to_dataframe(users: List[Dict[str, str]]) -> pd.DataFrame:
    if not users:
        return pd.DataFrame(columns=list(DISPLAY_COLUMNS.values()))

    rows = []
    for user in users:
        rows.append({column_title: user.get(field, "") for field, column_title in DISPLAY_COLUMNS.items()})
    return pd.DataFrame(rows)


def user_label(user: Dict[str, str]) -> str:
    return f"{user.get('first_name', '')} {user.get('last_name', '')} - {user.get('phone_number', '')}"


def load_all_users() -> List[Dict[str, str]]:
    try:
        return get_all_users()
    except RuntimeError as exc:
        st.error(str(exc))
        return []


def render_user_table(users: List[Dict[str, str]], title: str = "Users") -> None:
    st.write(f"**{title}:** {len(users)} user(s)")
    st.dataframe(users_to_dataframe(users), use_container_width=True, hide_index=True)


def user_input_form(defaults: Dict[str, str], form_key: str, submit_label: str):
    with st.form(form_key, clear_on_submit=form_key == "add_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name", value=defaults.get("first_name", ""), key=f"{form_key}_first_name")
            birth_date = st.text_input(
                "Birth Date",
                value=defaults.get("birth_date", ""),
                placeholder="YYYY-MM-DD",
                key=f"{form_key}_birth_date",
            )
            phone_number = st.text_input(
                "Phone Number",
                value=defaults.get("phone_number", ""),
                placeholder="Example: +213555123456",
                key=f"{form_key}_phone_number",
            )
        with col2:
            last_name = st.text_input("Last Name", value=defaults.get("last_name", ""), key=f"{form_key}_last_name")
            birth_place = st.text_input("Birth Place", value=defaults.get("birth_place", ""), key=f"{form_key}_birth_place")

        submitted = st.form_submit_button(submit_label)

    user_data = normalize_user_input(
        {
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "birth_place": birth_place,
            "phone_number": phone_number,
        }
    )
    return submitted, user_data


st.title("Advanced User Management System")
st.caption("Python + Streamlit GUI + MongoDB NoSQL database")

with st.sidebar:
    st.header("Project Menu")
    st.write("Each feature is separated to make the CRUD operations clear.")
    st.info("Birth date format: YYYY-MM-DD")
    st.warning("Phone numbers are unique in MongoDB.")

add_tab, display_tab, search_tab, update_tab, delete_tab = st.tabs(
    ["➕ Add User", "📋 Display Users", "🔎 Search User", "✏️ Update User", "🗑️ Delete User"]
)

with add_tab:
    st.subheader("Add New User")
    submitted, user_data = user_input_form(defaults={}, form_key="add_user_form", submit_label="Save User")

    if submitted:
        is_valid, message = validate_user(user_data)
        if not is_valid:
            st.error(message)
        else:
            now = datetime.now(timezone.utc)
            user_data["created_at"] = now
            user_data["updated_at"] = now
            try:
                add_user(user_data)
                st.success("User added successfully.")
            except ValueError as exc:
                st.error(str(exc))
            except RuntimeError as exc:
                st.error(str(exc))

with display_tab:
    st.subheader("Display Users")
    st.write("This page fetches all users from MongoDB and displays them in a structured table.")
    users = load_all_users()
    render_user_table(users, title="Total users")

with search_tab:
    st.subheader("Search User")
    st.write("Choose the field, then type the search value. Phone number and birth date are searched exactly.")

    field_options = list(SEARCHABLE_FIELDS.keys())
    selected_field = st.selectbox(
        "Search field",
        options=field_options,
        format_func=lambda key: SEARCHABLE_FIELDS[key],
    )
    search_text = st.text_input(
        "Search value",
        placeholder="Example: Ahmed, Ali, 2002-05-14, Oum El Bouaghi, or 0555123456",
    )

    try:
        search_results = search_users(search_text, selected_field) if search_text.strip() else []
    except RuntimeError as exc:
        st.error(str(exc))
        search_results = []

    if search_text.strip():
        render_user_table(search_results, title="Matching results")
    else:
        st.info("Enter a value to start searching.")

with update_tab:
    st.subheader("Update User")
    st.write("Select a user, load their data into the form, then edit and save the changes.")
    users = load_all_users()

    if users:
        selected_index = st.selectbox(
            "Select user to update",
            options=list(range(len(users))),
            format_func=lambda index: user_label(users[index]),
            key="update_select_user",
        )
        selected_user = users[selected_index]
        submitted, updated_data = user_input_form(
            defaults=selected_user,
            form_key="update_user_form",
            submit_label="Update User",
        )

        if submitted:
            is_valid, message = validate_user(updated_data)
            if not is_valid:
                st.error(message)
            else:
                updated_data["updated_at"] = datetime.now(timezone.utc)
                try:
                    update_user(selected_user["_id"], updated_data)
                    st.success("User updated successfully.")
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
                except RuntimeError as exc:
                    st.error(str(exc))
    else:
        st.info("No users found. Add a user first.")

with delete_tab:
    st.subheader("Delete User")
    st.write("Select a user and confirm before deleting the record from MongoDB.")
    users = load_all_users()

    if users:
        selected_index = st.selectbox(
            "Select user to delete",
            options=list(range(len(users))),
            format_func=lambda index: user_label(users[index]),
            key="delete_select_user",
        )
        selected_user = users[selected_index]
        st.warning("Selected user:")
        render_user_table([selected_user], title="User to delete")
        st.error("Danger zone: this action permanently deletes the selected user from MongoDB.")
        confirm_delete = st.checkbox("I confirm that I want to delete this user.")

        if st.button("Delete User", disabled=not confirm_delete):
            try:
                deleted_count = delete_user(selected_user["_id"])
                if deleted_count:
                    st.success("User deleted successfully.")
                    st.rerun()
                else:
                    st.warning("No user was deleted.")
            except RuntimeError as exc:
                st.error(str(exc))
    else:
        st.info("No users found. Add a user first.")
