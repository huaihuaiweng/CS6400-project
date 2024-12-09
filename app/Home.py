import streamlit as st
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)# Import apps
from app.Reading_List import app as reading_list_app
from app.Recommendations import app as recommendations_app

if "page" not in st.session_state:
    st.session_state.page = "Reading List"

st.sidebar.title("Navigation")
st.session_state.page = st.sidebar.radio("Select a Page", ["Reading List", "Recommendation Page"])

if st.session_state.page == "Reading List":
    reading_list_app()
elif st.session_state.page == "Recommendation Page":
    recommendations_app()
