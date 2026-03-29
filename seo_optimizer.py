"""n8n AI自動化マスター - SEO最適化ラッパー

blog_engineのSEOOptimizerを使用し、JSON-LD構造化データ生成機能を追加。
BlogPosting / FAQPage / BreadcrumbList に対応。
"""
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blog_engine.seo_optimizer import SEOOptimizer as BaseSEOOptimizer  # noqa: E402


class N8nSEOOptimizer(BaseSEOOptimizer):
    """n8n特化のSEO最適化クラス（JSON-LD構造化データ対応）"""

    def __init__(self, config):
        super().__init__(config)
        self.blog_url = config.BLOG_URL
        self.blog_name = config.BLOG_NAME

    def generate_blog_posting_jsonld(self, article: dict) -> str:
        """BlogPosting JSON-LDを生成する"""
        slug = article.get("slug", "untitled")
        data = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": article.get("title", ""),
            "description": article.get("meta_description", ""),
            "url": f"{self.blog_url}/articles/{slug}.html",
            "datePublished": article.get("generated_at", datetime.now().isoformat()),
            "dateModified": article.get("generated_at", datetime.now().isoformat()),
            "author": {
                "@type": "Organization",
                "name": self.blog_name,
                "url": self.blog_url,
            },
            "publisher": {
                "@type": "Organization",
                "name": self.blog_name,
                "url": self.blog_url,
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": f"{self.blog_url}/articles/{slug}.html",
            },
            "keywords": ", ".join(article.get("tags", [])),
            "articleSection": article.get("category", ""),
            "inLanguage": "ja",
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def generate_faq_jsonld(self, article: dict) -> str:
        """FAQPage JSON-LDを生成する"""
        faq_items = article.get("faq", [])
        if not faq_items:
            return ""

        data = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item.get("question", ""),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": item.get("answer", ""),
                    },
                }
                for item in faq_items
            ],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def generate_breadcrumb_jsonld(self, article: dict) -> str:
        """BreadcrumbList JSON-LDを生成する"""
        category = article.get("category", "未分類")
        title = article.get("title", "")

        data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "ホーム",
                    "item": self.blog_url,
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": category,
                    "item": f"{self.blog_url}/category/{category}",
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": title,
                },
            ],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    def generate_all_jsonld(self, article: dict) -> list:
        """全ての構造化データを生成して返す"""
        scripts = []

        blog_posting = self.generate_blog_posting_jsonld(article)
        scripts.append(f'<script type="application/ld+json">\n{blog_posting}\n</script>')

        faq = self.generate_faq_jsonld(article)
        if faq:
            scripts.append(f'<script type="application/ld+json">\n{faq}\n</script>')

        breadcrumb = self.generate_breadcrumb_jsonld(article)
        scripts.append(f'<script type="application/ld+json">\n{breadcrumb}\n</script>')

        return scripts
