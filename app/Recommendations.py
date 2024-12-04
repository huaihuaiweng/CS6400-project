import streamlit as st
import sqlite3

# Database connection
def create_connection():
    try:
        return sqlite3.connect("papers.db")  # Replace with your actual database path
    except sqlite3.Error as e:
        st.error(f"Database connection failed: {e}")
        return None

# Fetch all papers in the reading list
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

# Fetch paper details by paper_id
def fetch_paper_details(paper_ids):
    conn = create_connection()
    if not conn:
        return []
    try:
        query = f"""
            SELECT paper_id, title, authors
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

# Mock function to recommend papers
def reccPaper(reading_list):
    # Replace this with your recommendation logic
    # For now, use existing paper IDs for simplicity
    return [paper[0] for paper in reading_list]  # Mock recommendation IDs

# Recommendations Page
def app():
    st.title("Paper Recommendations")

    # Fetch reading list
    reading_list = fetch_reading_list()
    st.write("Debug: Reading List", reading_list)  # Debugging output

    if not reading_list:
        st.warning("Your reading list is empty.")
        return

    # Display the reading list
    st.write("Your Reading List:")
    for _, title, authors in reading_list:
        st.write(f"**Title**: {title}")
        st.write(f"**Authors**: {authors}")

    # Get recommendations
    recommended_paper_ids = reccPaper(reading_list)
    st.write("Debug: Recommended Paper IDs", recommended_paper_ids)  # Debugging output

    if not recommended_paper_ids:
        st.warning("No recommendations available.")
        return

    # Fetch and display recommended papers
    recommended_papers = fetch_paper_details(recommended_paper_ids)
    st.write("Debug: Recommended Papers", recommended_papers)  # Debugging output

    if recommended_papers:
        st.write("Recommendations:")
        for _, title, authors in recommended_papers:
            st.write(f"**Title**: {title}")
            st.write(f"**Authors**: {authors}")
    else:
        st.warning("No recommendations available.")