import streamlit as st
import geemap.foliumap as geemap

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
Web App URL: <https://land-screening-tool.streamlit.app>
"""

st.sidebar.title("About")
st.sidebar.info(markdown)

# Customize page title
st.title("Land Screening Tool")

st.markdown(
    """
    This web "Land Screening Tool" application allows a user to define a region of interest (ROI) and then map the NLCD 2021 layer for that ROI.

    The app then calculates the individual landcover types for that region and more speciifcally the areas of non-forested coverage.

    
    Click on "land ccreening app" on the left panel.

    Test it out for your region! 


    -NP
    """
)