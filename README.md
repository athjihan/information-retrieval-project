# 🔍 Information Retrieval Project

This project implements an **Information Retrieval (IR) system** using data scraped from **Kompas.com** — a national news domain in Indonesia 🇮🇩.
The system performs **web scraping**, **text preprocessing**, **BM25 indexing**, and provides an **interactive Streamlit web interface** for searching and exploring news articles efficiently.

---

## 👥 Team Members

1. 👩‍💻 **Athaya Naura Khalilah** — 23/512716/PA/21899
2. 👩‍💻 **Rizka Nurdiana** — 23/513519/PA/21941
3. 👩‍💻 **Nasya Putri Raudhah Dahlan** — 23/513931/PA/21967
4. 👩‍💻 **Jihan Dwi Athanaya** — 23/518584/PA/22255

---

## 🧭 Project Overview

### 📑 1. Web Scraping using BeautifulSoup4

Scrapes news articles from **Kompas.com** using to collect real-world Indonesian-language data for the search system. The scraped data includes titles, content, and publication dates.

### 🧹 2. Text Preprocessing using Sastrawi

Cleans and normalizes the text using by removing unnecessary symbols, stopwords, and applying tokenization or stemming for better retrieval performance.

### 🧮 3. Indexing with BM25

Builds an inverted index using the **BM25 ranking algorithm using Pyserini** to enable relevance-based document retrieval. This index allows fast and accurate search queries.

### 💬 4. Searching via Streamlit

Provides a **Streamlit-based user interface** for entering search queries, viewing ranked results, and exploring matching news content interactively.

🔁 **End-to-end workflow:**
`scraper.py` → `preprocessor.py` → `indexer.py` → `app.py`

---

## ⚙️ Installation

Follow these steps to set up and run the project locally:

1. **📦 Clone the repository:**

   ```bash
   git clone https://github.com/athjihan/information-retrieval-project.git
   cd information-retrieval-project
   ```

2. **🐍 Create a virtual environment (recommended):**

   ```bash
   python -m venv .venv
   ```

3. **🚀 Activate the virtual environment:**

   * **Windows:**

     ```bash
     .venv\Scripts\activate
     ```
   * **macOS/Linux:**

     ```bash
     source .venv/bin/activate
     ```

4. **📚 Install required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ How to Run the Program

There are **two main ways** to run this project depending on your setup:

---

### 🧩 Option 1: Full Pipeline (Scraping → Preprocessing → Indexing → UI)

1. **Activate your virtual environment:**

   * Windows: `.venv\Scripts\activate`
   * macOS/Linux: `source .venv/bin/activate`

2. **📰 Run the scraper:**

   ```bash
   python scraper.py
   ```

   ➜ Collects articles from Kompas.com and stores them in the `data/` directory.

3. **🧹 Run the preprocessor:**

   ```bash
   python preprocessor.py
   ```

   ➜ Cleans and structures text data for indexing.

4. **🗂️ Build the BM25 index:**

   ```bash
   python indexer.py
   ```

   ➜ Creates the searchable index inside the `index_bm25/` folder.

5. **🌐 Launch the Streamlit interface:**

   ```bash
   streamlit run app.py
   ```

   ➜ Opens the web app in your default browser for searching.

---

### 💡 Option 2: Run Only the Streamlit App

If you already have the prepared `data/` and `index_bm25/` directories, you can skip scraping and indexing.

1. **Activate your virtual environment:**

   * Windows: `.venv\Scripts\activate`
   * macOS/Linux: `source .venv/bin/activate`

2. **🚀 Run the Streamlit app directly:**

   ```bash
   streamlit run app.py
   ```

   ➜ Instantly access the search interface and explore the indexed articles 🔎

---

## 🧰 Tech Stack

* 🐍 **Python** — core implementation
* 📰 **Kompas.com** — data source (scraping target)
* ⚖️ **BM25** — document ranking algorithm
* 🎛️ **Streamlit** — web-based user interface
* 🧹 **NLTK / Sastrawi** — text preprocessing tools

---

## 📂 Project Structure

```
information-retrieval-project/
│
├── app.py                # Streamlit interface
├── scraper.py            # Web scraping script (Kompas.com)
├── preprocessor.py       # Data cleaning and normalization
├── indexer.py            # BM25 indexing module
│
├── data/                 # Raw or preprocessed text data
├── index_bm25/           # Stored index files
├── requirements.txt      # Dependencies list
└── README.md             # Project documentation
```

---

✨ **In summary:**
This project demonstrates the full lifecycle of an **Information Retrieval system**, from collecting real-world data to providing an interactive search experience — all using the Indonesian news domain **Kompas.com** 🇮🇩

---

Apakah kamu mau aku tambahkan juga **contoh hasil tampilan Streamlit UI** (misalnya hasil pencarian dan snippet berita) dalam bentuk tabel atau screenshot placeholder di README-nya biar lebih menarik lagi?
