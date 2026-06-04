import streamlit as st
import json
import pandas as pd
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials




st.set_page_config(
    page_title="Online Viewer",
    layout="wide"
)

# Load data
with open("data.json", "r") as f:
    data = json.load(f)

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

if os.path.exists("credentials.json"):
    creds = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scopes
    )
else:
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )

client = gspread.authorize(creds)
spreadsheet = client.open("Hematology_feedback")
worksheet = spreadsheet.sheet1

# Select patient/group
group_name = st.sidebar.selectbox(
    "Select Patient",
    list(data.keys())
)

group = data[group_name]

st.title("Leukemia Image-Report Viewer")

# Layout
left, right = st.columns([3, 1])

# -------------------------
# IMAGE AREA
# -------------------------
with left:
    st.subheader("Images")

    if len(group["images"]) > 0:

        # Selected image
        if "selected_image" not in st.session_state:
            st.session_state.selected_image = group["images"][0]

        zoom = st.slider("Zoom", 50, 200, 50, step=10)

        st.image(
            st.session_state.selected_image,
            width=int(700 * zoom / 100)
        )

        st.markdown("---")

        # Thumbnail grid
        cols = st.columns(4)

        for idx, img in enumerate(group["images"]):
            with cols[idx % 4]:
                if st.button(
                    f"Image {idx+1}",
                    key=f"img_{idx}"
                ):
                    st.session_state.selected_image = img

# -------------------------
# RIGHT PANEL
# -------------------------
with right:

    st.subheader("Description")
    st.write(group["text"])

    st.subheader("Information")
    st.json(group["info"])

    st.subheader("Feedback")

    reviewer = st.text_input("Reviewer name")

    feedback = st.text_area(
        "Enter your feedback",
        height=200
    )

    if st.button("Submit Feedback"):
        row = {
            "timestamp": str(datetime.now()),
            "group": group_name,
            "reviewer": reviewer,
            "feedback": feedback
        }

        worksheet.append_row([
            row["timestamp"],
            row["group"],
            row["reviewer"],
            row["feedback"]
        ])

        st.success("Feedback submitted.")