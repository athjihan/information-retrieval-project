from pyserini.search.lucene import LuceneSearcher
import json
import pandas as pd
from pathlib import Path
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords

# Define local paths for data and index, consistent with indexer.py
DATA_DIR = Path("./data")
INDEX_DIR = Path("./index_bm25")

# Path to preprocessed file for metadata lookup
clean_json_file = "data/kompas_nasional_clean.json"

# ====== Setup preprocessing (sama seperti di preprocessor.py) ======
factory = StemmerFactory()
stemmer = factory.create_stemmer()
stop_words = set(stopwords.words("indonesian"))
custom_stop = {"baca", "juga", "halaman", "kompas"}
stop_words = stop_words.union(custom_stop)

def preprocess_query(text):
    """
    Preprocess query dengan cara yang sama seperti dokumen
    """
    if not text:
        return ""
    # 1. lowercase
    text = text.lower()
    # 2. hapus angka & simbol
    text = re.sub(r"[^a-z\s]", " ", text)
    # 3. tokenisasi
    tokens = text.split()
    # 4. stopword removal
    tokens = [t for t in tokens if t not in stop_words]
    # 5. stemming
    tokens = [stemmer.stem(t) for t in tokens]
    # 6. gabung kembali jadi string
    return " ".join(tokens)

class InformationRetriever:
    def __init__(self):
        self.searcher = None
        self.meta_lookup = {}
        self._initialize_retriever()

    def _initialize_retriever(self):
        if not INDEX_DIR.exists():
            print(f"Error: Index directory '{INDEX_DIR}' not found. Please run indexer.py first.")
            return

        try:
            self.searcher = LuceneSearcher(str(INDEX_DIR))
            self.searcher.set_bm25(k1=0.9, b=0.4)
            print(f"✅ Pyserini searcher initialized with index: {INDEX_DIR}")
        except Exception as e:
            print(f"Error initializing Pyserini searcher: {e}")
            self.searcher = None
            return

        # Load original data for metadata (title, date, url)
        clean_json_path = clean_json_file
        if not Path(clean_json_path).exists():
            print(f"Warning: Metadata file '{clean_json_path}' not found. Search results will have limited metadata.")
            return

        with open(clean_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.meta_lookup = {art.get("url", str(idx)): art for idx, art in enumerate(data)}
        print(f"✅ Metadata loaded for {len(self.meta_lookup)} articles.")

    def search(self, query, k=20, preprocess=True):
        if not self.searcher:
            print("Retriever not initialized. Cannot perform search.")
            return []

        # PREPROCESSING QUERY
        if preprocess:
            query = preprocess_query(query)
        
        if not query.strip():
            print("⚠️  Query kosong setelah preprocessing!")
            return []

        hits = self.searcher.search(query, k=k)
        results = []
        for hit in hits:
            docid = hit.docid
            score = hit.score
            meta = self.meta_lookup.get(docid, {})
            content = meta.get("content", "")
            results.append({
                "score": score,
                "title": meta.get("title", "[NO TITLE]"),
                "date": meta.get("date", ""),
                "author": meta.get("author", ""),
                "url": meta.get("url", docid),
                "content": content
            })
        return results

if __name__ == "__main__":
    # Example usage:
    retriever = InformationRetriever()

    queries = [
        "politik",
        "prabowo tetapkan ikn jadi ibukota politik 2028",
        "korupsi anggaran",
        "ekonomi indonesia",
        "pemilu presiden"
    ]

    for q in queries:
        print("="*80)
        print(f"Query: {q}")
        print("="*80)
        results = retriever.search(q, preprocess=True)  # Aktifkan preprocessing

        print(f"Jumlah artikel relevan: {len(results)}\n")

        if results:
            df_results = pd.DataFrame(results)
            print(df_results[['score', 'title', 'date', 'url']].head(20))  # Tampilkan top 20
        else:
            print("Tidak ada artikel yang ditemukan untuk kueri ini.")
        print("\n")
