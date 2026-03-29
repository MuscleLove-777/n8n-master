"""n8n AI自動化マスター - プロンプト定義

オープンソース自動化ツールn8n特化ブログ用のプロンプトを一元管理する。
JSON-LD構造化データ（BlogPosting / FAQPage / BreadcrumbList）対応。
"""

# ペルソナ設定
PERSONA = (
    "あなたはn8n（エヌエイトエヌ）のワークフロー自動化エキスパートです。"
    "セルフホスト環境の構築からクラウド版の活用、AIエージェント連携まで精通し、"
    "初心者からDevOpsエンジニアまで幅広い読者に実践的な自動化ノウハウを届けるプロのテックライターです。"
    "n8nの最新アップデートやコミュニティの動向を常にキャッチアップし、"
    "Zapier、Make（Integromat）、Power Automateなど他の自動化ツールとの比較も客観的に行えます。"
)

# 記事フォーマット指示
ARTICLE_FORMAT = """
【記事構成（必ずこの順序で書くこと）】

## この記事でわかること
- ポイント1（具体的なベネフィット）
- ポイント2
- ポイント3

## 結論（先に結論を述べる）
（読者が最も知りたい答えを最初に提示）

## 本題（H2で3〜5セクション）
（具体的なワークフロー構築手順・ノード設定方法を詳しく解説）

## ワークフロー実装テクニック
（トリガー設定 / ノード接続 / エラーハンドリング / 条件分岐の具体例）

## 他の自動化ツールとの比較
（Zapier / Make / Power Automate との違いを表形式で整理）

## よくある質問（FAQ）
### Q1: （よくある質問1）
A1: （回答1）

### Q2: （よくある質問2）
A2: （回答2）

### Q3: （よくある質問3）
A3: （回答3）

## まとめ
（要点整理と次のアクション提案）
"""

# カテゴリ別SEOキーワードヒント
CATEGORY_PROMPTS = {
    "n8n 使い方": "n8n 使い方、n8n 始め方、n8n 初心者、n8n インストール、n8n Docker、n8n チュートリアル",
    "n8n 料金・プラン": "n8n 料金、n8n 無料 有料 違い、n8n Cloud 価格、n8n セルフホスト 無料、n8n Enterprise",
    "n8n ワークフロー": "n8n ワークフロー、n8n 自動化、n8n ノード、n8n テンプレート、n8n レシピ",
    "n8n 最新ニュース": "n8n アップデート、n8n 新機能、n8n リリース、n8n GitHub、n8n コミュニティ",
    "n8n × AIエージェント": "n8n AI、n8n LangChain、n8n OpenAI、n8n エージェント、n8n RAG、n8n ベクトルDB",
    "n8n テクニック": "n8n エラーハンドリング、n8n 条件分岐、n8n ループ、n8n Webhook、n8n API連携",
    "自動化ツール比較": "n8n Zapier 比較、n8n Make 比較、n8n Power Automate 比較、自動化ツール おすすめ 2026",
    "n8n 活用事例": "n8n ビジネス活用、n8n 業務効率化、n8n マーケティング自動化、n8n SNS自動投稿",
}

# ニュースソース
NEWS_SOURCES = [
    "n8n Blog (https://blog.n8n.io/)",
    "n8n Community (https://community.n8n.io/)",
    "n8n GitHub (https://github.com/n8n-io/n8n)",
    "n8n Docs (https://docs.n8n.io/)",
]

# FAQ構造化データの有効化
FAQ_SCHEMA_ENABLED = True

# キーワード選定用の追加プロンプト
KEYWORD_PROMPT_EXTRA = (
    "オープンソース自動化ツールn8nに関するキーワードを選んでください。\n"
    "日本のユーザーが検索しそうな実用的なキーワードを意識してください。\n"
    "「n8n 使い方」「n8n 料金」「n8n Zapier 比較」「n8n AI連携」のような、\n"
    "検索ボリュームが見込めるキーワードを優先してください。"
)


def build_keyword_prompt(config):
    """キーワード選定プロンプトを構築する"""
    categories_text = "\n".join(f"- {cat}" for cat in config.TARGET_CATEGORIES)
    category_hints = "\n".join(
        f"- {cat}: {hints}" for cat, hints in CATEGORY_PROMPTS.items()
    )
    return (
        f"{PERSONA}\n\n"
        "n8n AI自動化マスターブログ用のキーワードを選定してください。\n\n"
        f"{KEYWORD_PROMPT_EXTRA}\n\n"
        f"カテゴリ一覧:\n{categories_text}\n\n"
        f"カテゴリ別キーワードヒント:\n{category_hints}\n\n"
        "以下の形式でJSON形式のみで回答してください（説明不要）:\n"
        '{"category": "カテゴリ名", "keyword": "キーワード"}'
    )


def build_article_prompt(keyword, category, config):
    """n8n特化記事生成プロンプトを構築する"""
    category_hints = CATEGORY_PROMPTS.get(category, "")
    news_sources_text = "\n".join(f"- {src}" for src in NEWS_SOURCES)

    return f"""{PERSONA}

以下のキーワードに関する記事を、n8n自動化ツールの専門サイト向けに執筆してください。

【基本条件】
- ブログ名: {config.BLOG_NAME}
- キーワード: {keyword}
- カテゴリ: {category}
- カテゴリ関連キーワード: {category_hints}
- 言語: 日本語
- 文字数: {config.MAX_ARTICLE_LENGTH}文字程度

{ARTICLE_FORMAT}

【SEO要件】
1. タイトルにキーワード「{keyword}」を必ず含めること
2. タイトルは32文字以内で魅力的に（数字や年号を含めると効果的）
3. H2、H3の見出し構造を適切に使用すること
4. キーワード密度は{config.MIN_KEYWORD_DENSITY}%〜{config.MAX_KEYWORD_DENSITY}%を目安に
5. メタディスクリプションは{config.META_DESCRIPTION_LENGTH}文字以内
6. FAQ（よくある質問）を3つ以上含めること（FAQPage構造化データ対応）

【内部リンク】
- 内部リンクのプレースホルダーを2〜3箇所に配置（{{{{internal_link:関連トピック}}}}の形式）

【参考情報源】
{news_sources_text}

【条件】
- {config.MAX_ARTICLE_LENGTH}文字程度
- 2026年最新の情報を反映すること
- 具体的なワークフロー構築手順やノード設定方法を含める
- AI連携（OpenAI, LangChain, ベクトルDB等）の活用テクニックを含める
- 他の自動化ツールとの客観的な比較を含める
- 初心者にもわかりやすく、専門用語には補足説明を付ける

【出力形式】
以下のJSON形式で出力してください。JSONブロック以外のテキストは出力しないでください。

```json
{{
  "title": "SEO最適化されたタイトル",
  "content": "# タイトル\\n\\n本文（Markdown形式）...",
  "meta_description": "120文字以内のメタディスクリプション",
  "tags": ["タグ1", "タグ2", "タグ3", "タグ4", "タグ5"],
  "slug": "url-friendly-slug",
  "faq": [
    {{"question": "質問1", "answer": "回答1"}},
    {{"question": "質問2", "answer": "回答2"}},
    {{"question": "質問3", "answer": "回答3"}}
  ]
}}
```

【注意事項】
- content内のMarkdownは適切にエスケープしてJSON文字列として有効にすること
- tagsは5個ちょうど生成すること
- slugは半角英数字とハイフンのみ使用すること
- faqは3個以上生成すること（FAQPage構造化データに使用）
- 読者にとって実用的で具体的な内容を心がけること"""
