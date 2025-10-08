import streamlit as st

def show_study_mode_page(navigate):
    st.title("📚 Study Mode")
    st.caption("Upload study materials and activate the AI assistance system.")

    # Privacy Notice Modal
    st.subheader("⚠️ Privacy Notice")
    st.write("""
    When you activate Study Mode, the system may analyze your uploaded materials,
    monitor your interaction time, and suggest breaks or improvements.
    Please review and accept to proceed.
    """)
    
    agree = st.checkbox("I agree to the terms above")
    next_disabled = not agree

    st.divider()

    if st.button("Next ➜", disabled=next_disabled):
        st.success("Privacy agreement accepted. Study mode activated!")

        # Upload section
        st.subheader("📂 Upload Study Material (PDF)")
        uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
        if uploaded_file:
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")

        # Settings section
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        col1, col2, col3 = st.columns(3)
        with col1:
            ui_toggle = st.toggle("Change UI Theme")
        with col2:
            alert_toggle = st.toggle("Enable Alerts")
        with col3:
            reco_toggle = st.toggle("Study Break Recommendations")

        st.info("Settings will take effect once backend integration is complete.")
