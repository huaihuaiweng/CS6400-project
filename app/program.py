# %%
import os    
import pandas as pd
import ollama
import chromadb
import re
import sqlite3

# %%
client = chromadb.PersistentClient(path="full_data/")

# %%
def retrieveID(paper_name, cursor):
    connection = sqlite3.connect("papers.db")
    cursor = connection.cursor()

    query = """
    SELECT paper_id FROM papers
    WHERE title = ?
    Limit 1
    """
    cursor.execute(query, (paper_name,))
    results = cursor.fetchall()
    
    #This returns paperID for use in future queries because working with a single ID is easier than working with title string
    return(results[0][0])

    #retrieveID("Intersection Theory, Integrable Hierarchies and Topological Field Theory") Example use case returns 9201003

# %%
def retrieveID_batch(paper_names, cursor):
    connection = sqlite3.connect("papers.db")
    cursor = connection.cursor()
    paper_names_str = str(paper_names).replace('[', '(').replace(']', ')')

    query = f"""
    SELECT title,paper_id FROM papers
    WHERE title IN {paper_names_str}
    """
    cursor.execute(query)
    results = cursor.fetchall()
    print(results)
    mp = {}
    for result in results:
        mp[result[0]] = result[1]

    ids_list = []
    for name in paper_names:
      ids_list.append(mp[name])

    return ids_list


# %%
def get_similar_abstract(paper_id, cursor, limit=30):
    #VectorDB is broken for me so I will assume this returns a list of IDs and try not to kill myself

    query = """
    SELECT abstract FROM papers
    WHERE paper_id = ?
    Limit 1
    """
    cursor.execute(query, (paper_id,))
    results = cursor.fetchall()
    #Retrieved abstract from relationalDB
    abstract = results[0][0]
    
    #Make Call to VectorDB; No clue if this works or not because once again my connection is being shot and stabbed
    #Instantiate Collection; using name = abstract change if named differently
    collection = client.get_or_create_collection(name="docs")
    
    response = ollama.embeddings(
      prompt=abstract,
      model="mxbai-embed-large"
    )
    results = collection.query(
      query_embeddings=[response["embedding"]],
      n_results=limit
    )

    #Data will have to be formatted by someone who can yk read the fucking data but just return list of ids
    data = results['ids'][0]
    return(data)

# %%
def get_similar_abstract_batch(paper_ids, cursor, limit=30):
    paper_ids_str = str(paper_ids).replace('[', '(').replace(']', ')')
    query = f"""
    SELECT paper_id,abstract FROM papers
    WHERE paper_id IN {paper_ids_str}
    """
    cursor.execute(query)
    results = cursor.fetchall()
    #Retrieved abstract from relationalDB
    mp = {}
    for result in results:
        mp[result[0]] = result[1]
    # abstract = results[0][0]
    abs_list = []
    for id in paper_ids:
      abs_list.append(mp[id])
    
    #Make Call to VectorDB; No clue if this works or not because once again my connection is being shot and stabbed
    #Instantiate Collection; using name = abstract change if named differently
    collection = client.get_or_create_collection(name="docs")
    
    response = ollama.embed(
      input=abs_list,
      model="mxbai-embed-large"
    )
    results = collection.query(
      query_embeddings=response["embeddings"],
      n_results=limit
    )

    #Data will have to be formatted by someone who can yk read the fucking data but just return list of ids
    data = results['ids'][0]
    return data

# %%
def get_similar_authors(paper_id, cursor,limit=30):
    #VectorDB is broken for me so I will assume this returns a list of IDs and try not to kill myself

    query = """
    SELECT authors FROM papers
    WHERE paper_id = ?
    Limit 1
    """
    cursor.execute(query, (paper_id,))
    results = cursor.fetchall()
    #Retrieved abstract from relationalDB
    abstract = results[0][0]
    
    #Make Call to VectorDB; No clue if this works or not because once again my connection is being shot and stabbed
    #Instantiate Collection; using name = abstract change if named differently
    collection = client.get_or_create_collection(name="authors")
    
    response = ollama.embeddings(
      prompt=abstract,
      model="mxbai-embed-large"
    )
    results = collection.query(
      query_embeddings=[response["embedding"]],
      n_results=limit
    )

    #Data will have to be formatted by someone who can yk read the fucking data but just return list of ids
    data = results['ids'][0]
    return(data)

# %%
def get_similar_authors_batch(paper_ids, cursor,limit=30):
    paper_ids_str = str(paper_ids).replace('[', '(').replace(']', ')')
    query = f"""
    SELECT paper_id,authors FROM papers
    WHERE paper_id IN {paper_ids_str}
    """
    cursor.execute(query)
    results = cursor.fetchall()
    #Retrieved abstract from relationalDB
    mp = {}
    for result in results:
        mp[result[0]] = result[1]
    # abstract = results[0][0]
    author_list = []
    for id in paper_ids:
      author_list.append(mp[id])
    
    #Make Call to VectorDB; No clue if this works or not because once again my connection is being shot and stabbed
    #Instantiate Collection; using name = abstract change if named differently
    collection = client.get_or_create_collection(name="authors")
    
    response = ollama.embed(
      input=author_list,
      model="mxbai-embed-large"
    )
    results = collection.query(
      query_embeddings=response["embeddings"],
      n_results=limit
    )

    #Data will have to be formatted by someone who can yk read the fucking data but just return list of ids
    data = results['ids'][0]
    return data

# %%
def find_co_citations(paper_id, cursor, limit = 30):

    #This query returns top co-citations as a list of tuples [(paper_id, citation_count)] 
    # query = """
    # SELECT 
    #     CASE 
    #         WHEN paper_1_id = ? THEN paper_2_id
    #         ELSE paper_1_id 
    #     END AS co_cited_paper_id,
    #     co_citation_count
    # FROM co_citations
    # WHERE paper_1_id = ? OR paper_2_id = ?
    # ORDER BY co_citation_count DESC
    # """
    query = """
    SELECT 
        CASE 
            WHEN paper_1_id = ? THEN paper_2_id
            ELSE paper_1_id
        END AS co_cited_paper_id,
        co_citation_count,
        pd.publication_date
    FROM co_citations
    JOIN paper_dates pd 
        ON pd.paper_id = CASE 
            WHEN paper_1_id = ? THEN paper_2_id
            ELSE paper_1_id
        END
    WHERE paper_1_id = ? OR paper_2_id = ?
    ORDER BY co_citation_count DESC, 
             pd.publication_date DESC
    LIMIT ?
    """
    cursor.execute(query, (paper_id, paper_id, paper_id, paper_id, limit))
    top_co_citations = cursor.fetchall()
    paper_id_list = [x[0] for x in top_co_citations]
    return paper_id_list
    #Sample Input: 
    #find_co_citations(9201001)
    #Sample Output: ['9201013', '9302014', '9203009', '9201011', '9201033', '9203043',
    #'9208031', '9208046', '9302048', '9303139', '9304011', '9201003', '9202006', '9203030',
    #'9206090', '9307063', '9312210', '9505127', '9201010', '9207020']

# %%
def find_co_citations_batch_optimized(paper_ids, cursor, limit=30):
    # Use VALUES to avoid a temporary table
    query = f"""
    WITH batch_inputs AS (
        VALUES {','.join(f'({paper_id}, {limit})' for paper_id in paper_ids)}
    ),
    RankedResults AS (
        SELECT 
            CASE 
                WHEN paper_1_id = bi.column1 THEN paper_2_id
                ELSE paper_1_id
            END AS co_cited_paper_id,
            co_citation_count,
            pd.publication_date,
            bi.column1 AS original_paper_id,
            ROW_NUMBER() OVER (
                PARTITION BY bi.column1 
                ORDER BY co_citation_count DESC, pd.publication_date DESC
            ) AS rank
        FROM co_citations
        JOIN paper_dates pd 
            ON pd.paper_id = CASE 
                WHEN paper_1_id = bi.column1 THEN paper_2_id
                ELSE paper_1_id
            END
        JOIN batch_inputs bi
            ON paper_1_id = bi.column1 OR paper_2_id = bi.column1
    )
    SELECT co_cited_paper_id, co_citation_count, publication_date, original_paper_id
    FROM RankedResults
    WHERE rank <= ?
    ORDER BY original_paper_id, rank
    """
    cursor.execute(query, (limit,))
    return cursor.fetchall()


# %%
def filter_recommendation(paper_ids, cursor):
    paper_ids = str(paper_ids).replace('[', '(').replace(']', ')')
    query = f"""
    SELECT paper_id  from papers
    WHERE paper_id in {paper_ids}
    ORDER BY citation_count DESC, submitted_date DESC
    LIMIT 10
    """
    cursor.execute(query)
    retList = cursor.fetchall()
    retList =[x[0] for x in retList]
    return retList

# %%
def reccPaper(paper_name):
    connection = sqlite3.connect("papers.db")
    cursor = connection.cursor()

    paper_id = retrieveID(paper_name, cursor)
    
    abstract_id_list = get_similar_abstract(paper_id, cursor,5)
    
    author_id_list = get_similar_authors(paper_id, cursor,5)

    co_citation_list = find_co_citations(paper_id, cursor,5)
    
    combined_list = abstract_id_list + author_id_list + co_citation_list
    
    final_recommendation_list = filter_recommendation(combined_list, cursor)

    connection.commit()
    cursor.close()
    connection.close()
    
    return final_recommendation_list

# %%
def recc_paper_batch(paper_names):
    connection = sqlite3.connect("papers.db")
    cursor = connection.cursor()

    paper_ids = retrieveID_batch(paper_names, cursor)
    
    abstract_id_list = get_similar_abstract_batch(paper_ids, cursor,5)
    
    author_id_list = get_similar_authors_batch(paper_ids, cursor,5)

    co_citation_list = []
    
    for paper_id in paper_ids:
        co_citation_list.extend(find_co_citations(paper_id, cursor,5))
    
    print("ALL",abstract_id_list, author_id_list, co_citation_list)
    
    combined_list = abstract_id_list + author_id_list + co_citation_list
    
    final_recommendation_list = filter_recommendation(combined_list, cursor)

    connection.commit()
    cursor.close()
    connection.close()
    
    return final_recommendation_list

# %%
def evaluate(paper_ids, cursor, input_paper):
    paper_ids = str(paper_ids).replace('[', '(').replace(']', ')')
    query = f"""
    SELECT count(*)
    from papers p, citations c
    WHERE p.paper_id in {paper_ids}
    AND ((from_paper_id = p.paper_id AND to_paper_id = {input_paper}) OR (from_paper_id = {input_paper} AND to_paper_id = p.paper_id)) 
    """
    cursor.execute(query)
    retList = cursor.fetchall()
    cnt = retList[0][0]
    return cnt

# %%
def combine_multiple(paper_list):
    final_results = {}
    for paper in paper_list:
        results = reccPaper(paper)
        for rec in results:
            if rec not in final_results:
                final_results[rec] = 0
            final_results[rec] += 1
    
    ls = []
    for rec in final_results:
        ls.append((final_results[rec],rec))
    
    ls.sort()
    return ls[-10:]




# %%
# reccPaper('Shuffling quantum field theory')

# # %%
# recc_paper_batch(['Shuffling quantum field theory'])

# # %%
# combine_multiple(['Shuffling quantum field theory','Mathematics and Physics of N=2 Strings','Two algebraic properties of thermal quantum field theories'])

# # %%
# cursor.execute("SELECT title from papers LIMIT 10")
# test_ids = [i[0] for i in cursor.fetchall()]


# %%
# print(test_ids)

# %%
# ans = []
# for i in test_ids:
#     print(i)
#     reccPaper(i)
# print(ans)

# %%
# recc_paper_batch(test_ids)

# %%
def find_co_citations_batch(paper_ids, cursor, limit = 30):

    #This query returns top co-citations as a list of tuples [(paper_id, citation_count)] 
    # query = """
    # SELECT 
    #     CASE 
    #         WHEN paper_1_id = ? THEN paper_2_id
    #         ELSE paper_1_id 
    #     END AS co_cited_paper_id,
    #     co_citation_count
    # FROM co_citations
    # WHERE paper_1_id = ? OR paper_2_id = ?
    # ORDER BY co_citation_count DESC
    # """
    query = """
    SELECT 
        CASE 
            WHEN paper_1_id = ? THEN paper_2_id
            ELSE paper_1_id
        END AS co_cited_paper_id,
        co_citation_count,
        pd.publication_date
    FROM co_citations
    JOIN paper_dates pd 
        ON pd.paper_id = CASE 
            WHEN paper_1_id = ? THEN paper_2_id
            ELSE paper_1_id
        END
    WHERE paper_1_id = ? OR paper_2_id = ?
    ORDER BY co_citation_count DESC, 
             pd.publication_date DESC
    LIMIT ?
    """
    query_list = []
    for paper_id in paper_ids:
        query_list.append((paper_id,paper_id,paper_id,paper_id,limit))
    cursor.executemany(query,query_list)
    # cursor.execute(query, (paper_id, paper_id, paper_id, paper_id, limit))
    top_co_citations = cursor.fetchall()
    paper_id_list = [x[0] for x in top_co_citations]
    return paper_id_list
    #Sample Input: 
    #find_co_citations(9201001)
    #Sample Output: ['9201013', '9302014', '9203009', '9201011', '9201033', '9203043',
    #'9208031', '9208046', '9302048', '9303139', '9304011', '9201003', '9202006', '9203030',
    #'9206090', '9307063', '9312210', '9505127', '9201010', '9207020']

# %%
# find_co_citations_batch(test_ids,cursor,5)


