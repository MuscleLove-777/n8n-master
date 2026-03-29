"""n8n AI自動化マスター - トピック収集モジュール

topics.jsonからトピックを読み込み、未使用のものを優先度順に返す。
また、Gemini APIでトレンドトピックを自動収集する機能を持つ。
"""
import json
import logging
import random
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class TopicCollector:
    """トピック収集・管理クラス"""

    def __init__(self, config):
        self.config = config
        self.topics_file = Path(config.BASE_DIR) / "topics.json"
        self.topics = self._load_topics()
        logger.info("TopicCollector を初期化しました（%d カテゴリ）", len(self.topics))

    def _load_topics(self) -> dict:
        """topics.jsonからトピックを読み込む"""
        if not self.topics_file.exists():
            logger.warning("topics.json が見つかりません: %s", self.topics_file)
            return {}

        with open(self.topics_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_next_topic(self) -> tuple:
        """次に書くべきトピックを優先度順に返す

        Returns:
            tuple: (category, keyword) のタプル
        """
        # 優先度順にソート: high > medium > low
        priority_order = {"high": 0, "medium": 1, "low": 2}

        candidates = []
        for category, topics in self.topics.items():
            for topic in topics:
                if topic.get("status") == "pending":
                    priority = priority_order.get(topic.get("priority", "medium"), 1)
                    candidates.append((priority, category, topic))

        if not candidates:
            logger.warning("未処理のトピックがありません")
            return None, None

        # 優先度でソート後、同一優先度内はランダム
        candidates.sort(key=lambda x: x[0])
        top_priority = candidates[0][0]
        top_candidates = [c for c in candidates if c[0] == top_priority]
        selected = random.choice(top_candidates)

        return selected[1], selected[2]["keyword"]

    def mark_as_done(self, category: str, keyword: str):
        """トピックを完了状態にする"""
        if category in self.topics:
            for topic in self.topics[category]:
                if topic["keyword"] == keyword:
                    topic["status"] = "done"
                    topic["done_at"] = datetime.now().isoformat()
                    self._save_topics()
                    logger.info("トピック完了: [%s] %s", category, keyword)
                    return

    def _save_topics(self):
        """topics.jsonを保存する"""
        with open(self.topics_file, "w", encoding="utf-8") as f:
            json.dump(self.topics, f, ensure_ascii=False, indent=2)

    def get_stats(self) -> dict:
        """トピックの統計情報を返す"""
        total = 0
        done = 0
        pending = 0
        by_category = {}

        for category, topics in self.topics.items():
            cat_total = len(topics)
            cat_done = sum(1 for t in topics if t.get("status") == "done")
            cat_pending = cat_total - cat_done
            total += cat_total
            done += cat_done
            pending += cat_pending
            by_category[category] = {
                "total": cat_total, "done": cat_done, "pending": cat_pending
            }

        return {
            "total": total, "done": done, "pending": pending,
            "by_category": by_category,
        }
