import json
from app.program import reccPaper
import os
import re
import sqlite3


def save_results_to_file(final_results, file_name='combined_results.json'):
    with open(file_name, 'w') as f:
        json.dump(final_results, f)

def load_results_from_file(file_name='combined_results.json'):
    try:
        with open(file_name, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def update_results(new_paper, file_name='combined_results.json', add=True):
    # Load existing results
    final_results = load_results_from_file(file_name)
    
    # Get recommendations for the new paper
    new_results = reccPaper(new_paper)
    
    # Update the existing results
    if add:
        for rec in new_results:
            if rec not in final_results:
                final_results[rec] = 0
            final_results[rec] += 1
    else:
        for rec in new_results:
            final_results[rec] -= 1
            if final_results[rec] == 0:
                del final_results[rec]

    
    # Save the updated results back to the file
    save_results_to_file(final_results, file_name)
    
    # Return the top 10 recommendations
    sorted_results = sorted([(count, rec) for rec, count in final_results.items()], reverse=True)
    return sorted_results[:10]

# Function to parse a single .abs file
def parse_abs_data(abs_data):
    patterns = {
        'paper_id': r'Paper: (.+)',
        'authors': r'Authors: (.+)',
        'title': r'Title: (.+)',
        'comments': r'Comments: (.+)',
        'subj_class': r'Subj-class: (.+)',
        'journal_ref': r'Journal-ref: (.+)',
        'abstract': r'\n\\\\\n ([\s\S]+?)\n\\\\\n',
    }
    return {key: re.search(pattern, abs_data).group(1).strip() if re.search(pattern, abs_data) else None
            for key, pattern in patterns.items()}

def extract_citations(paper_id, citation_file_path):
    """
    Extracts incoming and outgoing citations for a given paper_id from the citation file.

    :param paper_id: The paper_id to find citations for.
    :param citation_file_path: Path to the citation file.
    :return: A tuple (outgoing_citations, incoming_citations).
        - outgoing_citations: List of papers cited by the given paper_id (from paper_id).
        - incoming_citations: List of papers citing the given paper_id (to paper_id).
    """
    outgoing_citations = set()
    incoming_citations = set()

    try:
        with open(citation_file_path, "r") as file:
            for line in file:
                # Skip comments or blank lines
                if line.startswith("#") or not line.strip():
                    continue

                # Parse citation line
                from_paper, to_paper = line.strip().split()
                
                if from_paper == paper_id:
                    outgoing_citations.add(to_paper)  # Outgoing citations
                elif to_paper == paper_id:
                    incoming_citations.add(from_paper)  # Incoming citations

    except FileNotFoundError:
        print(f"Error: File not found at {citation_file_path}.")
    except Exception as e:
        print(f"Error processing citation file: {e}")

    return list(outgoing_citations), list(incoming_citations)

def insert_new_paper(conn, paper_metadata, citations_from, citations_to, publication_date):
    """
    Inserts a new paper into the database and incrementally updates citation and co-citation counts.

    :param conn: SQLite database connection.
    :param paper_metadata: Dictionary containing paper metadata (e.g., paper_id, title, authors, etc.).
    :param citations_from: List of papers that this paper cites (outgoing citations).
    :param citations_to: List of papers that cite this paper (incoming citations).
    :param publication_date: Date when the paper was published.
    """
    try:
        cur = conn.cursor()

        # Insert the new paper into the papers table
        cur.execute("""
            INSERT INTO papers (paper_id, title, authors, comments, subj_class, journal_ref, abstract, submitted_date, citation_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_metadata["paper_id"], 
            paper_metadata["title"], 
            paper_metadata["authors"], 
            paper_metadata["comments"], 
            paper_metadata["subj_class"], 
            paper_metadata["journal_ref"], 
            paper_metadata["abstract"], 
            publication_date, 
            len(citations_to)  # Citation count is the number of incoming citations
        ))

        # Insert the new paper's publication date
        cur.execute("""
            INSERT INTO paper_dates (paper_id, publication_date)
            VALUES (?, ?)
        """, (paper_metadata["paper_id"], publication_date))

        # Insert outgoing citations (papers cited by the new paper)
        for cited_paper_id in citations_from:
            cur.execute("""
                INSERT INTO citations (from_paper_id, to_paper_id)
                VALUES (?, ?)
            """, (paper_metadata["paper_id"], cited_paper_id))

            # Increment citation count for the cited paper
            cur.execute("""
                UPDATE papers
                SET citation_count = citation_count + 1
                WHERE paper_id = ?
            """, (cited_paper_id,))

        # Incrementally update co-citations for outgoing citations
        for i in range(len(citations_from)):
            for j in range(i + 1, len(citations_from)):
                paper_1_id, paper_2_id = sorted([citations_from[i], citations_from[j]])
                cur.execute("""
                    INSERT INTO co_citations (paper_1_id, paper_2_id, co_citation_count)
                    VALUES (?, ?, 1)
                    ON CONFLICT (paper_1_id, paper_2_id)
                    DO UPDATE SET co_citation_count = co_citation_count + 1
                """, (paper_1_id, paper_2_id))

        # Insert incoming citations (papers citing the new paper)
        for citing_paper_id in citations_to:
            cur.execute("""
                INSERT INTO citations (from_paper_id, to_paper_id)
                VALUES (?, ?)
            """, (citing_paper_id, paper_metadata["paper_id"]))

            # Incrementally update co-citations for incoming citations
            cur.execute("""
                SELECT to_paper_id
                FROM citations
                WHERE from_paper_id = ?
            """, (citing_paper_id,))
            cited_papers = [row[0] for row in cur.fetchall()]

            for other_paper_id in cited_papers:
                if other_paper_id != paper_metadata["paper_id"]:
                    paper_1_id, paper_2_id = sorted([paper_metadata["paper_id"], other_paper_id])
                    cur.execute("""
                        INSERT INTO co_citations (paper_1_id, paper_2_id, co_citation_count)
                        VALUES (?, ?, 1)
                        ON CONFLICT (paper_1_id, paper_2_id)
                        DO UPDATE SET co_citation_count = co_citation_count + 1
                    """, (paper_1_id, paper_2_id))

        conn.commit()

    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error inserting new paper: {e}")

def remove_paper(conn, paper_id):
    """
    Removes a paper from the database and updates citation and co-citation counts.
    
    :param conn: SQLite database connection.
    :param paper_id: ID of the paper to remove.
    """
    try:
        cur = conn.cursor()

        # Get all papers cited by the paper to be removed
        cur.execute("""
            SELECT to_paper_id
            FROM citations
            WHERE from_paper_id = ?
        """, (paper_id,))
        cited_papers = [row[0] for row in cur.fetchall()]

        # Get all papers citing the paper to be removed
        cur.execute("""
            SELECT from_paper_id
            FROM citations
            WHERE to_paper_id = ?
        """, (paper_id,))
        citing_papers = [row[0] for row in cur.fetchall()]

        # Update citation counts for cited papers
        for cited_paper_id in cited_papers:
            cur.execute("""
                UPDATE papers
                SET citation_count = citation_count - 1
                WHERE paper_id = ?
            """, (cited_paper_id,))

        # Remove all co-citation entries involving this paper
        cur.execute("""
            DELETE FROM co_citations
            WHERE paper_1_id = ? OR paper_2_id = ?
        """, (paper_id, paper_id))


        # Delete from citations table
        cur.execute("""
            DELETE FROM citations
            WHERE from_paper_id = ? OR to_paper_id = ?
        """, (paper_id, paper_id))

        # Delete from paper_dates table
        cur.execute("""
            DELETE FROM paper_dates
            WHERE paper_id = ?
        """, (paper_id,))

        # Delete from papers table
        cur.execute("""
            DELETE FROM papers
            WHERE paper_id = ?
        """, (paper_id,))

        conn.commit()

    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error removing paper: {e}")