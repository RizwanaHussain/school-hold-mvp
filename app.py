import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage

# ✅ Gmail SMTP Configuration (Replace with YOUR Email & Password)
EMAIL_ADDRESS = "anawzir1311@gmail.com"  # <-- your Gmail here
EMAIL_PASSWORD = "tiidjoiavyehinuz"  # Your App Password (without spaces)

# ✅ Load Data from Excel Files using 'openpyxl' engine
students = pd.read_excel("student_data.xlsx", engine='openpyxl')
staff_mapping = pd.read_excel("bus_details.xlsx", engine='openpyxl')

# ✅ Streamlit App Interface
st.title("🚸 Child Hold Request Form (MVP)")

with st.form("hold_request"):
    student_name = st.text_input("Student Name (Exactly as in Records)")
    grade = st.selectbox("Grade", students["Grade"].unique())
    section = st.selectbox("Section", students["Section"].unique())
    bus_no = st.selectbox("Bus Number", students["Bus No"].unique())
    parent_name = st.text_input("Parent Name")
    consent = st.checkbox("✅ I Confirm My Request To Hold My Child")

    submitted = st.form_submit_button("Submit Request")

    if submitted:
        if not consent:
            st.error("⚠️ You must confirm the consent to proceed.")
        else:
            # ✅ Lookup Student & Staff
            student_match = students[
                (students["Student Name"] == student_name) &
                (students["Grade"] == grade) &
                (students["Section"] == section) &
                (students["Bus No"] == bus_no)
            ]

            staff_match = staff_mapping[
                (staff_mapping["Grade"] == grade) &
                (staff_mapping["Section"] == section) &
                (staff_mapping["Bus No"] == bus_no)
            ]

            if not student_match.empty and not staff_match.empty:
                email_list = [
                    staff_match.iloc[0]["Class Teacher Email"],
                    staff_match.iloc[0]["Supervisor Email"],
                    staff_match.iloc[0]["Bus Attender Email"],
                    staff_match.iloc[0]["Bus Driver Email"]
                ]

                msg = EmailMessage()
                msg['Subject'] = "🚸 Child Hold Request Notification"
                msg['From'] = EMAIL_ADDRESS
                msg['To'] = ", ".join(email_list)
                msg.set_content(f"""
                Child Hold Request Received:

                Student Name: {student_name}
                Grade: {grade}-{section}
                Bus No: {bus_no}
                Parent Name: {parent_name}

                ✅ ACTION: Please hold the student at school. Parent will pick up.

                - This is an automated message.
                """)

                # ✅ Send Email via Gmail SMTP
                try:
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                        smtp.send_message(msg)
                    st.success("✅ Request submitted & emails sent successfully!")
                except Exception as e:
                    st.error(f"❌ Email sending failed: {e}")

            else:
                st.error("⚠️ Student or Staff not found. Please double-check the details.")
