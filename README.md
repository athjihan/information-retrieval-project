# Information Retrieval Project

This project implements an information retrieval system, likely involving web scraping, text preprocessing, indexing using BM25, and a Streamlit-based user interface for searching.
Team:
1. Athaya Naura Khalilah	    (23/512716/PA/21899)
2. Rizka Nurdiana				(23/513519/PA/21941)
3. Nasya Putri Raudhah Dahlan	(23/513931/PA/21967)
4. Jihan Dwi Athanaya			(23/518584/PA/22255)


## Installation

To set up the project, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/athjihan/information-retrieval-project.git
    cd information-retrieval-project
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```

4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run the Program

There are two main ways to run this program:

### 1. Starting from Scraping and Indexing

This approach covers the full pipeline, from collecting data to building the search index.

1.  **Activate your virtual environment** (if not already active):
    *   **Windows:** `.venv\Scripts\activate`
    *   **macOS/Linux:** `source .venv/bin/activate`

2.  **Run the scraper to collect data:**
    ```bash
    python scraper.py
    ```
    This will likely populate the `data/` directory with raw articles.

3.  **Run the preprocessor to clean and prepare the data:**
    ```bash
    python preprocessor.py
    ```
    This step processes the scraped data for indexing.

4.  **Run the indexer to build the BM25 index:**
    ```bash
    python indexer.py
    ```
    This will create the search index in the `index_bm25/` directory.

5.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
    Your web browser should automatically open to the Streamlit application.

### 2. Running the Streamlit Application Directly (assuming data and index are ready)

If you already have the `data/` and `index_bm25/` directories populated with processed data and a built index, you can directly launch the Streamlit application.

1.  **Activate your virtual environment** (if not already active):
    *   **Windows:** `.venv\Scripts\activate`
    *   **macOS/Linux:** `source .venv/bin/activate`

2.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
    Your web browser should automatically open to the Streamlit application, where you can start searching.
