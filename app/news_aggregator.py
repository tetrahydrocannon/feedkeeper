import feedparser
from app import db
from app.models import Article
from datetime import datetime
from sqlalchemy import func
import bleach

# List of RSS feed URLs
feeds = [
    'http://www.bbc.co.uk/news/10628494',
    'http://edition.cnn.com/services/rss/',
    'https://www.nytimes.com/services/xml/rss/index.html',
    'https://www.reuters.com/tools/rss',
    'https://www.theguardian.com/uk/rss',
    'https://www.aljazeera.com/xml/rss/all.xml',
    'https://www.npr.org/rss/',
    'https://abcnews.go.com/abcnews/topstories',
    'https://www.cbsnews.com/latest/rss/main',
    'https://techcrunch.com/feed/',
    'https://www.wired.com/feed/rss',
    'https://www.theverge.com/rss/index.xml',
    'https://www.engadget.com/rss.xml',
    'https://www.bloomberg.com/feed',
    'https://www.ft.com/rss',
    'https://www.wsj.com/news/rss',
    'https://www.forbes.com/real-time/feed2/',
    'https://www.scientificamerican.com/feed/',
    'https://www.nature.com/nature/articles?type=research&error=cookies_not_supported&code=f4ec28e7-8f42-4b9c-a403-80d1779e4ea8',
    'https://www.healthline.com/rss',
    'https://www.newscientist.com/feed/home/',
    'https://www.washingtonpost.com/rss/',
    'https://timesofindia.indiatimes.com/rss.cms',
    'https://www.smh.com.au/rssfeeds',
    'https://www.lemonde.fr/rss/',
    'https://www.spiegel.de/schlagzeilen/tops/index.rss',
    'https://www.espn.com/espn/rss/news',
    'http://feeds.bbci.co.uk/sport/rss.xml',
]

# List of keywords to monitor
keywords = [
    'technology', 'economy', 'health', 'science', 'election', 'climate change',
    'COVID-19', 'vaccine', 'AI', 'cybersecurity', 'market', 'finance', 'innovation'
]

def fetch_and_store_articles():
    for feed_url in feeds:
        parsed_feed = feedparser.parse(feed_url)
        for entry in parsed_feed.entries:
            title = entry.get('title', '')
            description = entry.get('description', '')
            content = entry.get('content', [{'value': ''}])[0]['value']
            author = entry.get('author', '')
            published_at = entry.get('published', '')
            link = entry.get('link', '')

            # Convert published_at to datetime
            if published_at:
                published_at = datetime(*entry.published_parsed[:6])

            # Sanitize HTML content for both content and description
            sanitized_content = bleach.clean(
                content,
                tags=['p', 'b', 'i', 'u', 'a', 'br', 'img'],
                attributes={'a': ['href'], 'img': ['src', 'alt', 'style']},
                strip=True
            )

            sanitized_description = bleach.clean(
                description,
                tags=['p', 'b', 'i', 'u', 'a', 'br', 'img'],
                attributes={'a': ['href'], 'img': ['src', 'alt', 'style']},
                strip=True
            )

            # Check if any keyword is present in the title or description
            found_keywords = [keyword for keyword in keywords if keyword in title or keyword in description]
            
            # Avoid inserting duplicates based on link
            if not Article.query.filter(func.lower(Article.link) == func.lower(link)).first():
                article = Article(
                    feed_url=feed_url,
                    title=title,
                    description=sanitized_description,  # Use sanitized description here
                    content=sanitized_content,
                    author=author,
                    published_at=published_at,
                    link=link,
                    keywords=found_keywords,
                    raw_data=entry
                )
                db.session.add(article)
                db.session.commit()

