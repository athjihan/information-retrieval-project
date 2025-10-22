import os
import json
import sys
import subprocess
from pathlib import Path

# Define local paths for data and index
DATA_DIR = Path("./data")
INDEX_DIR = Path("./index_bm25")

# Ensure data and index directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Path sudah konsisten
in_file = "data/kompas_nasional_clean.json"
jsonl_path = DATA_DIR / "kompas_nasional_clean.jsonl"

def create_jsonl_for_pyserini(input_json_file, output_jsonl_file):
    """
    Loads preprocessed JSON data and converts it to JSONL format for Pyserini.
    """
    if not Path(input_json_file).exists():
        print(f"⚠️  Error: Input file '{input_json_file}' not found.")
        choice = input("Jalankan preprocessor.py dulu? (y/n): ").strip().lower()
        if choice == 'y':
            print("Menjalankan preprocessor.py...")
            subprocess.run([sys.executable, "preprocessor.py"])
            if not Path(input_json_file).exists():
                print(f"❌ Preprocessing gagal atau dibatalkan. File {input_json_file} tidak ditemukan.")
                return 0
        else:
            print("Program dihentikan. Silakan jalankan preprocessor.py terlebih dahulu.")
            return 0

    with open(input_json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(output_jsonl_file, "w", encoding="utf-8") as f:
        for idx, art in enumerate(data):
            title = art.get("title", "")
            tokens = " ".join(art.get("tokens", []))

            rec = {
                "id": art.get("url", str(idx)),
                "contents": f"{title} {tokens}".strip()
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"✅ JSONL for Pyserini created: {output_jsonl_file}")
    print(f"Number of documents: {len(data)}")
    return len(data)

def index_documents(jsonl_input_path, index_output_path):
    """
    Indexes documents using Pyserini's command-line interface.
    """
    # CEK APAKAH INDEX SUDAH ADA
    if index_output_path.exists() and any(index_output_path.iterdir()):
        print(f"\n✅ Index sudah ada di: {index_output_path}")
        choice = input("Indexing ulang? (y/n): ").strip().lower()
        if choice != 'y':
            print("Menggunakan index yang sudah ada.")
            return
    
    print(f"Starting Pyserini indexing to {index_output_path}...")
    
    # Clear existing index if it exists
    if index_output_path.exists():
        import shutil
        shutil.rmtree(index_output_path)
        print(f"Removed existing index at {index_output_path}")

    # Use Pyserini's command-line indexing (same as Colab but for Windows)
    cmd = [
        sys.executable, "-m", "pyserini.index.lucene",
        "--collection", "JsonCollection",
        "--input", str(DATA_DIR.resolve()),  # directory containing JSONL file
        "--index", str(index_output_path.resolve()),
        "--generator", "DefaultLuceneDocumentGenerator",
        "--threads", "1",
        "--storePositions", "--storeDocvectors", "--storeRaw"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Pyserini indexing complete. Index saved to: {index_output_path}")
        print(result.stdout)
    else:
        print(f"❌ Indexing failed with error:")
        print(result.stderr)
        print(result.stdout)


if __name__ == "__main__":
    input_json_file_path = "data/kompas_nasional_clean.json"

    # Create JSONL file
    num_docs = create_jsonl_for_pyserini(input_json_file_path, jsonl_path)

    if num_docs > 0:
        # Index the documents
        index_documents(jsonl_path, INDEX_DIR)
    else:
        print("No documents to index. Please check preprocessing step.")
