import streamlit as st
import json
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
if "current_group" not in st.session_state:
    st.session_state.current_group = group_name

elif st.session_state.current_group != group_name:
    st.session_state.current_group = group_name
    st.session_state.feedback_text = ""

st.title("Leukemia Image-Report Viewer")

# Layout
left, right = st.columns([1.5, 2])

# -------------------------
# IMAGE AREA
# -------------------------
with left:
    st.subheader("Images")

    if len(group["images"]) > 0:

        # Selected image
        if (
            "selected_group" not in st.session_state
            or st.session_state.selected_group != group_name
        ):
            st.session_state.selected_group = group_name
            st.session_state.selected_image = group["images"][0]

        zoom = st.slider("Zoom", 50, 200, 50, step=10)

        st.image(
            st.session_state.selected_image,
            width=int(700 * zoom / 100)
        )

        st.markdown("---")

        # Thumbnail grid
        st.markdown("### Image thumbnails")

        with st.container(height=500):
            cols = st.columns(5)

            for idx, img in enumerate(group["images"]):
                with cols[idx % 5]:
                    caption = f"Image {idx+1}"

                    if img == st.session_state.selected_image:
                        caption = f"✅ Image {idx+1}"

                    st.image(
                        img,
                        caption=caption,
                        use_container_width=True
                    )

                    if st.button("Select", key=f"select_{group_name}_{idx}"):
                        st.session_state.selected_image = img

# -------------------------
# RIGHT PANEL
# -------------------------
with right:

    

    # st.subheader("Information")
    info = group["info"]

    st.subheader("Summary")
    st.write(f"**Diagnosis:** {info['metadata_filename_diagnosis']}")
    st.write(f"**Number of images:** {info['n_images']}")
    st.write(f"**Total cells:** {info['n_cells_total']}")
    st.write(f"**Identified WBCs:** {info['n_cells_identified_wbc']}")

    with st.expander("Cell counts"):
        st.json(info["cell_counts"])

    with st.expander("Cell percentages - all cells"):
        st.json(info["cell_percentages_all"])

    with st.expander("Cell percentages - clinical"):
        st.json(info["cell_percentages_clinical"])

    with st.expander("Attributes"):
        st.json(info["attributes"])

    with st.expander("Report-ready summary"):
        st.json(info["report_ready"])

    with st.expander("Diagnostic flags"):
        st.json(info["report_ready"]["diagnostic_flags"])

    with st.expander("Blast morphology"):
        st.json(info["report_ready"]["blast_morphology"])

    with st.expander("QC"):
        st.json(info["report_ready"]["qc"])

    st.subheader("Report")
    st.markdown(group["text"])

    st.subheader("Feedback")

    reviewer = st.text_input("Reviewer name")

    if "feedback_text" not in st.session_state:
        st.session_state.feedback_text = ""

    feedback = st.text_area(
        "Enter your feedback, or enter 'No feedback' if you don't have any",
        key="feedback_text",
        height=200
    )

    if st.button("Submit Feedback"):

        if feedback.strip() == "":
            st.warning("Please enter feedback before submitting.")

        elif reviewer.strip() == "":
            st.warning("Please enter reviewer name before submitting.")

        else:
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

            st.success(f"Feedback submitted for {group_name}.")
            