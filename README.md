# Project Setup
Our project consists of two components:
1. the initial setup / loading of data into the vector DB and relational DB
2. the interface component utilizing streamlit

## Setup Instructions

### Data Loading Instructions

1. Pull the Github Code into a local repository
2. Download the papers.db file located at https://gtvault-my.sharepoint.com/:u:/g/personal/xweng42_gatech_edu/EaPi6ZNz96ZCpD7J27BEHLMBOoVikGB8ehOBgY5vzfDEhQ into the CS6400-project folder
3. Download the full data folder located https://drive.google.com/drive/folders/1iPM551nLRMC2pD0EBWrqfgwT-QSAMAF7?usp=drive_link which includes the full data information
   These files were stored outside of GitHub due to their large sizes being restricted by GitHub upload limits

To test Data Loading locally
1. Our application uses the latest version of the Ollama language model which can be found https://ollama.com/
2. `pip install -r requirements.txt` will install all the dependencies necessary for our application to function
3. For our vector DB we utilize ChromaDB found https://www.trychroma.com/ and for our relational database we utilize SQLite3 found https://docs.python.org/3/library/sqlite3.html
   Both Databases are part of the pip install process and do not require further management
4. For better visualization while our team made changes and updates to the system, our project utilizes ipynb files for the initial datasetup
   This can be opened by first creating an environment with `python3 -m venv env` <br>
5. Followed by `source env/bin/activate` <br>
