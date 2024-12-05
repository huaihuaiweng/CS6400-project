from flask import render_template, Blueprint
import sqlite3
from app.helpers import load_results_from_file

# Blueprint for modular routing
recommendations_bp = Blueprint("recommendations", __name__, template_folder="templates")

# Database connection
def create_connection():
    try:
        return sqlite3.connect("papers.db")  # Replace with your actual database path
    except sqlite3.Error as e:
        print(f"Database connection failed: {e}")
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
        print(f"Error fetching reading list: {e}")
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
            SELECT paper_id, title, authors, abstract
            FROM papers
            WHERE paper_id IN ({','.join(['?'] * len(paper_ids))})
        """
        cur = conn.cursor()
        cur.execute(query, paper_ids)
        result = cur.fetchall()
        return result
    except sqlite3.Error as e:
        print(f"Error fetching paper details: {e}")
        return []
    finally:
        conn.close()

# Mock function to recommend papers
def reccPaper():
    res = load_results_from_file()
    sorted_results = sorted([(count, rec) for rec, count in res.items()], reverse=True)
    return [i[1] for i in sorted_results[:10]]

# Flask route for Recommendations Page
@recommendations_bp.route("/recommendations")
def recommendations():
    # Fetch the reading list
    reading_list = fetch_reading_list()

    if not reading_list:
        return render_template("recommendations.html", recommended_papers=None, message="Your reading list is empty. Add some papers to get recommendations.")

    # Get recommendations based on the reading list
    recommended_paper_ids = reccPaper()
    
    if not recommended_paper_ids:
        return render_template("recommendations.html", recommended_papers=None, message="No recommendations available at this time.")

    # Fetch details of the recommended papers
    recommended_papers = fetch_paper_details(recommended_paper_ids)

    if recommended_papers:
        return render_template("recommendations.html", recommended_papers=recommended_papers, message=None)
    else:
        return render_template("recommendations.html", recommended_papers=None, message="No recommendations available.")