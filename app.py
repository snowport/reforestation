import streamlit as st
import geemap.foliumap as geemap

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
Web App URL: <https://noah-geemap.streamlit.app>
"""

st.sidebar.title("About")
st.sidebar.info(markdown)

# Customize page title
st.title("Land Screening App")

st.markdown(
    """
    This webapp allows a user to define a region of interest (ROI) and then map the NLCD 2021 layer for that ROI.

    The app then calculates the individual landcover types for that region and plots them on a bar graph.

    Test if out for your region! Click on the "land ccreening app" on the left.
    """
)