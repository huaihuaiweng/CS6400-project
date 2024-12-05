import streamlit as st
import sqlite3
from fuzzywuzzy import process
from app.Recommendations import app as recommendation_app
from app.helpers import update_results

# Database connection
def create_connection():
    return sqlite3.connect("papers.db")  # Replace with your actual database path

# Fetch all paper titles from the database (cached with st.cache_data)
@st.cache_data
def fetch_all_papers():
    conn = create_connection()
    query = "SELECT paper_id, title, authors FROM papers"
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.close()
    return result

# Search for similar titles using fuzzy matching (cached with st.cache_data)
@st.cache_data
def search_papers_by_title(papers, query, limit=5):
    titles = [paper[1] for paper in papers]  # Extract only titles
    results = process.extract(query, titles, limit=limit)
    return [(papers[titles.index(result[0])][0], result[0], papers[titles.index(result[0])][2], result[1]) for result in results]

# Fetch all papers in the reading list (not cached to ensure immediate updates)
def fetch_reading_list():
    conn = create_connection()
    query = """
        SELECT papers.paper_id, papers.title, papers.authors
        FROM reading_list
        INNER JOIN papers ON reading_list.paper_id = papers.paper_id
    """
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.close()
    return result

# Add a paper to the reading list
def add_to_reading_list(conn, paper_id):
    query = "INSERT INTO reading_list (paper_id) VALUES (?)"
    cur = conn.cursor()

    try:
        cur.execute(query, (paper_id,))
        conn.commit()
        query = "SELECT title from papers where paper_id=?"
        cur.execute(query, (paper_id,))
        paper_name = cur.fetchall()[0][0]
        update_results(paper_name)
        return True
    except sqlite3.IntegrityError:
        return False  # Paper already in the reading list
    return False
# Remove multiple papers from the reading list
def remove_from_reading_list(conn, paper_ids):
    query = "DELETE FROM reading_list WHERE paper_id = ?"
    cur = conn.cursor()
    for paper_id in paper_ids:
        cur.execute(query, (paper_id,))
        query = "SELECT title from papers where paper_id=?"
        cur.execute(query, (paper_id,))
        paper_name = cur.fetchall()[0][0]
        update_results(paper_name,add=False)

    conn.commit()



def app():

    # Initialize the app
    st.title("Manage Your Reading List")
        
    # Create a "reading_list" table if it doesn't exist
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reading_list (
            paper_id TEXT PRIMARY KEY,
            FOREIGN KEY (paper_id) REFERENCES papers (paper_id)
        )
    """)
    conn.commit()

    # Section to search and add papers to the reading list
    st.header("Search and Add Papers to Your Reading List")
    search_query = st.text_input("Enter a title to search:")
    all_papers = fetch_all_papers()

    if search_query:
        search_results = search_papers_by_title(all_papers, search_query)
        if search_results:
            st.write("Search Results:")
            for result in search_results:
                paper_id, title, authors, similarity = result
                st.write(f"**Title**: {title}")
                st.write(f"**Authors**: {authors}")
                # st.write(f"**Similarity**: {similarity}%")
                if st.button(f"Add to Reading List: {title}", key=f"add_{paper_id}"):
                    added = add_to_reading_list(conn, paper_id)
                    if added:
                        st.success(f"'{title}' has been added to your reading list.")
                        st.session_state["reading_list"] = fetch_reading_list()  # Refresh the reading list
                    else:
                        st.warning(f"'{title}' is already in your reading list.")
        else:
            st.write("No results found. Try a different query.")

    # Display and manage the reading list
    st.header("Your Reading List")

    if "reading_list" not in st.session_state:
        st.session_state["reading_list"] = fetch_reading_list()

    if "selected_papers" not in st.session_state:
        st.session_state["selected_papers"] = set()

    reading_list = st.session_state["reading_list"]
    if reading_list:
        st.write("Select papers to remove from your reading list:")
        for paper in reading_list:
            paper_id, title, authors = paper
            checkbox_key = f"checkbox_{paper_id}"
            if st.checkbox(f"Title: {title}, Authors: {authors}", key=checkbox_key):
                st.session_state["selected_papers"].add(paper_id)
            else:
                st.session_state["selected_papers"].discard(paper_id)

        if st.button("Remove Selected Papers"):
            if st.session_state["selected_papers"]:
                # Remove selected papers
                remove_from_reading_list(conn, list(st.session_state["selected_papers"]))
                st.success("Selected papers have been removed from your reading list.")
                # Clear selections and refresh reading list
                st.session_state["selected_papers"].clear()
                st.session_state["reading_list"] = fetch_reading_list()  # Update the reading list
            else:
                st.warning("No papers selected.")
    else:
        st.write("Your reading list is empty.")

    conn.close()