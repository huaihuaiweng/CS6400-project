# Project Setup
Our project consists of two components:  
1. the initial setup / loading of data into the vector DB and relational DB
2. the interface component utilizing streamlit

## Setup Instructions

### Installing Necessary Requirements:
1. Our team utilized ipynb files to allow for better setup visualization: ipynb documentation can be found: https://code.visualstudio.com/docs/datascience/jupyter-notebooks, https://jupyter.org/
2. This can be opened by first creating an environment with `python3 -m venv env` <br>
3. Followed by `source env/bin/activate` <br>
4. Our application uses the latest version of the Ollama language model which can be found https://ollama.com/
5. `pip install -r requirements.txt` will install all the dependencies necessary for our application to function
    Additional version requirements for our project can be found in this requirements.txt file
6. For our vector DB we utilize ChromaDB found https://www.trychroma.com/ and for our relational database we utilize SQLite3 found https://docs.python.org/3/library/sqlite3.html
   Both Databases are part of the pip install process and do not require further management
   
### Database Download Instructions

1. Pull the Github Code into a local repository
2. Download the papers.db file located at https://gtvault-my.sharepoint.com/:u:/g/personal/xweng42_gatech_edu/EaPi6ZNz96ZCpD7J27BEHLMBOoVikGB8ehOBgY5vzfDEhQ into the CS6400-project folder
3. Download the vector data folder located https://drive.google.com/drive/folders/1iPM551nLRMC2pD0EBWrqfgwT-QSAMAF7?usp=drive_link which includes the full data information
   These files were stored outside of GitHub due to their large sizes being restricted by GitHub upload limits

### Data Loading

The full databases already exist within the papers.db downloaded from the gatech OneDrive and folder files located at the google drive aand therefore further data loading and data preprocessing is not actually required

If the daatabase download steps are skipped, data loading and data preprocessing instructions can be followed to load the databases locally
  
To (optionally) test preprocessing locally:
The original dataset is available at https://snap.stanford.edu/data/cit-HepTh.html where the abstract information tar can be downloaded: cit-HepTh-abstracts.tar.gz  
Extract the tar and gz files and save the cit-HepTh-abstracts folder in the 
repository

A sample dataset under 5mb cannot be provided as using a set of those file limits would lead to improper citations and co-citation graphs with missing data

Example of datafile:
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

To initialize files into the vector and relational Databases:
1. Run the cells in relational_db_upload.ipynb to load into the relational DB
2. Run the cells in vector_db_preprocess.ipynb to load into the vector DB

relational_paper_db.ipynb was utilized for our local testing of queries and does not need to be run for data preprocessing

Note that the collections referenced in the vector DB already exist in the current GitHub

### Running the Project
Backend Running of files was mostly explained in the data preprocessing
Funtionalities of adding and deleting files can be tested with the cells of insert_delete_paper.ipynb

project.ipynb contains our visualizations and tests for our reports. The cells can be run on the full dataset and full databases to see the effectiveness of our improvements to the querying.

To run the front end UI:
streamlit run app/Home.py


## References


