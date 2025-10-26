# Evaluasi Precision dan Recall untuk BM25 (Pyserini)
import pandas as pd
from retriever import InformationRetriever

# Query yang digunakan
queries = [
    "politik",
    "prabowo tetapkan ikn jadi ibukota politik 2028",
    "korupsi anggaran",
    "ekonomi indonesia",
    "pemilu presiden"
]

# Fungsi bantu untuk cek relevansi sederhana
import re

def is_relevant(query, content):
    if not content:
        return False

    # Ubah query jadi kumpulan token unik
    tokens = re.findall(r'\w+', query.lower())  # ambil kata aja
    if not tokens:
        return False

    # Bentuk pola regex OR seperti di VSCode, misal (politik|ikn|prabowo)
    pattern = r'\b(' + '|'.join(map(re.escape, tokens)) + r')\b'

    # Cocokkan di konten (case-insensitive, multiline)
    return re.search(pattern, content, flags=re.IGNORECASE) is not None


# Fungsi utama evaluasi retrieval
def evaluate_retrieval(queries, top_k=20):
    retriever = InformationRetriever()
    if not retriever.searcher:
        print("Retriever tidak siap. Pastikan index sudah dibuat.")
        return pd.DataFrame()

    eval_results = []

    for q in queries:
        results = retriever.search(q, k=top_k)  # gunakan Pyserini BM25 via retriever
        relevant = sum(1 for r in results if is_relevant(q, r.get("content", "")))

        # Hitung jumlah dokumen relevan di seluruh dataset
        total_relevant = sum(is_relevant(q, a.get("content", "")) for a in retriever.meta_lookup.values())
        precision = relevant / len(results) if len(results) > 0 else 0
        recall = relevant / total_relevant if total_relevant > 0 else 0

        eval_results.append({
            "query": q,
            "precision": precision,
            "recall": recall,
            "total_relevant_docs": total_relevant,
            "retrieved_relevant_docs": relevant
        })

        print(f"\nQuery: {q}")
        print(f"Top {top_k} hasil ditemukan: {len(results)}")
        print(f"Relevan di hasil: {relevant}")
        print(f"Total relevan di dataset: {total_relevant}")
        print(f"Precision: {precision:.2f}")  
        print(f"Recall: {recall:.2f}")      

    # Rangkuman dalam tabel
    df_eval = pd.DataFrame(eval_results)
    if not df_eval.empty:
        print("\n=== Rata-rata Evaluasi ===")
        print(f"Average Precision: {df_eval['precision'].mean():.2f}")
        print(f"Average Recall: {df_eval['recall'].mean():.2f}")

    return df_eval

if __name__ == "__main__":
    df_eval = evaluate_retrieval(queries, top_k=20)
    print("\nHasil evaluasi:")
    print(df_eval)