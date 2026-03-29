"""n8n AI自動化マスター - スケジューラーラッパー

blog_engineのBlogSchedulerを使用する。
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blog_engine.scheduler import BlogScheduler  # noqa: E402


def create_scheduler(config, prompts=None):
    """BlogSchedulerのインスタンスを作成する"""
    return BlogScheduler(config, prompts)
