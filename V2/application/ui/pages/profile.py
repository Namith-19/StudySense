import streamlit as st

def render():
    st.title("👤 Profile")
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.write("User: **John Doe**")
    st.write("Email: johndoe@studysense.ai")
    st.write("Account Type: Student")

    st.markdown("---")
    st.subheader("Edit Profile")
    new_name = st.text_input("Update Name", "John Doe")
    st.button("Save Changes")
