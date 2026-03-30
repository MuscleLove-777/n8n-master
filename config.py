"""n8n AI自動化マスター - ブログ固有設定"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

BLOG_NAME = "n8n AI自動化マスター"
BLOG_DESCRIPTION = "オープンソースAI自動化ツールn8nの使い方・ワークフロー構築・AIエージェント連携を毎日更新。GitHub15万スターの自動化プラットフォームを完全解説。"
BLOG_URL = "https://musclelove-777.github.io/n8n-master"
BLOG_TAGLINE = "n8nで業務を完全自動化するための日本語情報サイト"
BLOG_LANGUAGE = "ja"

GITHUB_REPO = "MuscleLove-777/n8n-master"
GITHUB_BRANCH = "gh-pages"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

OUTPUT_DIR = BASE_DIR / "output"
ARTICLES_DIR = OUTPUT_DIR / "articles"
SITE_DIR = OUTPUT_DIR / "site"
TOPICS_DIR = OUTPUT_DIR / "topics"

TARGET_CATEGORIES = [
    "n8n 使い方",
    "n8n 料金・プラン",
    "n8n ワークフロー",
    "n8n 最新ニュース",
    "n8n × AIエージェント",
    "n8n テクニック",
    "自動化ツール比較",
    "n8n 活用事例",
]

THEME = {
    "primary": "#ff6d5a",
    "accent": "#1a1a2e",
    "gradient_start": "#ff6d5a",
    "gradient_end": "#ea4c89",
    "dark_bg": "#0a0a1a",
    "dark_surface": "#1a1a2e",
    "light_bg": "#fff5f3",
    "light_surface": "#ffffff",
}

MAX_ARTICLE_LENGTH = 4000
ARTICLES_PER_DAY = 1
SCHEDULE_HOURS = [12]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

ENABLE_SEO_OPTIMIZATION = True
MIN_SEO_SCORE = 75
MIN_KEYWORD_DENSITY = 1.0
MAX_KEYWORD_DENSITY = 3.0
META_DESCRIPTION_LENGTH = 120
ENABLE_INTERNAL_LINKS = True

AFFILIATE_LINKS = {
    "n8n Cloud": [
        {"service": "n8n Cloud", "url": "https://n8n.io/cloud", "description": "n8n Cloudに登録する"},
    ],
    "n8n Self-host": [
        {"service": "n8n Docker", "url": "https://docs.n8n.io/hosting/", "description": "n8nをセルフホストする"},
    ],
    "AI連携": [
        {"service": "OpenAI API", "url": "https://platform.openai.com", "description": "OpenAI APIに登録"},
        {"service": "Google AI Studio", "url": "https://aistudio.google.com", "description": "Google AI Studioで始める"},
    ],
    "オンライン講座": [
        {"service": "Udemy", "url": "https://www.udemy.com", "description": "Udemyでn8n講座を探す"},
    ],
    "書籍": [
        {"service": "Amazon", "url": "https://www.amazon.co.jp", "description": "Amazonで自動化関連書籍を探す"},
        {"service": "楽天ブックス", "url": "https://www.rakuten.co.jp", "description": "楽天で自動化関連書籍を探す"},
    ],
}
AFFILIATE_TAG = "musclelove07-22"

ADSENSE_CLIENT_ID = os.environ.get("ADSENSE_CLIENT_ID", "")
ADSENSE_ENABLED = bool(ADSENSE_CLIENT_ID)
DASHBOARD_PORT = 8105

# Google Analytics (GA4)
GOOGLE_ANALYTICS_ID = "G-CSFVD34MKK"

# Google Search Console 認証ファイル
SITE_VERIFICATION_FILES = {
    "googlea31edabcec879415.html": "google-site-verification: googlea31edabcec879415.html",
}
