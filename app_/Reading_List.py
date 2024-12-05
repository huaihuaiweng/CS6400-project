from flask import render_template, Blueprint, request, redirect, url_for
import sqlite3
from fuzzywuzzy import process
from app.helpers import update_results

# Blueprint for modular routing
reading_list_bp = Blueprint("reading_list", __name__, template_folder="templates")

# Database connection
def create_connection():
    return sqlite3.connect("papers.db")  # Replace with your actual database path

# Fetch all paper titles from the database
def fetch_all_papers():
    conn = create_connection()
    query = "SELECT paper_id, title, authors FROM papers"
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.close()
    return result

# Search for similar titles using fuzzy matching
def search_papers_by_title(papers, query, limit=5):
    titles = [paper[1] for paper in papers]  # Extract only titles
    results = process.extract(query, titles, limit=limit)
    return [(papers[titles.index(result[0])][0], result[0], papers[titles.index(result[0])][2], result[1]) for result in results]

# Fetch all papers in the reading list
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
def add_to_reading_list(paper_id):
    conn = create_connection()
    query = "INSERT INTO reading_list (paper_id) VALUES (?)"
    cur = conn.cursor()
    try:
        cur.execute(query, (paper_id,))
        conn.commit()
        query = "SELECT title FROM papers WHERE paper_id=?"
        cur.execute(query, (paper_id,))
        paper_name = cur.fetchall()[0][0]
        update_results(paper_name)
    except sqlite3.IntegrityError:
        return False  # Paper already in the reading list
    finally:
        conn.close()
    return True

# Remove multiple papers from the reading list
def remove_from_reading_list(paper_ids):
    conn = create_connection()
    query = "DELETE FROM reading_list WHERE paper_id = ?"
    cur = conn.cursor()
    for paper_id in paper_ids:
        cur.execute(query, (paper_id,))
        query = "SELECT title FROM papers WHERE paper_id=?"
        cur.execute(query, (paper_id,))
        paper_name = cur.fetchall()[0][0]
        update_results(paper_name, add=False)
    conn.commit()
    conn.close()

# Flask route for Reading List page
@reading_list_bp.route("/reading-list", methods=["GET", "POST"])
def reading_list():
    search_results = None
    search_query = None
    reading_list = fetch_reading_list()  # Current reading list

    if request.method == "POST":
        if "search" in request.form:
            search_query = request.form.get("search_query", "").strip()  # Get the user's input
            if search_query:
                all_papers = fetch_all_papers()  # Fetch all papers
                reading_list_paper_ids = {paper[0] for paper in reading_list}  # Exclude papers already in reading list
                search_results = search_papers_by_title(all_papers, search_query)
                search_results = [result for result in search_results if result[0] not in reading_list_paper_ids]

        elif "add" in request.form:
            paper_id = request.form.get("paper_id")
            if paper_id:
                add_to_reading_list(paper_id)
            return redirect(url_for("reading_list.reading_list"))

        elif "remove" in request.form:
            selected_papers = request.form.getlist("selected_papers")
            if selected_papers:
                remove_from_reading_list(selected_papers)
            return redirect(url_for("reading_list.reading_list"))

    return render_template(
        "reading_list.html",
        reading_list=reading_list,
        search_results=search_results,
        search_query=search_query
    )