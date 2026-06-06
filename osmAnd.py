#!/usr/bin/env python3
import re
import os
import sys
import argparse
import requests
import zipfile
from tqdm import tqdm
from io import BytesIO
from bs4 import BeautifulSoup

# This file creates the function fetch_and_process which grabs a list of relevant map zips, downloads them, then extracts the maps, and updates the name. 

def fetch_listing(listing_url, session=None, timeout=30):
    sess = session or requests.Session()
    r = sess.get(listing_url, timeout=timeout)
    r.raise_for_status()
    return r.text

def extract_zip_links_bs(html_text, name, listing_url):
    """
    Use BeautifulSoup to extract hrefs to .zip files and return list of (filename, absolute_url)
    whose filename matches `name` (case-insensitive).
    """
    escaped = re.escape(name)
    name_re = re.compile(escaped, re.IGNORECASE)

    soup = BeautifulSoup(html_text, "html.parser")
    anchors = soup.find_all("a", href=True)
    base_root_match = re.match(r'^(https?://[^/]+)', listing_url)
    base_root = base_root_match.group(1) if base_root_match else listing_url
    base_dir = listing_url.rsplit('/', 1)[0] + '/'

    results = []
    for a in anchors:
        href = a.get("href")
        if not href:
            continue
        if not href.lower().endswith(".zip"):
            continue
        # normalize to absolute URL
        if href.lower().startswith(("http://", "https://")):
            url = href
        elif href.startswith("/"):
            url = base_root + href
        else:
            url = base_dir + href
        fname = url.rsplit("/", 1)[-1]
        if name_re.search(fname):
            results.append((fname, url))
    return results

# def download_file(url, session=None, timeout=30):
    """
    Download URL without using a progress bar.
    """
#     sess = session or requests.Session()
#     r = sess.get(url, stream=True, timeout=timeout)
#     r.raise_for_status()
#     return r.content

def download_file(url, session=None, timeout=30, chunk_size=8192):
    """
    Download URL and return bytes. Shows a tqdm progress bar if content-length present.
    """
    sess = session or requests.Session()
    with sess.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        chunks = []
        if total:
            with tqdm(total=total, unit='B', unit_scale=True, desc=os.path.basename(url)) as pbar:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if not chunk:
                        continue
                    chunks.append(chunk)
                    pbar.update(len(chunk))
        else:
            # unknown size — still show a spinner-like progress via tqdm without total
            with tqdm(unit='B', unit_scale=True, desc=os.path.basename(url)) as pbar:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if not chunk:
                        continue
                    chunks.append(chunk)
                    pbar.update(len(chunk))
        return b"".join(chunks)

# def extract_zip_bytes_to_folder(zip_bytes, target_folder):
    """
    Zip extraction without a progress bar.
    """
#     os.makedirs(target_folder, exist_ok=True)
#     extracted = []
#     with zipfile.ZipFile(BytesIO(zip_bytes)) as z:
#         z.extractall(target_folder)
#         for zi in z.infolist():
#             extracted.append(os.path.join(target_folder, zi.filename))
#     return extracted

def extract_with_byte_progress(zip_bytes, target_folder, chunk_size=8192):
    """
    Zip extraction with a tqdm progress bar.
    """
    os.makedirs(target_folder, exist_ok=True)
    with zipfile.ZipFile(BytesIO(zip_bytes)) as z:
        infos = z.infolist()
        total_bytes = sum(zi.file_size for zi in infos)
        with tqdm(total=total_bytes, unit='B', unit_scale=True, desc='extract') as pbar:
            for zi in infos:
                # skip directories
                if zi.is_dir():
                    target_path = os.path.join(target_folder, zi.filename)
                    os.makedirs(target_path, exist_ok=True)
                    continue
                target_path = os.path.join(target_folder, zi.filename)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with z.open(zi) as src, open(target_path, "wb") as dst:
                    while True:
                        chunk = src.read(chunk_size)
                        if not chunk:
                            break
                        dst.write(chunk)
                        pbar.update(len(chunk))

def rename_obf_remove_suffix(folder, suffix_pattern=r'_2(?=\.obf$)'):
    changes = []
    pat = re.compile(suffix_pattern)
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith('.obf') and pat.search(f):
                old = os.path.join(root, f)
                new_name = pat.sub('', f)
                new = os.path.join(root, new_name)
                if os.path.exists(new):
                    os.remove(new)
                os.replace(old, new)
                changes.append((old, new))
    return changes

def fetch_and_process(name, listing_url="https://download.osmand.net/list.php", files_dir="files", session=None, timeout=30):
    sess = session or requests.Session()
    html_text = fetch_listing(listing_url, session=sess, timeout=timeout)
    matches = extract_zip_links_bs(html_text, name, listing_url)

    os.makedirs(files_dir, exist_ok=True)
    results = []
    for fname, url in matches:
        entry = {'zip_name': fname, 'url': url, 'downloaded': False, 'extracted_to': None, 'renames': [], 'errors': []}
        try:
            data = download_file(url, session=sess, timeout=timeout)
            entry['downloaded'] = True
        except Exception as e:
            entry['errors'].append(f"download error: {e}")
            results.append(entry)
            continue
            
        try:
            subfolder = files_dir
            extract_with_byte_progress(data, subfolder)
            entry['extracted_to'] = subfolder
        except zipfile.BadZipFile:
            entry['errors'].append("bad zip file or not a zip")
            results.append(entry)
            continue
        except Exception as e:
            entry['errors'].append(f"extract error: {e}")
            results.append(entry)
            continue

        try:
            changes = rename_obf_remove_suffix(subfolder)
            entry['renames'] = changes
        except Exception as e:
            entry['errors'].append(f"rename error: {e}")

        results.append(entry)
    return results

def main(argv=None):
    p = argparse.ArgumentParser(description="Download and extract OsmAnd zip files matching a state/country name.")
    p.add_argument("name", help="State or country name to match (case-insensitive, regex-escaped automatically).")
    p.add_argument("--listing-url", default="https://download.osmand.net/list.php", help="Listing URL (default download.osmand.net/list.php).")
    p.add_argument("--files-dir", default="files", help="Directory to extract zip contents into (created if missing).")
    args = p.parse_args(argv)

    try:
        results = fetch_and_process(args.name, listing_url=args.listing_url, files_dir=args.files_dir)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if not results:
        print("No matching zip files found.")
        return

    for r in results:
        status = "OK" if r['downloaded'] and not r['errors'] else "ERR"
        print(f"{status}: {r['zip_name']} -> {r['extracted_to'] or 'not extracted'}")
        for err in r['errors']:
            print(f"  - {err}")
        for old, new in r.get('renames', []):
            print(f"  renamed: {old} -> {new}")

if __name__ == "__main__":
    main()

## Below used to test modifications and updates with a smaller state map.
# state = "us_rhode"
# listing_url = "https://download.osmand.net/list.php"
# fetch_and_process(state, listing_url, files_dir="files")
