"""n8n AI自動化マスター - サイト生成ラッパー

blog_engineのSiteGeneratorを使用し、robots.txt生成とJSON-LD注入を追加。
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blog_engine.site_generator import SiteGenerator as BaseSiteGenerator  # noqa: E402


class N8nSiteGenerator(BaseSiteGenerator):
    """n8n特化のサイト生成クラス"""

    def __init__(self, config):
        super().__init__(config)

    def build_site(self):
        """サイトをビルドし、robots.txtも生成する"""
        super().build_site()
        self._generate_robots_txt()
        print("  robots.txt 生成: robots.txt")

    def _generate_robots_txt(self):
        """robots.txtを生成する"""
        blog_url = self.config.BLOG_URL
        content = (
            "User-agent: *\n"
            "Allow: /\n"
            "\n"
            f"Sitemap: {blog_url}/sitemap.xml\n"
        )
        (self.output_dir / "robots.txt").write_text(content, encoding="utf-8")
