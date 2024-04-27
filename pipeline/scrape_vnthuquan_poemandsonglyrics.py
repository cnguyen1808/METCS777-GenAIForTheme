import sys
import requests
from bs4 import BeautifulSoup
import urllib.parse
import csv
from unidecode import unidecode

# Base URL and parameters for poems
base_poem_url = 'http://vietnamthuquan.eu/Tho'
poem_params = {'tranghientai': 1, 'tua': 'T'}

# Base URL and parameters for songs
base_song_url = 'http://vietnamthuquan.eu/nhac'
song_params = {'tranghientai': 1, 'tua': 'T'}

# Function to scrape a single page and return list of hrefs
def scrape_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        box = soup.find('article', class_='hentry nenthochinh')
        poems = box.find_all('li', class_='menutruyen')
        hrefs = [poem.find('a')['href'] for poem in poems]
        return hrefs
    else:
        print(f"Failed to scrape page {url}")
        return []

# Function to scrape poems from multiple pages
def scrape_poems(base_url, params, total_pages):
    all_hrefs = []
    for page_num in range(1, total_pages + 1):
        params['tranghientai'] = page_num
        url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        hrefs = scrape_page(url)
        all_hrefs.extend(hrefs)
    return all_hrefs

# Function to scrape songs from multiple pages
def scrape_songs(base_url, params, total_pages):
    all_hrefs = []
    for page_num in range(1, total_pages + 1):
        params['tranghientai'] = page_num
        url = f"{base_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
        hrefs = scrape_page(url)
        all_hrefs.extend(hrefs)
    return all_hrefs

# Function to encode text to VISCII
def to_viscii(text):
    return text.encode('viscii')

# Function to decode VISCII-encoded bytes to Unicode
def from_viscii(bytes):
    return bytes.decode('viscii')

# Function to scrape and save poem data
def scrape_and_save_poems():
    all_poems_in_page = scrape_poems(base_poem_url, poem_params, 1012)

    with open("vnthuquan_poetry_data.csv", "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        is_empty = csvfile.tell() == 0
        poem_id_counter = 1    
        for href in all_poems_in_page:
            full_url = f'{base_poem_url}/{href}'
            full_url_encoded = urllib.parse.quote(full_url, safe=':/?=&')

            response = requests.get(full_url_encoded)
            if response.status_code == 200:
                poem_page = BeautifulSoup(response.content, 'html.parser')
                title = poem_page.find("div", class_="chuto30a").get_text(strip=True)
                author = poem_page.find("div", class_="chutieude").get_text(strip=True)
                body = poem_page.find("div", class_="truyen_text").get_text()

                title = unidecode(title)
                author = unidecode(author)
                body_lines = [unidecode(line) for line in body.split("\n")]

                if is_empty:
                    writer.writerow(["ID", "Title", "Author", "Body"])
                    is_empty = False

                writer.writerow([poem_id_counter, title, author, body_lines[2]])
                poem_id_counter += 1
            else:
                print(f"Failed to scrape page {full_url_encoded}")

# Function to scrape and save song lyrics data
def scrape_and_save_songs():
    all_songs_in_page = scrape_songs(base_song_url, song_params, 283)

    with open("vnthuquan_songlyrics_data.csv", "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        is_empty = csvfile.tell() == 0
        song_id_counter = 1    
        for href in all_songs_in_page:
            full_url = f'{base_song_url}/{href}'
            full_url_encoded = urllib.parse.quote(full_url, safe=':/?=&')

            response = requests.get(full_url_encoded)
            if response.status_code == 200:
                poem_page = BeautifulSoup(response.content, 'html.parser')
                title = poem_page.find("div", class_="chuto30b").get_text(strip=True)
                author = poem_page.find("span", class_="tga").get_text(strip=True)
                body = poem_page.find("div", class_="truyen_text").get_text()

                title = unidecode(title)
                author = unidecode(author)
                body_lines = [unidecode(line) for line in body.split("\n") if line.strip() and line[:12] != 'Your browser']
                lyric = max(body_lines, key=len)  
                poet = ''
                for ele in body_lines:
                    if ele[:7] == 'Tho Loi':
                        poet = ele[8:]

                if is_empty:
                    writer.writerow(["ID", "Title", "Author", "Poem_Author", "Body"])
                    is_empty = False

                if (lyric.strip() == '') and (len(lyric) <= 100): 
                    pass # Text lyrics is not available - ignore
                else: 
                    writer.writerow([song_id_counter, title, author, poet, lyric])
                    song_id_counter += 1
            else:
                print(f"Failed to scrape page {full_url_encoded}")

# Run the scraping functions
scrape_and_save_poems()
scrape_and_save_songs()
