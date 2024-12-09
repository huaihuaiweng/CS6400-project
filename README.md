# Project Setup
Our project consists of two components:
1. the initial setup / loading of data into the vector DB and relational DB
2. the interface component utilizing streamlit

## Setup Instructions

### Dependency Preparation Instructions

1. Pull the Github Code into a local repository
2. Download the papers.db file located at https://gtvault-my.sharepoint.com/:u:/g/personal/xweng42_gatech_edu/EaPi6ZNz96ZCpD7J27BEHLMBOoVikGB8ehOBgY5vzfDEhQ into the CS6400-project folder
3. Download the vector data folder located https://drive.google.com/drive/folders/1iPM551nLRMC2pD0EBWrqfgwT-QSAMAF7?usp=drive_link which includes the full data information
   These files were stored outside of GitHub due to their large sizes being restricted by GitHub upload limits

To test Data Loading locally
1. Our team utilized ipynb files to allow for better setup visualization: ipynb documentation can be found: https://code.visualstudio.com/docs/datascience/jupyter-notebooks, https://jupyter.org/
2. This can be opened by first creating an environment with `python3 -m venv env` <br>
3. Followed by `source env/bin/activate` <br>
4. Our application uses the latest version of the Ollama language model which can be found https://ollama.com/
5. `pip install -r requirements.txt` will install all the dependencies necessary for our application to function
    Additional version requirements for our project can be found in this requirements.txt file
6. For our vector DB we utilize ChromaDB found https://www.trychroma.com/ and for our relational database we utilize SQLite3 found https://docs.python.org/3/library/sqlite3.html
   Both Databases are part of the pip install process and do not require further management

### Data Loading

The full datasets already exist within the papers.db downloaded from the gatech OneDrive and folder files located at the google drive
The original dataset is available at https://snap.stanford.edu/data/cit-HepTh.html where the abstract information tar can be downloaded: cit-HepTh-abstracts.tar.gz
Extract the tar and gz files and save the cit-HepTh-abstracts folder in the repository
Example of datafile

```
Paper: hep-th/0002031
From: Maulik K. Parikh 
Date: Fri, 4 Feb 2000 17:04:51 GMT   (10kb)

Title: Confinement and the AdS/CFT Correspondence
Authors: D. S. Berman and Maulik K. Parikh
Comments: 12 pages, 1 figure, RevTeX
Report-no: SPIN-1999/25, UG-1999/42
Journal-ref: Phys.Lett. B483 (2000) 271-276
\\
  We study the thermodynamics of the confined and unconfined phases of
superconformal Yang-Mills in finite volume and at large N using the AdS/CFT
correspondence. We discuss the necessary conditions for a smooth phase
crossover and obtain an N-dependent curve for the phase boundary.
\\
```
### Data Preprocessing
To add files into the vector and relational Databases:
Run the cells in neo4j_paper_upload.ipynb
Run the cells in relational_db_upload.ipynb
Run the cells in relational_paper_db.ipynb

Note that the collections referenced in the vector DB already exist in the current GitHub

### Running the Project
Backend Running of files was mostly explained in the data preprocessing
Funtionalities of adding and deleting files can be tested with the cells of insert_delete_paper.ipynb

To run the front end UI:
streamlit run app/Home.py


## References
https://docs.trychroma.com/guides - Usage guide for chromaDB all code written is our own
https://docs.python.org/3/library/sqlite3.html - SQLite3 Documentation Guide
https://docs.streamlit.io/get-started - streamlit documentation guide

