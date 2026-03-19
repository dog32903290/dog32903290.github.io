from flask import Flask, render_template, jsonify
import requests
import csv
import io
import re

app = Flask(__name__)

# Google Sheet CSV URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1f1xkopplbQyjRVKtPeS3P2XKxRVAIEHX_7vzEEICJjw/export?format=csv"

def get_youtube_id(url):
    """提取 YouTube 影片 ID"""
    if "youtu.be/" in url:
        return url.split("/")[-1]
    if "/shorts/" in url:
        return url.split("/shorts/")[-1].split("?")[0]
    id_match = re.search(r'v=([^&]+)', url)
    return id_match.group(1) if id_match else None

def fetch_data():
    """從 Google Sheet 取得作品資料"""
    try:
        response = requests.get(SHEET_URL)
        response.raise_for_status()
        content = response.content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        projects = []
        for row in csv_reader:
            # 去除欄位名稱的空白並取得對應資料
            row = {k.strip(): v for k, v in row.items()}
            
            video_url = row.get('VideoID (YouTube ID)', '').strip()
            video_id = get_youtube_id(video_url)
            
            projects.append({
                "title": row.get('Title (標題)', '').strip(),
                "video_id": video_id,
                "description": row.get('Description (描述)', '').strip(),
                "category": row.get('Category (分類)', '音樂').strip(),
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
