import streamlit as st
import sqlite3
from app.helpers import load_results_from_file

def create_connection():
    try:
        return sqlite3.connect("papers.db")  # Replace with your actual database path
    except sqlite3.Error as e:
        st.error(f"Database connection failed: {e}")
        return None

def fetch_reading_list():
    conn = create_connection()
    if not conn:
        return []
    try:
        query = """
            SELECT papers.paper_id, papers.title, papers.authors
            FROM reading_list
            INNER JOIN papers ON reading_list.paper_id = papers.paper_id
        """
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        return result
    except sqlite3.Error as e:
        st.error(f"Error fetching reading list: {e}")
        return []
    finally:
        conn.close()

def fetch_paper_details(paper_ids):
    conn = create_connection()
    if not conn:
        return []
    try:
        query = f"""
            SELECT paper_id, title, authors, abstract
            FROM papers
            WHERE paper_id IN ({','.join(['?'] * len(paper_ids))})
        """
        cur = conn.cursor()
        cur.execute(query, paper_ids)
        result = cur.fetchall()
        return result
    except sqlite3.Error as e:
        st.error(f"Error fetching paper details: {e}")
        return []
    finally:
        conn.close()

def reccPaper():
    res = load_results_from_file()
    sorted_results = sorted([(count, rec) for rec, count in res.items()], reverse=True)
    print(sorted_results[:10])
    return [i[1] for i in sorted_results[:10]]

def app():
    st.title("Paper Recommendations")

    # Fetch the reading list
    reading_list = fetch_reading_list()

    if not reading_list:
        st.warning("Your reading list is empty. Add some papers to get recommendations.")
        return

    recommended_paper_ids = reccPaper()
    
    if not recommended_paper_ids:
        st.warning("No recommendations available at this time.")
        return

    recommended_papers = fetch_paper_details(recommended_paper_ids)

    if recommended_papers:
        st.write("### Recommended Papers:")
        for i, paper in enumerate(recommended_papers, start=1):
            paper_id, title, authors, abstract = paper  # Adjust if abstract is part of your fetched details
            st.write(f"**{i}. Title:** {title}")
            st.write(f"**Authors:** {authors}")
            st.write(f"**Abstract:** {abstract}\n")
    else:
        st.warning("No recommendations available.")
