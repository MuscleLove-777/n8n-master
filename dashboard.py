"""n8n AI自動化マスター - ダッシュボードラッパー

blog_engineのdashboard.create_appを使用する。
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from blog_engine.dashboard import create_app  # noqa: E402


def start_dashboard(config, prompts=None):
    """ダッシュボードを起動する"""
    import uvicorn
    host = getattr(config, "DASHBOARD_HOST", "127.0.0.1")
    port = getattr(config, "DASHBOARD_PORT", 8105)

    app = create_app(config, prompts)
    print(f"ダッシュボード起動: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
