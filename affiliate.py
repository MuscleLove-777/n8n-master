"""n8n AI自動化マスター - アフィリエイトラッパー

blog_engineのAffiliateManagerを使用する。
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blog_engine.affiliate import AffiliateManager  # noqa: E402


def create_affiliate_manager(config):
    """AffiliateManagerのインスタンスを作成する"""
    return AffiliateManager(config)
