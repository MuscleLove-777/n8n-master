#!/usr/bin/env python3
"""n8n AI自動化マスター - CLIエントリポイント

blog_engineのmainモジュールを使用する。
"""
import sys
import os
from llm import get_llm_client

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blog_engine.main import main  # noqa: E402

if __name__ == "__main__":
    # デフォルトのconfigパスを設定
    if "--config" not in sys.argv:
        config_path = os.path.join(os.path.dirname(__file__), "config.py")
        sys.argv.insert(1, "--config")
        sys.argv.insert(2, config_path)
    main()
