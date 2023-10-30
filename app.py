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
st.title("Earth Engine Web App")

st.markdown(
    """
    This multipage app template demonstrates various interactive web apps created using [streamlit](https://streamlit.io) and [geemap](https://geemap.org).
    """
)

markdown = """
"""

st.markdown(markdown)
m = geemap.Map()
m.add_basemap("OpenTopoMap")
m.to_streamlit(height=500)