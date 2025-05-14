import os
import markdown
from datetime import datetime

def load_articles(directory):
    articles = []
    for file in os.listdir(directory):
        if file.endswith(".md"):
            path = os.path.join(directory, file)
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                title = lines[0].strip('# \n')
                date_line = lines[1].strip()
                date = date_line.replace('*', '').strip()
                slug = os.path.splitext(file)[0]
                articles.append({
                    'title': title,
                    'date': date,
                    'slug': slug,
                    'path': path
                })
    # Sort by date (latest first)
    articles.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"), reverse=True)
    return articles

def get_article_content(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
        return markdown.markdown(text)

def paginate_articles(articles, page=1, per_page=5):
    start = (page - 1) * per_page
    return articles[start:start + per_page]
