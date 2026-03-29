#!/usr/bin/env python3
"""GitHub Actions用一括実行スクリプト

キーワード選定 → 記事生成 → SEO最適化 → サイトビルド を一括実行する。
JSON-LD構造化データ（BlogPosting / FAQPage / BreadcrumbList）対応。
"""
import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# blog_engineへのパスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run(config, prompts=None):
    """メイン処理: キーワード選定 → 記事生成 → SEO最適化 → サイトビルド"""
    logger.info("=== %s 自動生成開始 ===", config.BLOG_NAME)
    start_time = datetime.now()

    # ステップ1: キーワード選定
    logger.info("ステップ1: キーワード選定")
    try:
        from google import genai

        if not config.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY が設定されていません")
            sys.exit(1)

        client = genai.Client(api_key=config.GEMINI_API_KEY)

        if prompts and hasattr(prompts, "build_keyword_prompt"):
            prompt = prompts.build_keyword_prompt(config)
        else:
            categories_text = "\n".join(f"- {cat}" for cat in config.TARGET_CATEGORIES)
            prompt = (
                f"{config.BLOG_NAME}用のキーワードを選定してください。\n\n"
                "以下のカテゴリから1つ選び、そのカテゴリで今注目されている"
                "トピック・キーワードを1つ提案してください。\n\n"
                f"カテゴリ一覧:\n{categories_text}\n\n"
                "以下の形式でJSON形式のみで回答してください（説明不要）:\n"
                '{"category": "カテゴリ名", "keyword": "キーワード"}'
            )

        response = client.models.generate_content(
            model=config.GEMINI_MODEL, contents=prompt
        )
        response_text = response.text.strip()

        if "```" in response_text:
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        data = json.loads(response_text)
        category = data["category"]
        keyword = data["keyword"]
        logger.info("選定結果 - カテゴリ: %s, キーワード: %s", category, keyword)

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
