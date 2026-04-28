"""n8n AI自動化マスター - キーワードリサーチラッパー

blog_engineのKeywordResearcherを使用する。
"""
import sys
import os
from llm import get_llm_client

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blog_engine.keyword_researcher import KeywordResearcher  # noqa: E402


def create_researcher(config, prompts=None):
    """KeywordResearcherのインスタンスを作成する"""
    return KeywordResearcher(config, prompts)
