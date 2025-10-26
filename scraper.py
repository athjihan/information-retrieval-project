import requests
from bs4 import BeautifulSoup
import time
import csv
import json
from urllib.parse import urljoin, urlparse
import urllib.robotparser
from tqdm.auto import tqdm 
import random
import os
import datetime  
import shutil 

BASE = "https://indeks.kompas.com"
CATEGORY = "nasional"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
    "Accept-Language": "id,en-US;q=0.9,en;q=0.8",  
    "Referer": "https://indeks.kompas.com/",
}

session = requests.Session()
session.headers.update(HEADERS)

def get_robot_parser(base_url):
    robots_url = urljoin(base_url, "/robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception as e:
        print(f"Gagal baca robots.txt dari {robots_url}: {e}")
    can_fetch = rp.can_fetch(HEADERS["User-Agent"], urljoin(BASE, f"?site={CATEGORY}"))
    print("Robots allow fetch category?", can_fetch)
    return rp

def safe_get(url, retries=3, backoff=1.5):
    for i in range(retries):
        try:
            r = session.get(url, timeout=15)
            if r.status_code == 200:
                return r
            else:
                time.sleep(backoff * (i+1) + random.random())
        except requests.RequestException:
            time.sleep(backoff * (i+1) + random.random())
    return None

def extract_article_links_from_listpage(html, base=BASE):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    # Selector fokus ke daftar artikel indeks (hindari header/sidebar/trending)
    candidates = []
    selectors = [
        "div.article__list a.article__link",
        "h3.article__title a",
        "div.article__box a.article__link",
    ]
    for sel in selectors:
        candidates.extend(soup.select(sel))

    # Fallback
    if not candidates:
        candidates = soup.find_all("a", href=True)

    for a in candidates:
        href = a.get("href", "")
        if not href:
            continue
        full = urljoin(base, href) if href.startswith("/") else href
        parsed = urlparse(full)

        # Ambil hanya artikel kompas (semua subdomain) dengan pola /read/
        if parsed.netloc.endswith("kompas.com") and "/read/" in parsed.path:
            if any(bad in full for bad in ["komentar", "copy", "/tag/"]):
                continue
            links.add(full.split("?")[0])

    return list(links)

def parse_article(html, url):
    soup = BeautifulSoup(html, "html.parser")

    title = None
    if soup.find("meta", property="og:title"):
        title = soup.find("meta", property="og:title").get("content", None)
    if not title and soup.title:
        title = soup.title.get_text().strip()

    date = None
    meta_date = soup.find("meta", {"property":"article:published_time"}) \
                or soup.find("meta", {"name":"pubdate"}) \
                or soup.find("meta", {"name":"date"})
    if meta_date:
        date = meta_date.get("content", None)
    if not date:
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            date = time_tag.get("datetime")

    author = None
    meta_author = soup.find("meta", {"name":"author"}) \
                  or soup.find("meta", {"property":"article:author"})
    if meta_author:
        author = meta_author.get("content", None)

    def extract_content(soup_obj):
        content = []
        article_el = soup_obj.find('article') or soup_obj.find('div', class_='read__content')
        if article_el:
            for p in article_el.find_all("p"):
                txt = p.get_text(strip=True)
                if txt:
                    content.append(txt)
        else:
            for p in soup_obj.find_all("p"):
                txt = p.get_text(strip=True)
                if txt and len(txt) > 50:
                    content.append(txt)
        return content

    content = extract_content(soup)

    pagination = soup.find("div", class_="paging__wrap")
    if pagination:
        page_links = []
        for a in pagination.find_all("a", href=True):
            if "page" in a["href"]:
                page_links.append(urljoin(url, a["href"]))
        page_links = sorted(set(page_links))
        for link in page_links:
            r = safe_get(link)
            if r:
                soup_page = BeautifulSoup(r.text, "html.parser")
                content.extend(extract_content(soup_page))
                time.sleep(1 + random.random()*0.8)

    tags = []
    tag_container = soup.find('div', class_='tags') or \
                    soup.find('ul', class_='tags') or \
                    soup.find('div', class_='tag-cloud')
    if tag_container:
        for a in tag_container.find_all('a', href=True):
            tags.append(a.get_text(strip=True))

    return {
        "url": url,
        "title": title,
        "date": date,
        "author": author,
        "content": "\n\n".join(content).strip(),
        "tags": tags
    }

def scrape_articles(base_url, category, max_articles=400, max_pages_per_day=8, max_days=60, start_date=None):
    rp = get_robot_parser(base_url)

    collected_links = []
    seen_links = set()

    # tanggal mulai: hari ini atau dari argumen
    cur_date = start_date or datetime.date.today()
    days_scanned = 0

    # Progress bar: hari dan link unik
    days_pbar = tqdm(total=max_days, desc="Days scanned", dynamic_ncols=True, position=0, leave=True)
    links_pbar = tqdm(total=max_articles, desc="Unique links", dynamic_ncols=True, position=1, leave=True)

    while len(collected_links) < max_articles and days_scanned < max_days:
        page = 1
        no_new_on_day = 0
        # loop halaman untuk tanggal cur_date
        while len(collected_links) < max_articles and page <= max_pages_per_day:
            list_url = f"{base_url}/?site={category}&date={cur_date.strftime('%Y-%m-%d')}&page={page}"
            res = safe_get(list_url)
            if not res:
                tqdm.write(f"Gagal ambil list page: {list_url}")
                break

            links = extract_article_links_from_listpage(res.text, base=base_url)
            new_links = [l for l in links if l not in seen_links]

            if new_links:
                for l in new_links:
                    seen_links.add(l)
                    collected_links.append(l)
                links_pbar.update(len(new_links))
                links_pbar.set_postfix(date=str(cur_date), page=page, new=len(new_links), total=len(collected_links))
                no_new_on_day = 0
            else:
                no_new_on_day += 1
                # jika 2 halaman berturut-turut tidak ada link baru, pindah hari
                if no_new_on_day >= 2:
                    break

            page += 1
            time.sleep(0.6 + random.random()*0.8)

        days_scanned += 1
        days_pbar.update(1)
        # mundur 1 hari
        cur_date = cur_date - datetime.timedelta(days=1)

    days_pbar.close()
    links_pbar.close()
    print(f"Total links collected: {len(collected_links)}")

    # Fetch artikel
    articles = []
    total_to_fetch = min(len(collected_links), max_articles)
    for url in tqdm(collected_links[:total_to_fetch], desc="Fetching Articles", dynamic_ncols=True, leave=True):
        # periksa robots (opsional; robots dari host indeks mungkin tidak merefleksikan subdomain lain)
        try:
            if not rp.can_fetch(HEADERS["User-Agent"], url):
                tqdm.write(f"robots disallow: {url}")
                continue
        except Exception:
            pass

        r = safe_get(url)
        if not r:
            tqdm.write(f"Gagal ambil artikel: {url}")
            continue
        parsed = parse_article(r.text, url)
        articles.append(parsed)
        time.sleep(0.8 + random.random()*1.2)

    return articles

if __name__ == "__main__":
    print("Starting scraping process...")
    
    # Buat folder data jika belum ada
    os.makedirs("data", exist_ok=True)
    
    out_json = "data/kompas_nasional_articles.json"  # ✅ Pindah ke folder data
    out_csv = "data/kompas_nasional_articles.csv"
    
    # CEK APAKAH FILE SUDAH ADA
    if os.path.exists(out_json) and os.path.exists(out_csv):
        print(f"\n✅ File hasil scraping sudah ada:")
        print(f"   - {out_json}")
        print(f"   - {out_csv}")
        
        choice = input("\nScraping ulang? (y/n): ").strip().lower()
        if choice != 'y':
            print("Menggunakan data yang sudah ada.")
            exit(0)
        else:
            # Hapus folder data jika user memilih scraping ulang
            if os.path.exists("data"):
                print("Menghapus folder 'data' untuk memulai ulang...")
                shutil.rmtree("data")
                os.makedirs("data", exist_ok=True) # Buat ulang folder data yang kosong
    
    # BARU SCRAPING JIKA DIPERLUKAN
    articles_data = scrape_articles(BASE, CATEGORY, max_articles=400)

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=2)

    keys = ["url","title","date","author","content","tags"]
    with open(out_csv, "w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for a in articles_data:
            row = {k: a.get(k, "") for k in keys}
            row["tags"] = ";".join(row.get("tags",[]))
            writer.writerow(row)

    print(f"Done. saved: {out_json}, {out_csv}")
