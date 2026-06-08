#!/usr/bin/env python3
"""
うんちステータスコード学習用サーバー
HTTP GET リクエストでステータスコードを返す

使用方法: python3 server.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

BASE_DIR = Path(__file__).parent

# ステータスコードのデータベース（HTTPレスポンスコードの決定用）
STATUS_DATABASE = {
    '100': {'code': 100, 'description': 'Continue - リクエストの送信を続けてかまいません'},
    '101': {'code': 101, 'description': 'Switching Protocols - プロトコルを切り替えます'},
    '102': {'code': 102, 'description': 'Processing - サーバーは処理を続けています'},
    '103': {'code': 103, 'description': 'Early Hints - 最終レスポンス前のヒントを返します'},
    '200': {'code': 200, 'description': 'OK - リクエストは成功しました'},
    '201': {'code': 201, 'description': 'Created - リソースが作成されました'},
    '204': {'code': 204, 'description': 'No Content - 成功しましたが内容はありません'},
    '206': {'code': 206, 'description': 'Partial Content - 部分的な内容を返します'},
    '300': {'code': 300, 'description': 'Multiple Choices - 複数の選択肢があります'},
    '301': {'code': 301, 'description': 'Moved Permanently - 永遠に別の場所に移動しました'},
    '302': {'code': 302, 'description': 'Found - 一時的に別の場所にあります'},
    '303': {'code': 303, 'description': 'See Other - 別のURLを見てください'},
    '304': {'code': 304, 'description': 'Not Modified - 変更されていません'},
    '307': {'code': 307, 'description': 'Temporary Redirect - 一時的にリダイレクトします'},
    '308': {'code': 308, 'description': 'Permanent Redirect - 永久的にリダイレクトします'},
    '400': {'code': 400, 'description': 'Bad Request - リクエストが不正です'},
    '401': {'code': 401, 'description': 'Unauthorized - 認証が必要です'},
    '403': {'code': 403, 'description': 'Forbidden - アクセスが禁止されています'},
    '404': {'code': 404, 'description': 'Not Found - ページが見つかりません'},
    '405': {'code': 405, 'description': 'Method Not Allowed - メソッドが許可されていません'},
    '408': {'code': 408, 'description': 'Request Timeout - リクエストがタイムアウトしました'},
    '409': {'code': 409, 'description': 'Conflict - リクエストが競合しています'},
    '410': {'code': 410, 'description': 'Gone - リソースは削除されました'},
    '418': {'code': 418, 'description': "I'm a Teapot - 紅茶を淹れるティーポットです（ジョーク）"},
    '429': {'code': 429, 'description': 'Too Many Requests - リクエストが多すぎます'},
    '500': {'code': 500, 'description': 'Internal Server Error - サーバーエラーが発生しました'},
    '501': {'code': 501, 'description': 'Not Implemented - 実装されていません'},
    '502': {'code': 502, 'description': 'Bad Gateway - 不正なゲートウェイです'},
    '503': {'code': 503, 'description': 'Service Unavailable - サービスが利用できません'},
    '504': {'code': 504, 'description': 'Gateway Timeout - ゲートウェイがタイムアウトしました'},
}


# よく使う理由フレーズ（未登録コードのフォールバック用）
REASON_PHRASES = {
    100: 'Continue', 101: 'Switching Protocols', 102: 'Processing', 103: 'Early Hints',
    200: 'OK', 201: 'Created', 204: 'No Content', 206: 'Partial Content',
    300: 'Multiple Choices', 301: 'Moved Permanently', 302: 'Found', 303: 'See Other',
    304: 'Not Modified', 307: 'Temporary Redirect', 308: 'Permanent Redirect',
    400: 'Bad Request', 401: 'Unauthorized', 402: 'Payment Required', 403: 'Forbidden',
    404: 'Not Found', 405: 'Method Not Allowed', 408: 'Request Timeout',
    409: 'Conflict', 410: 'Gone', 418: "I'm a Teapot", 429: 'Too Many Requests',
    500: 'Internal Server Error', 501: 'Not Implemented', 502: 'Bad Gateway',
    503: 'Service Unavailable', 504: 'Gateway Timeout',
}


def http_status_for_code(status_key: str) -> int:
    """URLパスから返すHTTPステータスコードを決定"""
    if status_key in STATUS_DATABASE:
        return STATUS_DATABASE[status_key]['code']

    if re.fullmatch(r'\d{3}', status_key):
        code = int(status_key)
        if 100 <= code <= 599:
            return code

    return 404


def description_for_code(status_key: str) -> str:
    """表示用の説明文を返す"""
    if status_key in STATUS_DATABASE:
        return STATUS_DATABASE[status_key]['description']

    http_code = http_status_for_code(status_key)
    phrase = REASON_PHRASES.get(http_code, 'Unknown')
    return f'{phrase} - HTTP {http_code}'


def status_payload(status_key: str) -> dict:
    """APIレスポンス用の共通ペイロード"""
    http_code = http_status_for_code(status_key)
    return {
        'code': status_key,
        'status': http_code,
        'phrase': REASON_PHRASES.get(http_code, 'Unknown'),
        'description': description_for_code(status_key),
    }


class PoopStatusHandler(BaseHTTPRequestHandler):
    """HTTPリクエストハンドラー"""

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        print(f"\n📨 リクエスト: {path}")

        if path in ('/', ''):
            self.serve_puzzle('200')
            return

        route = path.lstrip('/')

        if route.startswith('api/'):
            self.serve_api(route.replace('api/', '', 1))
            return

        if re.fullmatch(r'\d{3}', route):
            self.serve_puzzle(route)
            return

        if self.serve_static(route):
            return

        self.serve_puzzle('404')

    def serve_puzzle(self, status_key: str):
        http_code = http_status_for_code(status_key)
        html = self.load_html_file('puzzle.html')
        payload = json.dumps(status_payload(status_key), ensure_ascii=False)
        inject = f'<script>window.__INITIAL__={payload};</script>'
        html = html.replace('</head>', inject + '</head>', 1)

        self.send_response(http_code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

        print(f"✅ ステータス {http_code} ({description_for_code(status_key)}) を返送しました")

    def serve_api(self, requested_code: str):
        if not re.fullmatch(r'\d{3}', requested_code):
            self.send_response(404)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Not Found'}, ensure_ascii=False).encode('utf-8'))
            print("❌ API パスが見つかりません")
            return

        payload = status_payload(requested_code)
        http_code = payload['status']

        self.send_response(http_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8'))
        print(f"✅ API JSON {http_code} を返送しました")

    def serve_static(self, route: str) -> bool:
        file_path = (BASE_DIR / route).resolve()
        if not str(file_path).startswith(str(BASE_DIR.resolve())):
            return False
        if not file_path.is_file():
            return False

        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or 'application/octet-stream'

        self.send_response(200)
        self.send_header('Content-type', f'{content_type}; charset=utf-8')
        self.end_headers()
        self.wfile.write(file_path.read_bytes())
        print(f"✅ 静的ファイル {route} を返送しました")
        return True

    def load_html_file(self, filename: str) -> str:
        file_path = BASE_DIR / filename
        try:
            return file_path.read_text(encoding='utf-8')
        except FileNotFoundError:
            return f"<h1>エラー: {filename} が見つかりません</h1>"

    def log_message(self, format, *args):
        pass


def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, PoopStatusHandler)

    print("\n" + "=" * 60)
    print("🚽 うんちステータスコード学習サーバー")
    print("=" * 60)
    print("\n✨ サーバーが起動しました！")
    print(f"📍 URL: http://localhost:{port}")
    print("\n📝 例:")
    print(f"  http://localhost:{port}/")
    print(f"  http://localhost:{port}/303")
    print(f"  http://localhost:{port}/404")
    print(f"  http://localhost:{port}/418")
    print(f"  http://localhost:{port}/500")
    print("\nJSON API:")
    print(f"  curl http://localhost:{port}/api/303")
    print("\n⏹️  停止: Ctrl+C を押してください")
    print("=" * 60 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 サーバーを停止しています...")
        httpd.server_close()
        print("✅ サーバーが停止しました\n")


if __name__ == '__main__':
    run_server(8000)
