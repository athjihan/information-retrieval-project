import streamlit as st
import pandas as pd
import os
import json
from pathlib import Path
import math

# Import refactored modules
from retriever import InformationRetriever, clean_json_file

# --- Helper functions ---
def make_snippet(text: str, max_words: int = 40) -> str:
    """Create a snippet from text with specified word count."""
    if not text:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."

def get_page(items: list, page: int, page_size: int) -> list:
    """Get items for a specific page."""
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("Sistem Information Retrieval Berita Kompas")

# --- Helper functions for data management ---
@st.cache_data
def load_articles_data(file_path):
    if Path(file_path).exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# --- Main application logic ---
articles_clean_path = clean_json_file

# Load existing data at startup
cleaned_data = load_articles_data(articles_clean_path)

if cleaned_data is None:
    st.warning("Data tidak ditemukan. Pastikan data sudah diproses dan disimpan.")
    st.stop()

PAGE_SIZE = 10

# NEW: session state
if "query" not in st.session_state:
    st.session_state.query = ""
if "results" not in st.session_state:
    st.session_state.results = []
if "page" not in st.session_state:
    st.session_state.page = 1

# Initialize retriever
retriever = InformationRetriever()

if not retriever.searcher:
    st.warning("Sistem retrieval belum siap. Pastikan data sudah diindeks.")
    st.stop()

# Search UI
cols = st.columns([1, 2, 1])
with cols[1]:
    with st.form("search_form", clear_on_submit=False):
        query = st.text_input(
            label="Cari berita",
            value=st.session_state.query,
            placeholder="Masukkan kata kunci (mis. politik, ekonomi, hukum)...",
        )
        submitted = st.form_submit_button("Cari")

if submitted:
    if query.strip():
        with st.spinner("Mencari artikel..."):
            results = retriever.search(query)
        st.session_state.query = query
        st.session_state.results = results or []
        st.session_state.page = 1
    else:
        st.warning("Harap masukkan kata kunci pencarian.")

results = st.session_state.results
total = len(results)

if total == 0 and st.session_state.query:
    st.info("Tidak ada artikel yang ditemukan untuk kueri ini.")

if total > 0:
    page = st.session_state.page
    total_pages = max(1, math.ceil(total / PAGE_SIZE))

    def render_pagination(prefix: str):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("« Sebelumnya", disabled=(page <= 1), key=f"{prefix}_prev"):
                st.session_state.page -= 1
                st.rerun()
        with c2:
            st.markdown(f"Halaman {page} dari {total_pages} — {total} artikel")
        with c3:
            if st.button("Berikutnya »", disabled=(page >= total_pages), key=f"{prefix}_next"):
                st.session_state.page += 1
                st.rerun()

    st.divider()
    render_pagination("top")

    # Hasil per halaman
    for item in get_page(results, page, PAGE_SIZE):
        title = item.get("title", "Tanpa Judul")
        url = item.get("url", "#")
        date = item.get("date", "")
        author = item.get("author", "")
        content = item.get("content", "")

        # Judul yang bisa diklik menuju artikel asli
        st.markdown(f"### [{title}]({url})")

        # Meta info kecil
        meta_bits = [bit for bit in [date or None, author or None] if bit]
        if meta_bits:
            st.caption(" • ".join(meta_bits))

        # Cuplikan konten
        st.write(make_snippet(content, max_words=40))

        st.divider()

    render_pagination("bottom")
