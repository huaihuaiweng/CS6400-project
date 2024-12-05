import streamlit as st
import sys
import os

# Add project root to sys.path
sys.path.append('/Users/ericweng/GT/CS6400-project')

# Import apps
from app.Reading_List import app as reading_list_app
from app.Recommendations import app as recommendations_app

# Initialize session state for page navigation
if "page" not in st.session_state:
    st.session_state.page = "Reading List"

# Sidebar for Navigation
st.sidebar.title("Navigation")
st.session_state.page = st.sidebar.radio("Select a Page", ["Reading List", "Recommendation Page"])

# Page Navigation
if st.session_state.page == "Reading List":
    reading_list_app()
elif st.session_state.page == "Recommendation Page":
    recommendations_app()
