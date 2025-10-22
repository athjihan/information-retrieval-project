import re
import json
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords
import nltk
import os
import subprocess
import sys
import logging
try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# Download the stopwords corpus if not already downloaded
try:
    stopwords.words("indonesian")
except LookupError:
    nltk.download('stopwords')

# ====== Setup stopwords & stemmer ======
factory = StemmerFactory()
stemmer = factory.create_stemmer()
stop_words = set(stopwords.words("indonesian"))
custom_stop = {"baca", "juga", "halaman", "kompas"}
stop_words = stop_words.union(custom_stop)

def preprocess_text(text):
    if not text:
        return []
    # 1. lowercase
    text = text.lower()
    # 2. hapus html tags
    text = re.sub(r"<.*?>", " ", text)
    # 3. hapus pola "baca juga"
    text = re.sub(r"baca juga.*", " ", text)
    # 4. hapus .com
    text = re.sub(r"\.com", " ", text)
    # 5. hapus angka & simbol
    text = re.sub(r"[^a-z\s]", " ", text)
    # 6. tokenisasi
    tokens = text.split()
    # 7. stopword removal
    tokens = [t for t in tokens if t not in stop_words]
    # 8. stemming
    tokens = [stemmer.stem(t) for t in tokens]
    return tokens

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.info("Preprocessing dimulai")

    in_file = "data/kompas_nasional_articles.json"   # ✅ Dari folder data
    out_file = "data/kompas_nasional_clean.json"     # ✅ Simpan di folder data

    # CEK FILE INPUT
    if not os.path.exists(in_file):
        logging.warning(f"{in_file} not found.")
        choice = input("Jalankan scraper.py dulu? (y/n): ").strip().lower()
        if choice == 'y':
            logging.info("Menjalankan scraper.py...")
            subprocess.run([sys.executable, "scraper.py"])
            if not os.path.exists(in_file):
                logging.error(f"Scraping gagal atau dibatalkan. File {in_file} tidak ditemukan.")
                exit(1)
        else:
            logging.info("Program dihentikan. Silakan jalankan scraper.py terlebih dahulu.")
            exit(1)

    # CEK FILE OUTPUT - hindari preprocessing ulang
    if os.path.exists(out_file):
        logging.info(f"File hasil preprocessing sudah ada: {out_file}")
        choice = input("Preprocessing ulang? (y/n): ").strip().lower()
        if choice != 'y':
            logging.info("Menggunakan data yang sudah ada.")
            exit(0)

    from time import perf_counter
    t0 = perf_counter()

    # PROSES PREPROCESSING
    with open(in_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    logging.info(f"Memproses {len(data)} artikel dari {in_file} → {out_file}")
    if tqdm is None:
        logging.warning("tqdm tidak terpasang. Jalankan: pip install tqdm (progress bar nonaktif sementara)")

    cleaned = []
    total = len(data)
    iterator = enumerate(data)
    if tqdm is not None:
        iterator = tqdm(enumerate(data), total=total, desc="Preprocessing", unit="artikel")

    for idx, art in iterator:
        raw_text = art.get("content", "")
        tokens = preprocess_text(raw_text)
        art["tokens"] = tokens
        cleaned.append(art)

        if idx == 0:
            block_lines = []
            block_lines.append("="*50)
            block_lines.append("SEBELUM :")
            block_lines.append((raw_text[:200] + "...\n") if raw_text else "(kosong)\n")
            block_lines.append("SESUDAH :")
            n_per_line = 10
            pretty_tokens = []
            pretty_tokens.append("[")
            for i in range(0, len(tokens), n_per_line):
                line = ", ".join(tokens[i:i+n_per_line])
                if i + n_per_line < len(tokens):
                    pretty_tokens.append(line + ",")
                else:
                    pretty_tokens.append(line)
            pretty_tokens.append("]")
            block_lines.extend(pretty_tokens)
            block_lines.append("="*50)
            text_block = "\n".join(block_lines)
            if tqdm is not None:
                tqdm.write(text_block)
            else:
                print(text_block)

        # Fallback progress jika tqdm tidak ada
        if tqdm is None and ((idx + 1) % 50 == 0 or (idx + 1) == total):
            print(f"Progress: {idx+1}/{total} artikel")

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    elapsed = perf_counter() - t0
    logging.info(f"Selesai. Preprocessed {len(cleaned)} artikel → {out_file} (durasi: {elapsed:.2f}s)")
