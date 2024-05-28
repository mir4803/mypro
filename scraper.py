import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from models import SessionLocal, Article

BASE_URL = "https://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=86"
DOWNLOAD_DIR = "downloads"

def fetch_page(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def download_file(url, filename):
    response = requests.get(url, stream=True)
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    with open(os.path.join(DOWNLOAD_DIR, filename), 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def scrape_board():
    soup = fetch_page(BASE_URL)
    rows = soup.select('#contents_inner > div > table > tbody > tr')
    
    # 최근 5건만 처리
    rows = rows[:5]

    for row in rows:
        title = row.select_one('td.subject a').get_text(strip=True)
        department = row.select_one('td:nth-child(3)').get_text(strip=True)
        date_str = row.select_one('td:nth-child(5)').get_text(strip=True)
        
        try:
            date = datetime.strptime(date_str, '%Y.%m.%d')
        except ValueError:
            print(f"Date format error: {date_str}")
            continue

        attachment_tag = row.select_one('td.attached-files a')
        if attachment_tag:
            attachment_link = attachment_tag['href']
            attachment_url = f"https://www.mss.go.kr{attachment_link}"
            attachment_name = attachment_url.split('streFileNm=')[-1]  # 파일 이름을 URL에서 추출

            # Download the attachment
            download_file(attachment_url, attachment_name)
        else:
            attachment_name = None

        # Save to database
        db = SessionLocal()
        save_to_db(db, title, department, date, attachment_name)
        db.close()

def save_to_db(db, title, department, date, attachment_name):
    article = Article(title=title, department=department, date=date, attachment=attachment_name)
    db.add(article)
    db.commit()

if __name__ == "__main__":
    scrape_board()
