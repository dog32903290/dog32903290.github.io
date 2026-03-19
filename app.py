from flask import Flask, render_template, jsonify
import requests
import csv
import io
import re

app = Flask(__name__)

# Google Sheet CSV URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1f1xkopplbQyjRVKtPeS3P2XKxRVAIEHX_7vzEEICJjw/export?format=csv"

def get_youtube_id(url):
    """提取 YouTube 影片 ID，支援多種 URL 格式"""
    if not url: return None
    url = url.strip()
    # 如果已經是 11 位的 ID
    if len(url) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', url):
        return url
    
    # 支援常見格式：watch?v=, youtu.be/, shorts/, embed/
    patterns = [
        r'v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'shorts/([a-zA-Z0-9_-]{11})',
        r'embed/([a-zA-Z0-9_-]{11})'
    ]
    for p in patterns:
        match = re.search(p, url)
        if match:
            return match.group(1)
    return None

def fetch_data():
    """從 Google Sheet 取得作品資料"""
    try:
        response = requests.get(SHEET_URL)
        response.raise_for_status()
        content = response.content.decode('utf-8-sig')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        projects = []
        for row in csv_reader:
            # 容錯處理：去除欄位名稱空白
            row = {str(k).strip(): v for k, v in row.items() if k is not None}
            
            video_url = row.get('VideoID (YouTube ID)', '').strip()
            video_id = get_youtube_id(video_url)
            
            # 只有標題與影片 ID 都存在時才加入，避免空資料
            title = row.get('Title (標題)', '').strip()
            if title and video_id:
                projects.append({
                    "title": title,
                    "video_id": video_id,
                    "description": row.get('Description (描述)', '').strip(),
                    "category": row.get('Category (分類)', '音樂').strip().lower(),
                    "year": "2024" 
                })
        return projects
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/category/<cat>')
def category(cat):
    all_projects = fetch_data()
    # 將網址的 '-' 轉回空格以便匹配 CSV
    target_cat = cat.replace('-', ' ')
    projects = [p for p in all_projects if str(p.get('category') or '').lower().strip() == target_cat.lower()]
    
    # 顯示用的標題
    title = cat.title().replace('-', ' ')
    return render_template('category.html', projects=projects, category_title=title)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
