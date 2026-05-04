#!/usr/bin/env python3
"""GitHub Actions用一括実行スクリプト

キーワード選定 → 記事生成 → SEO最適化 → サイトビルド を一括実行する。
JSON-LD構造化データ（BlogPosting / FAQPage / BreadcrumbList）対応。
"""
import sys
import os
import json
import re
import logging
import time
from datetime import datetime
from pathlib import Path

# blog_engineへのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run(config, prompts=None):
    """メイン処理: キーワード選定 → 記事生成 → SEO最適化 → サイトビルド"""
    logger.info("=== %s 自動生成開始 ===", config.BLOG_NAME)
    start_time = datetime.now()

    # ステップ1: キーワード選定（topic_collector経由で topics.json から）
    # 旧実装は Gemini に毎日「カテゴリ＋キーワード選んで」と頼んでたが、
    # Gemini がプロンプト例の例キーワードをオウム返しして同一記事量産が発生。
    # topic_collector.get_next_topic() で topics.json の優先度順に確実に順送りする。
    logger.info("ステップ1: キーワード選定（topics.json）")
    tc = None
    try:
        from topic_collector import TopicCollector
        tc = TopicCollector(config)
        category, keyword = tc.get_next_topic()
        if not category or not keyword:
            logger.error("topics.json に未処理(pending)のトピックがありません。topics.json を補充してください。")
            sys.exit(1)
        logger.info("選定結果 - カテゴリ: %s, キーワード: %s", category, keyword)
    except SystemExit:
        raise
    except Exception as e:
        logger.error("キーワード選定に失敗: %s", e)
        sys.exit(1)

    # ステップ2: 記事生成
    logger.info("ステップ2: 記事生成")
    try:
        from blog_engine.article_generator import ArticleGenerator
        from seo_optimizer import N8nSEOOptimizer

        generator = ArticleGenerator(config)
        article = generator.generate_article(
            keyword=keyword, category=category, prompts=prompts
        )
        logger.info("記事生成完了: %s", article.get("title", "不明"))

        optimizer = N8nSEOOptimizer(config)
        seo_result = optimizer.check_seo_score(article)
        article["seo_score"] = seo_result.get("total_score", 0)
        logger.info("SEOスコア: %d/100", article["seo_score"])

        # JSON-LD構造化データを記事に追加
        jsonld_scripts = optimizer.generate_all_jsonld(article)
        article["jsonld"] = jsonld_scripts
        logger.info("JSON-LD構造化データ: %d件生成", len(jsonld_scripts))

    except Exception as e:
        logger.error("記事生成に失敗: %s", e)
        sys.exit(1)

    # ステップ2.5: アフィリエイトリンク挿入
    logger.info("ステップ2.5: アフィリエイトリンク挿入")
    try:
        from blog_engine.affiliate import AffiliateManager
        affiliate_mgr = AffiliateManager(config)
        article = affiliate_mgr.insert_affiliate_links(article)
        logger.info("アフィリエイトリンク: %d件挿入", article.get("affiliate_count", 0))
    except Exception as aff_err:
        logger.warning("アフィリエイトリンク挿入をスキップ: %s", aff_err)

    # ステップ2.7: 記事JSONを再保存（SEOスコア・JSON-LD追加後）
    try:
        file_path = article.get("file_path")
        if file_path:
            save_data = {k: v for k, v in article.items() if k != "file_path"}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            logger.info("記事を再保存しました: %s", file_path)
    except Exception as save_err:
        logger.warning("記事の再保存をスキップ: %s", save_err)

    # ステップ3: サイトビルド
    logger.info("ステップ3: サイトビルド")
    try:
        from site_generator import N8nSiteGenerator
        site_gen = N8nSiteGenerator(config)
        site_gen.build_site()
        logger.info("サイトビルド完了")
    except Exception as e:
        logger.error("サイトビルドに失敗: %s", e)
        sys.exit(1)

    # ステップ4: トピックを done にして topics.json を更新（次回の重複防止）
    if tc is not None:
        try:
            tc.mark_as_done(category, keyword)
            logger.info("トピックを done に更新: [%s] %s", category, keyword)
        except Exception as e:
            logger.warning("topics.json の更新をスキップ: %s", e)

    # 完了
    duration = (datetime.now() - start_time).total_seconds()
    logger.info("=== 自動生成完了（%.1f秒） ===", duration)
    logger.info("  カテゴリ: %s", category)
    logger.info("  キーワード: %s", keyword)
    logger.info("  タイトル: %s", article.get("title", "不明"))
    logger.info("  SEOスコア: %d/100", article.get("seo_score", 0))


if __name__ == "__main__":
    # 直接実行時
    sys.path.insert(0, os.path.dirname(__file__))
    import config
    import prompts
    run(config, prompts)
