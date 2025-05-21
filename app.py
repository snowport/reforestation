import streamlit as st

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
Web App URL: <https://reforestation.streamlit.app>
"""

st.sidebar.title("About")
st.sidebar.info(markdown)

st.title("Reforestation Calculator")
st.image('https://ychef.files.bbci.co.uk/976x549/p07n19vr.jpg', width=1000)