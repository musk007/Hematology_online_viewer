import streamlit as st
import json
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="Online Viewer",
    layout="wide"
)

# Load data
with open("data.json", "r") as f:
    data = json.load(f)

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

    feedback = st.text_area(
        "Enter your feedback",
        height=200
    )

    if st.button("Submit Feedback"):
        row = {
            "group": group_name,
            "feedback": feedback,
            "timestamp": str(datetime.now())
        }

        pd.DataFrame([row]).to_csv(
            "feedback.csv",
            mode="a",
            header=not os.path.exists(f"{group_name}.csv"),
            index=False
        )
        st.write(os.path.abspath(f"{group_name}.csv"))
        st.success("Feedback submitted.")