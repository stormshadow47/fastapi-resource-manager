import streamlit as st
import requests

# Base URL for the FastAPI backend
BASE_URL = "http://127.0.0.1:8000"

# Authentication functions
def register(username: str, password: str):
    return requests.post(
        f"{BASE_URL}/register",
        json={"username": username, "password": password},
    )

def login(username: str, password: str):
    resp = requests.post(
        f"{BASE_URL}/token",
        data={"username": username, "password": password},
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    else:
        st.error("Login failed. Check credentials.")
        return None

# Book CRUD helpers
def get_books(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/books", headers=headers)
    return resp.json() if resp.status_code == 200 else []

def add_book(token: str, title: str, author: str):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(
        f"{BASE_URL}/books",
        json={"title": title, "author": author},
        headers=headers,
    )

def update_book(token: str, book_id: int, title: str, author: str):
    headers = {"Authorization": f"Bearer {token}"}
    data = {}
    if title:
        data["title"] = title
    if author:
        data["author"] = author
    return requests.put(f"{BASE_URL}/books/{book_id}", json=data, headers=headers)

def delete_book(token: str, book_id: int):
    headers = {"Authorization": f"Bearer {token}"}
    return requests.delete(f"{BASE_URL}/books/{book_id}", headers=headers)

def logout():
    for k in ("token", "username"):
        if k in st.session_state:
            del st.session_state[k]
    st.success("Logged out successfully!")
    st.rerun()

# Streamlit App
def main():
    st.title("Resource Management System")

    # Sidebar: Login / Register / Logout
    with st.sidebar:
        if "token" not in st.session_state:
            st.header("Authentication")
            choice = st.radio("Action", ["Login", "Register"])
            if choice == "Register":
                u = st.text_input("Username", key="reg_user")
                p = st.text_input("Password", type="password", key="reg_pwd")
                if st.button("Register"):
                    r = register(u, p)
                    if r.status_code == 200:
                        st.success("Registered! You can now log in.")
                    else:
                        st.error(f"Registration failed: {r.text}")
            else:
                u = st.text_input("Username", key="login_user")
                p = st.text_input("Password", type="password", key="login_pwd")
                if st.button("Login"):
                    token = login(u, p)
                    if token:
                        st.session_state.token = token
                        st.session_state.username = u
                        st.success("Logged in successfully!")
                        st.rerun()
        else:
            st.header("User")
            st.write(f"Logged in as: **{st.session_state.username}**")
            if st.button("Logout"):
                logout()

    # Main content: book list, update & add
    if "token" in st.session_state:
        token = st.session_state.token

        st.subheader("Books List")
        books = get_books(token)
        for book in books:
            with st.expander(f"{book['id']}: {book['title']}"):
                st.write(f"Author: {book['author']}")
                new_t = st.text_input("New Title", value=book["title"], key=f"t{book['id']}")
                new_a = st.text_input("New Author", value=book["author"], key=f"a{book['id']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update", key=f"up{book['id']}"):
                        r = update_book(token, book["id"], new_t, new_a)
                        if r.status_code == 200:
                            st.success("Book updated!")
                            st.rerun()
                        else:
                            st.error(f"Update failed: {r.text}")
                with col2:
                    if st.button("Delete", key=f"del{book['id']}"):
                        r = delete_book(token, book["id"])
                        if r.status_code == 200:
                            st.success("Book deleted!")
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {r.text}")

        st.subheader("Add a New Book")
        t = st.text_input("Title", key="new_title")
        a = st.text_input("Author", key="new_author")
        if st.button("Add Book"):
            r = add_book(token, t, a)
            if r.status_code == 200:
                st.success("Book added!")
                st.rerun()
            else:
                st.error(f"Add failed: {r.text}")
    else:
        st.info("Please log in or register using the sidebar.")

if __name__ == "__main__":
    main()
