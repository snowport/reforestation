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
st.title("Introduction: Land Screening Tool")

st.markdown(
    """
    The application allows a user to define a region of interest (ROI) and then map the NLCD 2021 layer for that ROI.
    
    The app then calculates the individual landcover types for that region and more speciifcally the areas of non-forested coverage.

    Click on "🌲 land screening tool" in the left panel. 
    
    Test out your ROI! 
    """
)

st.header("Step 1: Gather a GeoJSON")
st.write("Copy to your clipboard a GeoJSON from clicking on the link at the top of the page.")
st.image('images\Title.PNG', width=800)

st.header("Step 2: Enter JSON")
st.write("Paste the JSON into the text box and hit 'CTRL+ENTER' to add the ROI to a map")
st.image('images\example_JSON.PNG', width = 800)

st.header("Step 3: Select Slope Threshold")
st.write("Select a slope threshold between 10%, 20%, or 30%.")
st.image('images\slope_threshold.PNG', width=800)

st.header("Step 4: Run the Program")
st.write("Be sure the correct ROI is selected and when you are ready hit 'Calculate' to the run the application.")
st.image('images\Map1.PNG')

st.header("Step 5: Evaluate NLCD Results")
st.write("Check out the resulting NLCD layer for the chosen ROI and evaluate: ")
st.write("(1) Breakdown of landcover classes.")
st.image('images\Map2.PNG')
st.write("(2) Non-Forested Coverage Area")
st.image('images\\nf_results.PNG')
st.write("(3) Plantable Areas for Reforestation")
st.image('images\Map3.PNG')
st.write("You are able to 'Export the Image' of the plantable areas at the bottom of the page.")