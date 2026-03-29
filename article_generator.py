"""n8n AI自動化マスター - 記事生成ラッパー

blog_engineのArticleGeneratorを使用し、n8n特化の記事を生成する。
"""
import sys
import os

# blog_engineへのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blog_engine.article_generator import ArticleGenerator  # noqa: E402


def create_generator(config):
    """ArticleGeneratorのインスタンスを作成する"""
    return ArticleGenerator(config)
